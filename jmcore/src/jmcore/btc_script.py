"""
Bitcoin script utilities for fidelity bonds.

Uses python-bitcointx for script operations where appropriate.
"""

from __future__ import annotations

import hashlib

from bitcointx.core.script import (
    OP_0,
    OP_CHECKLOCKTIMEVERIFY,
    OP_CHECKSIG,
    OP_DROP,
    CScript,
    CScriptOp,
)


def mk_freeze_script(pubkey_hex: str, locktime: int) -> bytes:
    """
    Create a timelocked script using OP_CHECKLOCKTIMEVERIFY.

    Script format: <locktime> OP_CHECKLOCKTIMEVERIFY OP_DROP <pubkey> OP_CHECKSIG

    Args:
        pubkey_hex: Compressed public key as hex string (33 bytes)
        locktime: Unix timestamp for the locktime

    Returns:
        Script as bytes
    """
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    if len(pubkey_bytes) != 33:
        raise ValueError(f"Invalid pubkey length: {len(pubkey_bytes)}, expected 33")

    # Use python-bitcointx to build the script
    script = CScript([locktime, OP_CHECKLOCKTIMEVERIFY, OP_DROP, pubkey_bytes, OP_CHECKSIG])
    return bytes(script)


def disassemble_script(script_bytes: bytes) -> str:
    """
    Disassemble a Bitcoin script into human-readable form.

    Uses python-bitcointx for proper parsing.

    Args:
        script_bytes: Script bytes

    Returns:
        Human-readable script representation
    """
    script = CScript(script_bytes)
    parts: list[str] = []

    for op in script:
        if isinstance(op, CScriptOp):
            parts.append(str(op))
        elif isinstance(op, bytes):
            # Data push - try to interpret as number if small
            if len(op) <= 5:
                try:
                    num = _decode_scriptnum(op)
                    parts.append(str(num))
                except (ValueError, IndexError):
                    parts.append(f"<{op.hex()}>")
            else:
                parts.append(f"<{op.hex()}>")
        elif isinstance(op, int):
            parts.append(str(op))
        else:
            parts.append(repr(op))

    return " ".join(parts)


def _decode_scriptnum(data: bytes) -> int:
    """
    Decode a script number from bytes.

    Args:
        data: Encoded script number bytes

    Returns:
        Decoded integer
    """
    if len(data) == 0:
        return 0

    # Little-endian with sign bit in MSB
    result = int.from_bytes(data, "little")
    if data[-1] & 0x80:
        # Negative number - clear sign bit and negate
        result = -(result & ~(0x80 << ((len(data) - 1) * 8)))

    return result


def redeem_script_to_p2wsh_script(redeem_script: bytes) -> bytes:
    """
    Convert a redeem script to P2WSH scriptPubKey.

    Args:
        redeem_script: The redeem script bytes

    Returns:
        P2WSH scriptPubKey (OP_0 <32-byte-hash>)
    """
    script_hash = hashlib.sha256(redeem_script).digest()
    script = CScript([OP_0, script_hash])
    return bytes(script)
