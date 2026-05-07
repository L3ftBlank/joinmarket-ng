"""Wire-format tests for :mod:`jmcore.attestation_wire`."""

from __future__ import annotations

import os

import pytest

from jmcore.attestation_wire import (
    AttestPayload,
    AttestReqPayload,
    AttestWireError,
    decode_attest,
    decode_attestreq,
    encode_attest,
    encode_attestreq,
)
from jmcore.clsag_attestation import RingMember


def _ring(n: int) -> list[RingMember]:
    return [RingMember(pubkey_xonly=os.urandom(32), outpoint=os.urandom(36)) for _ in range(n)]


# ---- attestreq ----


def test_attestreq_roundtrip() -> None:
    payload = AttestReqPayload(
        run_id=os.urandom(32),
        round_no=3,
        signer_idx=2,
        ring=_ring(8),
    )
    wire = encode_attestreq(payload)
    decoded = decode_attestreq(wire)
    assert decoded.run_id == payload.run_id
    assert decoded.round_no == payload.round_no
    assert decoded.signer_idx == payload.signer_idx
    assert len(decoded.ring) == 8
    for a, b in zip(decoded.ring, payload.ring, strict=True):
        assert a.pubkey_xonly == b.pubkey_xonly
        assert a.outpoint == b.outpoint


def test_attestreq_minimum_ring() -> None:
    payload = AttestReqPayload(run_id=os.urandom(32), round_no=0, signer_idx=0, ring=_ring(1))
    decoded = decode_attestreq(encode_attestreq(payload))
    assert len(decoded.ring) == 1


def test_attestreq_rejects_bad_run_id() -> None:
    payload = AttestReqPayload(run_id=b"\x00" * 31, round_no=0, signer_idx=0, ring=_ring(2))
    with pytest.raises(AttestWireError, match="run_id"):
        encode_attestreq(payload)


def test_attestreq_rejects_signer_idx_out_of_range() -> None:
    with pytest.raises(AttestWireError, match="signer_idx"):
        encode_attestreq(
            AttestReqPayload(run_id=os.urandom(32), round_no=0, signer_idx=5, ring=_ring(3))
        )


def test_attestreq_rejects_negative_round() -> None:
    with pytest.raises(AttestWireError, match="round_no"):
        encode_attestreq(
            AttestReqPayload(run_id=os.urandom(32), round_no=-1, signer_idx=0, ring=_ring(2))
        )


def test_attestreq_decode_too_few_tokens() -> None:
    with pytest.raises(AttestWireError, match=">=4 header tokens"):
        decode_attestreq("a b c")


def test_attestreq_decode_set_size_mismatch() -> None:
    payload = AttestReqPayload(run_id=os.urandom(32), round_no=0, signer_idx=0, ring=_ring(3))
    wire = encode_attestreq(payload).split()
    # tamper: claim 5 members but provide 3
    wire[3] = "5"
    with pytest.raises(AttestWireError, match="set_size says 5"):
        decode_attestreq(" ".join(wire))


def test_attestreq_decode_bad_member_token() -> None:
    payload = AttestReqPayload(run_id=os.urandom(32), round_no=0, signer_idx=0, ring=_ring(2))
    wire = encode_attestreq(payload).split()
    wire[-1] = "missing-colon-token"
    with pytest.raises(AttestWireError, match="missing ':' separator"):
        decode_attestreq(" ".join(wire))


def test_attestreq_decode_bad_field_width() -> None:
    payload = AttestReqPayload(run_id=os.urandom(32), round_no=0, signer_idx=0, ring=_ring(2))
    wire = encode_attestreq(payload).split()
    pk_hex, op_hex = wire[-1].split(":")
    wire[-1] = f"{pk_hex[:-2]}:{op_hex}"  # truncate pubkey
    with pytest.raises(AttestWireError, match="field widths"):
        decode_attestreq(" ".join(wire))


def test_attestreq_decode_non_hex_pubkey() -> None:
    payload = AttestReqPayload(run_id=os.urandom(32), round_no=0, signer_idx=0, ring=_ring(1))
    wire = encode_attestreq(payload).split()
    _, op = wire[-1].split(":")
    wire[-1] = "z" * 64 + ":" + op
    with pytest.raises(AttestWireError, match="non-hex"):
        decode_attestreq(" ".join(wire))


# ---- attest ----


def test_attest_roundtrip() -> None:
    sig = os.urandom(33 + 32 + 32 * 5)
    payload = AttestPayload(run_id=os.urandom(32), round_no=2, signature=sig)
    wire = encode_attest(payload)
    decoded = decode_attest(wire)
    assert decoded == payload


def test_attest_roundtrip_with_expected_set_size() -> None:
    n = 5
    sig = os.urandom(33 + 32 + 32 * n)
    payload = AttestPayload(run_id=os.urandom(32), round_no=0, signature=sig)
    decoded = decode_attest(encode_attest(payload), expected_set_size=n)
    assert decoded.signature == sig


def test_attest_rejects_wrong_set_size() -> None:
    sig = os.urandom(33 + 32 + 32 * 5)
    payload = AttestPayload(run_id=os.urandom(32), round_no=0, signature=sig)
    with pytest.raises(AttestWireError, match="signature length"):
        decode_attest(encode_attest(payload), expected_set_size=6)


def test_attest_rejects_empty_signature() -> None:
    with pytest.raises(AttestWireError, match="non-empty"):
        encode_attest(AttestPayload(run_id=os.urandom(32), round_no=0, signature=b""))


def test_attest_rejects_short_run_id_hex() -> None:
    with pytest.raises(AttestWireError, match="run_id hex"):
        decode_attest("00 0 deadbeef")


def test_attest_rejects_extra_tokens() -> None:
    with pytest.raises(AttestWireError, match="3 tokens"):
        decode_attest("00 0 deadbeef extra")
