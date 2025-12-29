"""
Bitcoin address generation utilities.

This module re-exports address utilities from jmcore.bitcoin
for backward compatibility.
"""

from __future__ import annotations

# Keep bech32_encode for legacy imports from maker/tx_verification.py
import bech32 as bech32_lib

# Legacy exports for backward compatibility with existing imports
# These were internal functions used by maker/tx_verification.py
# Re-export from jmcore.bitcoin for backward compatibility
from jmcore.bitcoin import (
    hash160,
    pubkey_to_p2wpkh_address,
    pubkey_to_p2wpkh_script,
    script_to_p2wsh_address,
    script_to_p2wsh_scriptpubkey,
)


def bech32_encode(hrp: str, data: list[int]) -> str:
    """
    Legacy wrapper for bech32 encoding.

    This function is kept for backward compatibility with
    maker/tx_verification.py which imports it.
    """
    # First element is witness version, rest is the witness program in 5-bit groups
    if data:
        witver = data[0]
        # Convert 5-bit groups back to 8-bit for bech32 lib
        # The bech32 lib's encode takes 8-bit data and converts internally
        # So we need to convert from 5-bit to 8-bit
        witprog_5bit = data[1:]
        # Convert 5-bit groups to bytes
        acc = 0
        bits = 0
        witprog = []
        for value in witprog_5bit:
            acc = (acc << 5) | value
            bits += 5
            while bits >= 8:
                bits -= 8
                witprog.append((acc >> bits) & 0xFF)
        result = bech32_lib.encode(hrp, witver, bytes(witprog))
        if result is None:
            raise ValueError("Failed to encode bech32")
        return result
    raise ValueError("Empty data")


def convertbits(data: bytes, frombits: int, tobits: int, pad: bool = True) -> list[int]:
    """
    Convert between bit groups.

    Legacy wrapper kept for backward compatibility.
    """
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1

    for value in data:
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)

    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        raise ValueError("Invalid bits")

    return ret


__all__ = [
    "bech32_encode",
    "convertbits",
    "hash160",
    "pubkey_to_p2wpkh_address",
    "pubkey_to_p2wpkh_script",
    "script_to_p2wsh_address",
    "script_to_p2wsh_scriptpubkey",
]
