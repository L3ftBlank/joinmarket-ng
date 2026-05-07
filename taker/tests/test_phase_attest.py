"""Tests for ``Taker._phase_attest_round`` and the ``run_id`` lifecycle."""

from __future__ import annotations

import base64
import os
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from coincurve import PrivateKey
from jmcore.attestation_wire import AttestPayload, encode_attest
from jmcore.config import TxExtensionConfig
from jmcore.models import Offer, OfferType

from taker.ring_assembly import RingAssembly
from taker.taker import Taker


class _IdCrypto:
    """Stand-in for ``CryptoSession`` that base64-round-trips its input."""

    def encrypt(self, plaintext: str) -> str:
        return base64.b64encode(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return base64.b64decode(ciphertext).decode()


def _bond_data(seed: int) -> dict[str, Any]:
    """Generate ``fidelity_bond_data`` shaped like ``directory_client``'s output.

    Each call yields a unique secp256k1 keypair + outpoint so collisions
    are impossible across decoy and selected pools.
    """
    pk = PrivateKey.from_int(0x1000 + seed)
    pub = pk.public_key.format(compressed=True).hex()
    txid = f"{seed:064x}"  # 32-byte txid hex
    return {
        "utxo_txid": txid,
        "utxo_vout": 0,
        "utxo_pub": pub,
        "locktime": 1_900_000_000,
    }


def _make_offer(nick: str, seed: int, with_bond: bool = True) -> Offer:
    return Offer(
        ordertype=OfferType.SW0_RELATIVE,
        oid=seed,
        minsize=10_000,
        maxsize=10_000_000,
        txfee=0,
        cjfee=0,
        counterparty=nick,
        fidelity_bond_data=_bond_data(seed) if with_bond else None,
    )


def _make_session(nick: str, seed: int, *, with_crypto: bool = True) -> SimpleNamespace:
    """Lightweight stand-in for ``MakerSession``.

    ``_phase_attest_round`` only reads ``offer``, ``crypto`` and
    ``comm_channel`` off each session, so a duck-typed namespace lets
    us substitute ``_IdCrypto`` without spinning up real NaCl
    keypairs in every test.
    """
    return SimpleNamespace(
        nick=nick,
        offer=_make_offer(nick, seed),
        crypto=_IdCrypto() if with_crypto else None,
        comm_channel="directory:test:5222" if with_crypto else "",
    )


def _signature_bytes(set_size: int) -> bytes:
    # Length must equal 33 (key image) + 32 (c_0) + 32 * N (s vector).
    return os.urandom(33 + 32 + 32 * set_size)


def _build_taker(
    *,
    sessions: dict[str, SimpleNamespace],
    decoy_pool: list[Offer],
    tx_ext: TxExtensionConfig,
    maker_timeout_sec: float = 5.0,
    directory_client: Any | None = None,
) -> Taker:
    taker = Taker.__new__(Taker)
    taker.maker_sessions = sessions
    taker.run_id = b""
    taker.config = Mock()
    taker.config.tx_extension = tx_ext
    taker.config.maker_timeout_sec = maker_timeout_sec
    taker.orderbook_manager = Mock()
    taker.orderbook_manager.offers = decoy_pool
    taker.directory_client = directory_client or AsyncMock()
    return taker


# ---------------------------------------------------------------------------
# _ensure_run_id
# ---------------------------------------------------------------------------


def test_ensure_run_id_idempotent() -> None:
    taker = _build_taker(
        sessions={},
        decoy_pool=[],
        tx_ext=TxExtensionConfig(),
    )
    a = taker._ensure_run_id()
    b = taker._ensure_run_id()
    assert a == b
    assert len(a) == 32


# ---------------------------------------------------------------------------
# _build_attest_participants
# ---------------------------------------------------------------------------


def test_build_attest_participants_drops_sessionless_nicks() -> None:
    sessions = {
        "m1": _make_session("m1", 1),
        "m2": _make_session("m2", 2, with_crypto=False),  # no crypto/channel
    }
    taker = _build_taker(
        sessions=sessions,
        decoy_pool=[],
        tx_ext=TxExtensionConfig(),
    )
    # Synthesize a ring assembly using just the selected makers; this
    # function isn't responsible for the ring, only the participant
    # mapping.
    from jmcore.clsag_attestation import RingMember

    ring = [RingMember(pubkey_xonly=os.urandom(32), outpoint=os.urandom(36)) for _ in range(2)]
    assembly = RingAssembly(ring=ring, signer_idx_by_nick={"m1": 0, "m2": 1})

    participants, dropped = taker._build_attest_participants(assembly)
    assert [p.nick for p in participants] == ["m1"]
    assert dropped == ["m2"]


# ---------------------------------------------------------------------------
# _phase_attest_round
# ---------------------------------------------------------------------------


def _decoy_pool(count: int, *, start_seed: int = 100) -> list[Offer]:
    return [_make_offer(f"dec{i}", start_seed + i) for i in range(count)]


@pytest.mark.asyncio
async def test_phase_attest_round_no_sessions_returns_none() -> None:
    taker = _build_taker(
        sessions={},
        decoy_pool=_decoy_pool(30),
        tx_ext=TxExtensionConfig(min_anonymity_set_size=5, target_anonymity_set_size=10),
    )
    assert await taker._phase_attest_round(0) is None


@pytest.mark.asyncio
async def test_phase_attest_round_aborts_when_orderbook_too_small() -> None:
    # Orderbook can supply 2 selected + 1 decoy = 3 members; min is 5.
    sessions = {f"m{i}": _make_session(f"m{i}", i) for i in range(2)}
    taker = _build_taker(
        sessions=sessions,
        decoy_pool=_decoy_pool(1, start_seed=50),
        tx_ext=TxExtensionConfig(min_anonymity_set_size=5, target_anonymity_set_size=10),
    )
    assert await taker._phase_attest_round(0) is None


@pytest.mark.asyncio
async def test_phase_attest_round_happy_path() -> None:
    # 2 selected makers, plenty of decoys.
    sessions = {f"m{i}": _make_session(f"m{i}", i + 1) for i in range(2)}
    decoys = _decoy_pool(8, start_seed=100)

    tx_ext = TxExtensionConfig(min_anonymity_set_size=5, target_anonymity_set_size=10)
    set_size = 10  # 2 selected + 8 decoys

    # Build canned !attest replies for each maker. We don't need real
    # CLSAG — the orchestrator only decodes the wire frame; the upper
    # layer would CLSAG-verify separately.
    run_id_holder: dict[str, bytes] = {}

    async def fake_send(*args: Any, **kwargs: Any) -> None:
        return None

    async def fake_wait(
        *,
        expected_nicks: list[str],
        expected_command: str,
        timeout: float,
    ) -> dict[str, dict[str, Any]]:
        # The phase mints the run_id lazily; capture it for the reply.
        rid = run_id_holder["run_id"]
        out: dict[str, dict[str, Any]] = {}
        for nick in expected_nicks:
            payload = AttestPayload(run_id=rid, round_no=1, signature=_signature_bytes(set_size))
            encrypted = base64.b64encode(encode_attest(payload).encode()).decode()
            out[nick] = {"data": f"{encrypted} signing_pk sigb64", "error": False}
        return out

    directory_client = AsyncMock()
    directory_client.send_privmsg.side_effect = fake_send
    directory_client.wait_for_responses.side_effect = fake_wait

    taker = _build_taker(
        sessions=sessions,
        decoy_pool=decoys,
        tx_ext=tx_ext,
        directory_client=directory_client,
    )
    # Mint run_id manually so the canned replies see the same value.
    run_id_holder["run_id"] = taker._ensure_run_id()

    out = await taker._phase_attest_round(1)
    assert out is not None
    round_result, ring_assembly = out
    assert ring_assembly.set_size == set_size
    assert set(round_result.decoded.keys()) == {"m0", "m1"}
    assert round_result.failed_makers == []
    # send_privmsg called once per selected maker.
    assert directory_client.send_privmsg.await_count == 2


@pytest.mark.asyncio
async def test_phase_attest_round_unaddressable_session_funnels_to_failed() -> None:
    sessions = {
        "m0": _make_session("m0", 1),
        "m1": _make_session("m1", 2, with_crypto=False),  # unaddressable
    }
    decoys = _decoy_pool(8, start_seed=100)
    set_size = 10

    run_id_holder: dict[str, bytes] = {}

    async def fake_wait(
        *,
        expected_nicks: list[str],
        expected_command: str,
        timeout: float,
    ) -> dict[str, dict[str, Any]]:
        rid = run_id_holder["run_id"]
        out: dict[str, dict[str, Any]] = {}
        for nick in expected_nicks:
            payload = AttestPayload(run_id=rid, round_no=0, signature=_signature_bytes(set_size))
            encrypted = base64.b64encode(encode_attest(payload).encode()).decode()
            out[nick] = {"data": f"{encrypted} pk sig", "error": False}
        return out

    directory_client = AsyncMock()
    directory_client.send_privmsg = AsyncMock(return_value=None)
    directory_client.wait_for_responses.side_effect = fake_wait

    taker = _build_taker(
        sessions=sessions,
        decoy_pool=decoys,
        tx_ext=TxExtensionConfig(min_anonymity_set_size=5, target_anonymity_set_size=10),
        directory_client=directory_client,
    )
    run_id_holder["run_id"] = taker._ensure_run_id()

    out = await taker._phase_attest_round(0)
    assert out is not None
    round_result, _ = out
    assert "m0" in round_result.decoded
    assert "m1" in round_result.failed_makers
    # Only m0 was actually addressed on the wire.
    assert directory_client.send_privmsg.await_count == 1


@pytest.mark.asyncio
async def test_phase_attest_round_no_addressable_participants() -> None:
    # Both sessions lack crypto/channel; the round shouldn't hit the network.
    sessions = {
        "m0": _make_session("m0", 1, with_crypto=False),
        "m1": _make_session("m1", 2, with_crypto=False),
    }
    decoys = _decoy_pool(8, start_seed=100)

    directory_client = AsyncMock()
    taker = _build_taker(
        sessions=sessions,
        decoy_pool=decoys,
        tx_ext=TxExtensionConfig(min_anonymity_set_size=5, target_anonymity_set_size=10),
        directory_client=directory_client,
    )

    out = await taker._phase_attest_round(0)
    assert out is not None
    round_result, _ = out
    assert round_result.decoded == {}
    assert sorted(round_result.failed_makers) == ["m0", "m1"]
    directory_client.send_privmsg.assert_not_awaited()
    directory_client.wait_for_responses.assert_not_awaited()


@pytest.mark.asyncio
async def test_phase_attest_round_resilient_small_orderbook() -> None:
    # Min=3, target=20, but orderbook only supplies 2 + 4 decoys = 6.
    # Assembler should shrink rather than abort.
    sessions = {f"m{i}": _make_session(f"m{i}", i + 1) for i in range(2)}
    decoys = _decoy_pool(4, start_seed=100)
    expected_set_size = 6

    run_id_holder: dict[str, bytes] = {}

    async def fake_wait(
        *,
        expected_nicks: list[str],
        expected_command: str,
        timeout: float,
    ) -> dict[str, dict[str, Any]]:
        rid = run_id_holder["run_id"]
        out: dict[str, dict[str, Any]] = {}
        for nick in expected_nicks:
            payload = AttestPayload(
                run_id=rid, round_no=0, signature=_signature_bytes(expected_set_size)
            )
            encrypted = base64.b64encode(encode_attest(payload).encode()).decode()
            out[nick] = {"data": f"{encrypted} pk sig", "error": False}
        return out

    directory_client = AsyncMock()
    directory_client.wait_for_responses.side_effect = fake_wait

    taker = _build_taker(
        sessions=sessions,
        decoy_pool=decoys,
        tx_ext=TxExtensionConfig(min_anonymity_set_size=3, target_anonymity_set_size=20),
        directory_client=directory_client,
    )
    run_id_holder["run_id"] = taker._ensure_run_id()

    out = await taker._phase_attest_round(0)
    assert out is not None
    round_result, ring_assembly = out
    assert ring_assembly.set_size == expected_set_size
    assert sorted(round_result.decoded) == ["m0", "m1"]


# ---------------------------------------------------------------------------
# _phase_attest (Attestation assembly)
# ---------------------------------------------------------------------------


def _make_replier(
    *,
    run_id_holder: dict[str, bytes],
    set_size: int,
    round_no: int,
    error_for: set[str] | None = None,
    drop: set[str] | None = None,
) -> Any:
    """Build a wait_for_responses side-effect that returns canned !attest replies.

    ``error_for`` nicks return ``error=True`` (modeling a maker !error
    reply); ``drop`` nicks are simply absent from the returned dict
    (modeling a timeout).
    """

    error_for = error_for or set()
    drop = drop or set()

    async def fake_wait(
        *,
        expected_nicks: list[str],
        expected_command: str,
        timeout: float,
    ) -> dict[str, dict[str, Any]]:
        rid = run_id_holder["run_id"]
        out: dict[str, dict[str, Any]] = {}
        for nick in expected_nicks:
            if nick in drop:
                continue
            if nick in error_for:
                out[nick] = {"data": "rejected", "error": True}
                continue
            payload = AttestPayload(
                run_id=rid, round_no=round_no, signature=_signature_bytes(set_size)
            )
            encrypted = base64.b64encode(encode_attest(payload).encode()).decode()
            out[nick] = {"data": f"{encrypted} pk sig", "error": False}
        return out

    return fake_wait


@pytest.mark.asyncio
async def test_phase_attest_happy_path_assembles_blob() -> None:
    sessions = {f"m{i}": _make_session(f"m{i}", i + 1) for i in range(4)}
    decoys = _decoy_pool(8, start_seed=100)
    set_size = 12  # 4 selected + 8 decoys

    tx_ext = TxExtensionConfig(
        min_anonymity_set_size=5,
        target_anonymity_set_size=12,
        attestation_threshold_K=3,
    )
    directory_client = AsyncMock()
    rid_holder: dict[str, bytes] = {}
    directory_client.wait_for_responses.side_effect = _make_replier(
        run_id_holder=rid_holder, set_size=set_size, round_no=1
    )

    taker = _build_taker(
        sessions=sessions, decoy_pool=decoys, tx_ext=tx_ext, directory_client=directory_client
    )
    rid_holder["run_id"] = taker._ensure_run_id()

    attestation = await taker._phase_attest(1)
    assert attestation is not None
    assert attestation.set_size == set_size
    assert attestation.k == 3
    # All 4 makers stayed in the session — none failed.
    assert set(taker.maker_sessions.keys()) == {"m0", "m1", "m2", "m3"}


@pytest.mark.asyncio
async def test_phase_attest_drops_failed_makers_from_sessions() -> None:
    sessions = {f"m{i}": _make_session(f"m{i}", i + 1) for i in range(5)}
    decoys = _decoy_pool(8, start_seed=100)
    set_size = 13  # 5 selected + 8 decoys

    tx_ext = TxExtensionConfig(
        min_anonymity_set_size=5,
        target_anonymity_set_size=13,
        attestation_threshold_K=3,
    )
    directory_client = AsyncMock()
    rid_holder: dict[str, bytes] = {}
    # m1 times out, m3 returns an !error reply.
    directory_client.wait_for_responses.side_effect = _make_replier(
        run_id_holder=rid_holder,
        set_size=set_size,
        round_no=2,
        drop={"m1"},
        error_for={"m3"},
    )

    taker = _build_taker(
        sessions=sessions, decoy_pool=decoys, tx_ext=tx_ext, directory_client=directory_client
    )
    rid_holder["run_id"] = taker._ensure_run_id()

    attestation = await taker._phase_attest(2)
    assert attestation is not None
    assert attestation.k == 3
    # m1 / m3 dropped from the live set; survivors stay.
    assert set(taker.maker_sessions.keys()) == {"m0", "m2", "m4"}


@pytest.mark.asyncio
async def test_phase_attest_aborts_when_below_threshold() -> None:
    sessions = {f"m{i}": _make_session(f"m{i}", i + 1) for i in range(3)}
    decoys = _decoy_pool(8, start_seed=100)
    set_size = 11

    tx_ext = TxExtensionConfig(
        min_anonymity_set_size=5,
        target_anonymity_set_size=11,
        attestation_threshold_K=3,
    )
    directory_client = AsyncMock()
    rid_holder: dict[str, bytes] = {}
    # Only 2 of 3 makers reply — below K=3.
    directory_client.wait_for_responses.side_effect = _make_replier(
        run_id_holder=rid_holder, set_size=set_size, round_no=1, drop={"m2"}
    )

    taker = _build_taker(
        sessions=sessions, decoy_pool=decoys, tx_ext=tx_ext, directory_client=directory_client
    )
    rid_holder["run_id"] = taker._ensure_run_id()

    attestation = await taker._phase_attest(1)
    assert attestation is None
    # m2 still got dropped from the live set (it failed to attest).
    assert "m2" not in taker.maker_sessions


@pytest.mark.asyncio
async def test_phase_attest_aborts_when_ring_assembly_fails() -> None:
    # Min=10 but only 2 selected + 1 decoy = 3 members -> assembly fails.
    sessions = {f"m{i}": _make_session(f"m{i}", i + 1) for i in range(2)}
    decoys = _decoy_pool(1, start_seed=100)

    tx_ext = TxExtensionConfig(
        min_anonymity_set_size=10,
        target_anonymity_set_size=20,
        attestation_threshold_K=2,
    )
    taker = _build_taker(
        sessions=sessions,
        decoy_pool=decoys,
        tx_ext=tx_ext,
        directory_client=AsyncMock(),
    )
    assert await taker._phase_attest(1) is None
    # Round-0 sessions remain untouched when we never even sent
    # !attestreq — the freeze fallback uses them.
    assert set(taker.maker_sessions.keys()) == {"m0", "m1"}


@pytest.mark.asyncio
async def test_phase_attest_picks_signatures_by_signer_index() -> None:
    """K signatures are chosen deterministically by signer index, not arrival order."""
    sessions = {f"m{i}": _make_session(f"m{i}", i + 1) for i in range(5)}
    decoys = _decoy_pool(7, start_seed=100)
    set_size = 12

    tx_ext = TxExtensionConfig(
        min_anonymity_set_size=5,
        target_anonymity_set_size=12,
        attestation_threshold_K=2,
    )
    directory_client = AsyncMock()
    rid_holder: dict[str, bytes] = {}
    directory_client.wait_for_responses.side_effect = _make_replier(
        run_id_holder=rid_holder, set_size=set_size, round_no=1
    )

    taker = _build_taker(
        sessions=sessions, decoy_pool=decoys, tx_ext=tx_ext, directory_client=directory_client
    )
    rid_holder["run_id"] = taker._ensure_run_id()

    # Run the round once to learn the signer-index assignment, then
    # confirm _phase_attest picks the K lowest-indexed signers.
    out_round = await taker._phase_attest_round(1)
    assert out_round is not None
    _, assembly = out_round

    # Re-mint a fresh state for the actual _phase_attest call (since
    # the round above already consumed the wait_for_responses call).
    taker2 = _build_taker(
        sessions={f"m{i}": _make_session(f"m{i}", i + 1) for i in range(5)},
        decoy_pool=decoys,
        tx_ext=tx_ext,
        directory_client=directory_client,
    )
    rid_holder["run_id"] = taker2._ensure_run_id()

    attestation = await taker2._phase_attest(1)
    assert attestation is not None
    # Two signatures, ordered as the K lowest signer indices.
    assert attestation.k == 2
    # Exact ordering of nicks-by-signer-index isn't fixed (depends on
    # the ring shuffle), but the chosen set must be a subset of all
    # selected makers and the blob must round-trip.
    assert all(len(s) == 33 + 32 + 32 * set_size for s in attestation.ring_signatures)
