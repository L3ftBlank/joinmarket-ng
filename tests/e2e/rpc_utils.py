"""
Helpers for interacting with local Bitcoin Core regtest node.
"""

from __future__ import annotations

import math
import os
from typing import Any

import httpx
from loguru import logger

BITCOIN_RPC_URL = os.getenv("BITCOIN_RPC_URL", "http://127.0.0.1:18443")
BITCOIN_RPC_USER = os.getenv("BITCOIN_RPC_USER", "test")
BITCOIN_RPC_PASSWORD = os.getenv("BITCOIN_RPC_PASSWORD", "test")


class BitcoinRPCError(Exception):
    pass


async def rpc_call(
    method: str, params: list[Any] | None = None, wallet: str | None = None
) -> Any:
    url = BITCOIN_RPC_URL.rstrip("/")
    if wallet:
        url = f"{url}/wallet/{wallet}"

    payload = {
        "jsonrpc": "1.0",
        "id": "jm-tests",
        "method": method,
        "params": params or [],
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url, auth=(BITCOIN_RPC_USER, BITCOIN_RPC_PASSWORD), json=payload
        )

    data = response.json()
    if data.get("error"):
        raise BitcoinRPCError(data["error"])
    return data.get("result")


async def mine_blocks(blocks: int, address: str) -> None:
    """
    Mine blocks to a specific address.

    We avoid using wallet RPC completely - the wallet is external to Bitcoin Core.
    """
    await rpc_call("generatetoaddress", [blocks, address])
    logger.info(f"Mined {blocks} blocks to {address}")


async def ensure_wallet_funded(
    target_address: str, amount_btc: float = 1.0, confirmations: int = 1
) -> bool:
    """
    Fund a wallet address by mining blocks directly to it.

    We avoid wallet RPC completely - Bitcoin Core is just a source of truth,
    not for managing funds. The wallet is completely external.

    The block subsidy is NOT assumed to be 50 BTC: these tests share a
    long-running regtest chain whose subsidy halves every 150 blocks, so a
    fixed 110-block mine can deliver far less than ``amount_btc`` and starve
    downstream operations (under-funded takers fail CoinJoins or time out).
    Instead we read the current subsidy and mine enough mature coinbases
    (depth >= 100) to cover ``amount_btc`` plus a fee buffer.

    Args:
        target_address: Address to fund
        amount_btc: Minimum spendable amount the address should end up with
        confirmations: Extra confirmations to mine on top of maturity

    Returns:
        True if successful, False otherwise
    """
    try:
        info = await rpc_call("getblockchaininfo")
        height = int(info["blocks"])
        # Authoritative current subsidy (sats) from the chain, so we never
        # hardcode the halving schedule.
        stats = await rpc_call("getblockstats", [height, ["subsidy"]])
        subsidy_btc = float(stats["subsidy"]) / 1e8

        # Fee buffer covers the spends that follow funding (sendmany batches,
        # CoinJoin inputs). Generous on regtest where it costs nothing.
        target_btc = amount_btc + 0.5

        if subsidy_btc <= 0:
            logger.error(
                f"Block subsidy is zero at height {height}; cannot fund via "
                "coinbase on this exhausted regtest chain. Recreate the chain "
                "with `docker compose down -v`."
            )
            return False

        # Coinbase needs 100 confirmations to mature, so to end up with
        # ``needed_mature`` mature coinbases we mine that many plus 100.
        needed_mature = max(1, math.ceil(target_btc / subsidy_btc))
        blocks_to_mine = needed_mature + 100 + confirmations

        logger.info(
            f"Funding {target_address}: subsidy={subsidy_btc:.8f} BTC at "
            f"height {height}, mining {blocks_to_mine} blocks "
            f"(~{needed_mature * subsidy_btc:.4f} BTC mature) for >= {target_btc} BTC"
        )
        await rpc_call("generatetoaddress", [blocks_to_mine, target_address])
        return True
    except BitcoinRPCError as exc:
        logger.error(f"Failed to auto-fund wallet: {exc}")
        return False
    except Exception as exc:
        logger.error(f"Unexpected error during auto-funding: {exc}")
        return False
