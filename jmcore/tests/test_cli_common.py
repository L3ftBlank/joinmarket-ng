"""
Tests for the CLI common module.
"""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import pytest
from loguru import logger

from jmcore.cli_common import setup_cli, setup_logging
from jmcore.settings import reset_settings


@pytest.fixture(autouse=True)
def reset_settings_fixture() -> Generator[None, None, None]:
    """Reset settings before and after each test."""
    reset_settings()
    yield
    reset_settings()


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_sets_level(self) -> None:
        """Test that setup_logging configures the log level."""
        setup_logging("DEBUG")
        # Verify handler is configured (loguru doesn't expose level directly,
        # but we can check that the handler was added)
        handlers = logger._core.handlers
        assert len(handlers) > 0

    def test_setup_logging_case_insensitive(self) -> None:
        """Test that log level is case-insensitive."""
        # Should not raise
        setup_logging("trace")
        setup_logging("TRACE")
        setup_logging("Trace")


class TestSetupCli:
    """Tests for setup_cli function."""

    def test_setup_cli_returns_settings(self) -> None:
        """Test that setup_cli returns JoinMarketSettings."""
        from jmcore.settings import JoinMarketSettings

        settings = setup_cli()
        assert isinstance(settings, JoinMarketSettings)

    def test_setup_cli_cli_arg_overrides_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that CLI log level argument overrides settings."""
        # Set log level in env (settings)
        monkeypatch.setenv("LOGGING__LEVEL", "DEBUG")

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            setup_cli(log_level="TRACE")

            # Should use CLI value, not settings
            mock_add.assert_called_once()
            call_kwargs = mock_add.call_args[1]
            assert call_kwargs["level"] == "TRACE"

    def test_setup_cli_uses_settings_when_no_cli_arg(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that setup_cli uses settings.logging.level when no CLI arg."""
        # Set log level in env (settings)
        monkeypatch.setenv("LOGGING__LEVEL", "TRACE")

        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            setup_cli(log_level=None)

            # Should use settings value
            mock_add.assert_called_once()
            call_kwargs = mock_add.call_args[1]
            assert call_kwargs["level"] == "TRACE"

    def test_setup_cli_defaults_to_info(self) -> None:
        """Test that setup_cli defaults to INFO when no CLI arg and no settings."""
        with patch.object(logger, "remove"), patch.object(logger, "add") as mock_add:
            setup_cli(log_level=None)

            mock_add.assert_called_once()
            call_kwargs = mock_add.call_args[1]
            assert call_kwargs["level"] == "INFO"
