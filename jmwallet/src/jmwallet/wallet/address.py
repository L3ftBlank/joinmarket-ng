"""
Bitcoin address utilities.

Re-exports address helpers from ``jmcore.bitcoin``.
"""

from __future__ import annotations

# Re-export from jmcore.bitcoin
from jmcore.bitcoin import (
    hash160,
    pubkey_to_p2wpkh_address,
    pubkey_to_p2wpkh_script,
    script_to_p2wsh_address,
    script_to_p2wsh_scriptpubkey,
)

__all__ = [
    "hash160",
    "pubkey_to_p2wpkh_address",
    "pubkey_to_p2wpkh_script",
    "script_to_p2wsh_address",
    "script_to_p2wsh_scriptpubkey",
]
