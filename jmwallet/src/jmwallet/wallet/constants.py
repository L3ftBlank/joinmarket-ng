"""
Wallet constants shared across wallet modules.
"""

from __future__ import annotations

# Re-export the descriptor-range limit from the backend module, which is the
# canonical definition (kept there so the backend has no dependency on the
# wallet package, avoiding an import cycle). See its docstring for the rationale.
from jmwallet.backends.descriptor_wallet import MAX_DESCRIPTOR_RANGE

# Fidelity bond constants
FIDELITY_BOND_BRANCH = 2  # Internal branch for fidelity bonds

# Default range for descriptor scans (Bitcoin Core default is 1000)
DEFAULT_SCAN_RANGE = 1000

__all__ = ["DEFAULT_SCAN_RANGE", "FIDELITY_BOND_BRANCH", "MAX_DESCRIPTOR_RANGE"]
