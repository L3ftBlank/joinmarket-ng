"""Tests for Tor stream isolation via SOCKS5 authentication."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from jmcore.tor_isolation import (
    _PROCESS_TOKEN,
    IsolationCategory,
    IsolationCredentials,
    build_isolated_proxy_url,
    get_isolation_credentials,
)


class TestIsolationCategory:
    """Tests for the IsolationCategory enum."""

    def test_all_categories_are_strings(self) -> None:
        for cat in IsolationCategory:
            assert isinstance(cat.value, str)

    def test_all_categories_have_jm_prefix(self) -> None:
        for cat in IsolationCategory:
            assert cat.value.startswith("jm-"), f"{cat.name} missing 'jm-' prefix"

    def test_expected_members(self) -> None:
        names = {cat.name for cat in IsolationCategory}
        assert names == {
            "DIRECTORY",
            "PEER",
            "MEMPOOL",
            "NOTIFICATION",
            "UPDATE_CHECK",
            "HEALTH_CHECK",
        }

    def test_values_are_unique(self) -> None:
        values = [cat.value for cat in IsolationCategory]
        assert len(values) == len(set(values)), "Duplicate category values found"

    def test_string_equality(self) -> None:
        """IsolationCategory values compare equal to their string values."""
        assert IsolationCategory.DIRECTORY == "jm-directory"
        assert IsolationCategory.PEER.value == "jm-peer"


class TestProcessToken:
    """Tests for the per-process random token."""

    def test_token_is_hex_string(self) -> None:
        assert isinstance(_PROCESS_TOKEN, str)
        int(_PROCESS_TOKEN, 16)  # raises ValueError if not valid hex

    def test_token_length(self) -> None:
        # 16 bytes -> 32 hex chars
        assert len(_PROCESS_TOKEN) == 32


class TestIsolationCredentials:
    """Tests for the IsolationCredentials dataclass."""

    def test_creation(self) -> None:
        creds = IsolationCredentials(username="user", password="pass")
        assert creds.username == "user"
        assert creds.password == "pass"

    def test_frozen(self) -> None:
        creds = IsolationCredentials(username="user", password="pass")
        with pytest.raises(AttributeError):
            creds.username = "other"  # type: ignore[misc]

    def test_equality(self) -> None:
        a = IsolationCredentials(username="u", password="p")
        b = IsolationCredentials(username="u", password="p")
        assert a == b

    def test_inequality(self) -> None:
        a = IsolationCredentials(username="u1", password="p")
        b = IsolationCredentials(username="u2", password="p")
        assert a != b


class TestGetIsolationCredentials:
    """Tests for get_isolation_credentials()."""

    def test_username_is_category_value(self) -> None:
        for cat in IsolationCategory:
            creds = get_isolation_credentials(cat)
            assert creds.username == cat.value

    def test_password_is_process_token(self) -> None:
        creds = get_isolation_credentials(IsolationCategory.DIRECTORY)
        assert creds.password == _PROCESS_TOKEN

    def test_same_category_same_credentials(self) -> None:
        """Same category should yield identical credentials (same circuit)."""
        a = get_isolation_credentials(IsolationCategory.PEER)
        b = get_isolation_credentials(IsolationCategory.PEER)
        assert a == b

    def test_different_categories_different_usernames(self) -> None:
        """Different categories must have different usernames (different circuits)."""
        dir_creds = get_isolation_credentials(IsolationCategory.DIRECTORY)
        peer_creds = get_isolation_credentials(IsolationCategory.PEER)
        assert dir_creds.username != peer_creds.username

    def test_different_categories_same_password(self) -> None:
        """All categories in the same process share the same password."""
        passwords = {get_isolation_credentials(cat).password for cat in IsolationCategory}
        assert len(passwords) == 1


class TestBuildIsolatedProxyUrl:
    """Tests for build_isolated_proxy_url()."""

    def test_socks5h_by_default(self) -> None:
        url = build_isolated_proxy_url("127.0.0.1", 9050, IsolationCategory.DIRECTORY)
        assert url.startswith("socks5h://")

    def test_socks5_when_dns_local(self) -> None:
        url = build_isolated_proxy_url(
            "127.0.0.1",
            9050,
            IsolationCategory.MEMPOOL,
            resolve_dns_remotely=False,
        )
        assert url.startswith("socks5://")

    def test_host_and_port_in_url(self) -> None:
        url = build_isolated_proxy_url("127.0.0.1", 9050, IsolationCategory.PEER)
        assert "@127.0.0.1:9050" in url

    def test_credentials_embedded(self) -> None:
        url = build_isolated_proxy_url("127.0.0.1", 9050, IsolationCategory.NOTIFICATION)
        assert "jm-notification:" in url
        assert _PROCESS_TOKEN in url

    def test_full_url_format(self) -> None:
        url = build_isolated_proxy_url("127.0.0.1", 9050, IsolationCategory.UPDATE_CHECK)
        expected = f"socks5h://jm-update-check:{_PROCESS_TOKEN}@127.0.0.1:9050"
        assert url == expected

    def test_different_port(self) -> None:
        url = build_isolated_proxy_url("localhost", 9150, IsolationCategory.HEALTH_CHECK)
        assert "@localhost:9150" in url

    def test_different_categories_produce_different_urls(self) -> None:
        url_dir = build_isolated_proxy_url("127.0.0.1", 9050, IsolationCategory.DIRECTORY)
        url_peer = build_isolated_proxy_url("127.0.0.1", 9050, IsolationCategory.PEER)
        assert url_dir != url_peer

    def test_special_chars_are_percent_encoded(self) -> None:
        """Verify that username/password with special chars are encoded."""
        # The current implementation uses category values like "jm-directory"
        # which contain a hyphen (safe in URLs). Test via mocking a token with
        # special characters.
        with patch("jmcore.tor_isolation._PROCESS_TOKEN", "pass/word&foo=bar"):
            url = build_isolated_proxy_url("127.0.0.1", 9050, IsolationCategory.DIRECTORY)
            # The special chars should be percent-encoded
            assert "pass/word" not in url
            assert "pass%2Fword%26foo%3Dbar" in url
