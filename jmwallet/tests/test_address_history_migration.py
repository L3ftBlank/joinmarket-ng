"""Tests for migrating the legacy address_history_<fingerprint>.jsonl file
into the unified wallet_metadata.jsonl store on WalletService startup."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from jmwallet.wallet.service import WalletService


def _make_service(tmp_path: Path, mnemonic: str) -> WalletService:
    backend = MagicMock()
    backend.connect = AsyncMock()
    backend._descriptors_imported = True
    return WalletService(
        mnemonic=mnemonic,
        backend=backend,
        network="mainnet",
        mixdepth_count=2,
        data_dir=tmp_path,
    )


def _legacy_path(tmp_path: Path, fingerprint: str) -> Path:
    return tmp_path / f"address_history_{fingerprint.lower()}.jsonl"


@pytest.fixture
def mnemonic() -> str:
    # Standard BIP-39 test vector
    return (
        "abandon abandon abandon abandon abandon abandon "
        "abandon abandon abandon abandon abandon about"
    )


def test_migration_ingests_and_removes_legacy_file(tmp_path: Path, mnemonic: str) -> None:
    # Bootstrap once to discover the fingerprint, then plant a legacy file.
    svc = _make_service(tmp_path, mnemonic)
    fp = svc.wallet_fingerprint
    legacy = _legacy_path(tmp_path, fp)
    legacy.write_text(
        "# legacy header\n" + json.dumps("bcrt1qold1") + "\n" + json.dumps("bcrt1qold2") + "\n",
        encoding="utf-8",
    )

    # Re-instantiate to trigger migration on __init__.
    svc2 = _make_service(tmp_path, mnemonic)
    assert svc2.addresses_with_history == {"bcrt1qold1", "bcrt1qold2"}
    assert not legacy.exists(), "Legacy file should be unlinked after migration"
    # Stored as BIP-329 addr records with jm:used:legacy origin.
    assert svc2.metadata_store is not None
    rec = svc2.metadata_store.address_records["bcrt1qold1"]
    assert "legacy" in rec.origins


def test_migration_idempotent_when_legacy_missing(tmp_path: Path, mnemonic: str) -> None:
    svc = _make_service(tmp_path, mnemonic)
    assert svc.addresses_with_history == set()
    legacy = _legacy_path(tmp_path, svc.wallet_fingerprint)
    assert not legacy.exists()


def test_migration_skips_malformed_lines(tmp_path: Path, mnemonic: str) -> None:
    svc = _make_service(tmp_path, mnemonic)
    fp = svc.wallet_fingerprint
    legacy = _legacy_path(tmp_path, fp)
    legacy.write_text(
        "not-json-at-all\n"
        + json.dumps("bcrt1qgood")
        + "\n"
        + json.dumps(123)
        + "\n",  # non-string entry must be ignored
        encoding="utf-8",
    )
    svc2 = _make_service(tmp_path, mnemonic)
    assert svc2.addresses_with_history == {"bcrt1qgood"}
    assert not legacy.exists()
