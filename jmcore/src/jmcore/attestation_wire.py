"""Wire codecs for JMP-0006 ``!attestreq`` and ``!attest`` PRIVMSG bodies.

The IRC transport carries these as the encrypted plaintext field of a
private message; size is bounded by the directory client's chunking
rather than IRC's 512-byte line limit. We keep the format
human-debuggable (whitespace-separated hex tokens) at the cost of a
~2x size hit over a packed binary form, because every wire bug we've
hit historically has been worth the cost of being able to ``cat`` an
IRC log and read it.

Format
======

``!attestreq`` plaintext::

    <run_id_hex:64> <round_no:int> <signer_idx:int> <set_size:N> \
    <pk_hex:64>:<outpoint_hex:72> ... <pk_hex:64>:<outpoint_hex:72>

The token count is ``4 + N``; the parser validates that exact arity
so a truncated payload doesn't silently produce a partial ring.

``!attest`` plaintext::

    <run_id_hex:64> <round_no:int> <signature_hex>

The signature is the raw CLSAG output: ``33 + 32 + 32*N`` bytes,
hex-encoded. The set size is implicit from the pre-shared ring; we
re-derive it from the signature length and check it against what the
caller expects.

Why hex and not base64
======================

Two reasons: (1) the values themselves are mostly already 32-byte
fixed-width quantities for which hex is the universal
representation, so callers don't end up with mixed encodings; (2)
whitespace as a separator means we can keep the parser to a single
``str.split`` instead of dragging in a length-prefixed binary
framing. The size overhead (33% over base64) is irrelevant compared
to the transport's chunking budget.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from jmcore.clsag_attestation import (
    MAX_K,  # noqa: F401 - re-exported for callers that want to validate K bounds
    MAX_SET_SIZE,
    MIN_SET_SIZE,
    RUN_ID_LEN,
    RingMember,
    _ring_sig_size,  # type: ignore[attr-defined]
)

_PUBKEY_HEX_LEN: Final[int] = 64  # 32 bytes
_OUTPOINT_HEX_LEN: Final[int] = 72  # 36 bytes
_RUN_ID_HEX_LEN: Final[int] = RUN_ID_LEN * 2


@dataclass(frozen=True)
class AttestReqPayload:
    """Decoded ``!attestreq`` body."""

    run_id: bytes
    round_no: int
    signer_idx: int
    ring: list[RingMember]


@dataclass(frozen=True)
class AttestPayload:
    """Decoded ``!attest`` body."""

    run_id: bytes
    round_no: int
    signature: bytes


class AttestWireError(ValueError):
    """Wire-format-level decoding failure.

    We use a dedicated subclass (rather than plain ``ValueError``) so
    the protocol handler can distinguish "peer sent a malformed
    message" from "our caller passed bad arguments". Messages are
    short and stable so they can be logged verbatim without leaking
    secrets.
    """


def encode_attestreq(payload: AttestReqPayload) -> str:
    """Render an :class:`AttestReqPayload` to its wire string."""
    if len(payload.run_id) != RUN_ID_LEN:
        raise AttestWireError(f"run_id must be {RUN_ID_LEN} bytes, got {len(payload.run_id)}")
    n = len(payload.ring)
    if not MIN_SET_SIZE <= n <= MAX_SET_SIZE:
        raise AttestWireError(f"set_size {n} outside [{MIN_SET_SIZE}, {MAX_SET_SIZE}]")
    if not 0 <= payload.signer_idx < n:
        raise AttestWireError(f"signer_idx {payload.signer_idx} not in [0, {n})")
    if payload.round_no < 0:
        raise AttestWireError(f"round_no must be >= 0, got {payload.round_no}")
    for i, m in enumerate(payload.ring):
        if len(m.pubkey_xonly) != 32:
            raise AttestWireError(f"ring[{i}].pubkey_xonly must be 32 bytes")
        if len(m.outpoint) != 36:
            raise AttestWireError(f"ring[{i}].outpoint must be 36 bytes")

    parts: list[str] = [
        payload.run_id.hex(),
        str(payload.round_no),
        str(payload.signer_idx),
        str(n),
    ]
    parts.extend(f"{m.pubkey_xonly.hex()}:{m.outpoint.hex()}" for m in payload.ring)
    return " ".join(parts)


def decode_attestreq(wire: str) -> AttestReqPayload:
    """Parse a wire string produced by :func:`encode_attestreq`.

    Raises :class:`AttestWireError` on any structural mismatch. The
    parser is strict on token count and field widths because the
    handler is downstream of an authenticated channel: a malformed
    payload from an authenticated peer is a protocol bug worth
    surfacing, not something to repair quietly.
    """
    tokens = wire.split()
    if len(tokens) < 4:
        raise AttestWireError(f"!attestreq needs >=4 header tokens, got {len(tokens)}")
    run_id_hex, round_str, idx_str, n_str, *member_tokens = tokens

    if len(run_id_hex) != _RUN_ID_HEX_LEN:
        raise AttestWireError(f"run_id hex must be {_RUN_ID_HEX_LEN} chars, got {len(run_id_hex)}")
    try:
        run_id = bytes.fromhex(run_id_hex)
    except ValueError as exc:
        raise AttestWireError(f"run_id not hex: {exc}") from exc

    try:
        round_no = int(round_str)
        signer_idx = int(idx_str)
        n = int(n_str)
    except ValueError as exc:
        raise AttestWireError(f"non-integer header field: {exc}") from exc

    if not MIN_SET_SIZE <= n <= MAX_SET_SIZE:
        raise AttestWireError(f"set_size {n} outside [{MIN_SET_SIZE}, {MAX_SET_SIZE}]")
    if len(member_tokens) != n:
        raise AttestWireError(f"set_size says {n} members, payload has {len(member_tokens)}")
    if not 0 <= signer_idx < n:
        raise AttestWireError(f"signer_idx {signer_idx} not in [0, {n})")
    if round_no < 0:
        raise AttestWireError(f"round_no must be >= 0, got {round_no}")

    ring: list[RingMember] = []
    for i, tok in enumerate(member_tokens):
        if tok.count(":") != 1:
            raise AttestWireError(f"ring[{i}] missing ':' separator")
        pk_hex, op_hex = tok.split(":", 1)
        if len(pk_hex) != _PUBKEY_HEX_LEN or len(op_hex) != _OUTPOINT_HEX_LEN:
            raise AttestWireError(f"ring[{i}] field widths: pk={len(pk_hex)} op={len(op_hex)}")
        try:
            pk = bytes.fromhex(pk_hex)
            op = bytes.fromhex(op_hex)
        except ValueError as exc:
            raise AttestWireError(f"ring[{i}] non-hex: {exc}") from exc
        ring.append(RingMember(pubkey_xonly=pk, outpoint=op))

    return AttestReqPayload(run_id=run_id, round_no=round_no, signer_idx=signer_idx, ring=ring)


def encode_attest(payload: AttestPayload) -> str:
    if len(payload.run_id) != RUN_ID_LEN:
        raise AttestWireError(f"run_id must be {RUN_ID_LEN} bytes, got {len(payload.run_id)}")
    if payload.round_no < 0:
        raise AttestWireError(f"round_no must be >= 0, got {payload.round_no}")
    if not payload.signature:
        raise AttestWireError("signature must be non-empty")
    return f"{payload.run_id.hex()} {payload.round_no} {payload.signature.hex()}"


def decode_attest(wire: str, *, expected_set_size: int | None = None) -> AttestPayload:
    """Parse an ``!attest`` wire string.

    ``expected_set_size`` lets the caller cross-check the signature
    length against the ring it sent. We don't make it mandatory
    because some callers (e.g. raw replay tools) don't know N at
    parse time; the cryptographic verifier will catch any mismatch
    anyway, but eager checking gives a cleaner error.
    """
    tokens = wire.split()
    if len(tokens) != 3:
        raise AttestWireError(f"!attest needs 3 tokens, got {len(tokens)}")
    run_id_hex, round_str, sig_hex = tokens

    if len(run_id_hex) != _RUN_ID_HEX_LEN:
        raise AttestWireError(f"run_id hex must be {_RUN_ID_HEX_LEN} chars, got {len(run_id_hex)}")
    try:
        run_id = bytes.fromhex(run_id_hex)
        round_no = int(round_str)
        signature = bytes.fromhex(sig_hex)
    except ValueError as exc:
        raise AttestWireError(f"non-hex/non-int field: {exc}") from exc

    if round_no < 0:
        raise AttestWireError(f"round_no must be >= 0, got {round_no}")

    if expected_set_size is not None:
        expected = _ring_sig_size(expected_set_size)
        if len(signature) != expected:
            raise AttestWireError(
                f"signature length {len(signature)} != expected {expected} for N={expected_set_size}"
            )

    return AttestPayload(run_id=run_id, round_no=round_no, signature=signature)


__all__ = [
    "AttestPayload",
    "AttestReqPayload",
    "AttestWireError",
    "decode_attest",
    "decode_attestreq",
    "encode_attest",
    "encode_attestreq",
]
