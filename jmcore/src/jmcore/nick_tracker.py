"""
Multi-directory aware nick tracking.

Implements the pattern from JoinMarket reference implementation where a nick
is only considered "gone" when ALL directory connections report it as disconnected.

This prevents premature nick leave detection when:
- A peer temporarily disconnects from one directory but remains on others
- Directory connections are flaky or experiencing network issues
- There's a race condition between directory updates

Reference: joinmarket-clientserver/src/jmdaemon/onionmc.py:1078-1103
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from loguru import logger

# Generic type for directory identifier (could be str, DirectoryClient, etc.)
TDirectory = TypeVar("TDirectory")


class NickTracker(Generic[TDirectory]):
    """
    Tracks nick availability across multiple directory servers.

    A nick is considered "active" if it appears on at least one directory.
    A nick is only marked as "gone" when ALL directories report it as disconnected.

    This implements the multi-directory awareness pattern from the reference
    implementation (onionmc.py lines 1078-1103).
    """

    def __init__(self, on_nick_leave: Callable[[str], None] | None = None):
        """
        Initialize the nick tracker.

        Args:
            on_nick_leave: Optional callback when a nick leaves ALL directories
        """
        # active_nicks[nick] = {directory1: True, directory2: True, ...}
        # True = nick is present on this directory, False = gone from this directory
        self.active_nicks: dict[str, dict[TDirectory, bool]] = {}
        self.on_nick_leave = on_nick_leave

    def update_nick(self, nick: str, directory: TDirectory, is_present: bool) -> None:
        """
        Update a nick's presence status on a specific directory.

        Args:
            nick: The nick to update
            directory: The directory reporting the status
            is_present: True if nick is present on this directory, False if gone
        """
        if nick not in self.active_nicks:
            self.active_nicks[nick] = {}

        old_status = self.active_nicks[nick].get(directory)
        self.active_nicks[nick][directory] = is_present

        # Check if this update causes the nick to be completely gone
        if not is_present and old_status is True:
            # Nick just disappeared from this directory
            # Check if it's still present on any other directory
            if not self.is_nick_active(nick):
                logger.info(
                    f"Nick {nick} has left all directories "
                    f"(directories: {list(self.active_nicks[nick].keys())})"
                )
                if self.on_nick_leave:
                    self.on_nick_leave(nick)
                # Clean up the entry
                del self.active_nicks[nick]
        elif is_present and old_status is False:
            logger.debug(
                f"Nick {nick} returned to directory {directory} (was previously marked gone)"
            )

    def mark_nick_present(self, nick: str, directory: TDirectory) -> None:
        """
        Mark a nick as present on a directory.

        Args:
            nick: The nick
            directory: The directory where the nick is present
        """
        self.update_nick(nick, directory, True)

    def mark_nick_gone(self, nick: str, directory: TDirectory) -> None:
        """
        Mark a nick as gone from a directory.

        If this is the last directory where the nick was present,
        triggers the on_nick_leave callback.

        Args:
            nick: The nick
            directory: The directory where the nick left
        """
        self.update_nick(nick, directory, False)

    def is_nick_active(self, nick: str) -> bool:
        """
        Check if a nick is active on at least one directory.

        Args:
            nick: The nick to check

        Returns:
            True if nick is present on at least one directory
        """
        if nick not in self.active_nicks:
            return False
        return any(status for status in self.active_nicks[nick].values())

    def get_active_directories_for_nick(self, nick: str) -> list[TDirectory]:
        """
        Get list of directories where a nick is currently present.

        Args:
            nick: The nick to query

        Returns:
            List of directories where nick is active
        """
        if nick not in self.active_nicks:
            return []
        return [
            directory for directory, is_present in self.active_nicks[nick].items() if is_present
        ]

    def get_all_active_nicks(self) -> set[str]:
        """
        Get all nicks that are active on at least one directory.

        Returns:
            Set of active nicks
        """
        return {nick for nick in self.active_nicks if self.is_nick_active(nick)}

    def remove_directory(self, directory: TDirectory) -> list[str]:
        """
        Remove a directory from tracking (when connection is lost).

        Returns list of nicks that became completely gone after removing this directory.

        Args:
            directory: The directory to remove

        Returns:
            List of nicks that are no longer active after removing this directory
        """
        gone_nicks = []

        for nick in list(self.active_nicks.keys()):
            if directory in self.active_nicks[nick]:
                # Remove this directory from the nick's tracking
                del self.active_nicks[nick][directory]

                # Check if nick is now gone from all directories
                if not self.active_nicks[nick]:
                    # No directories left for this nick
                    logger.info(f"Nick {nick} is gone (last directory {directory} was removed)")
                    gone_nicks.append(nick)
                    if self.on_nick_leave:
                        self.on_nick_leave(nick)
                    del self.active_nicks[nick]
                elif not self.is_nick_active(nick):
                    # Still tracked on some directories but marked as gone on all
                    logger.info(
                        f"Nick {nick} is gone from all remaining directories "
                        f"after removing {directory}"
                    )
                    gone_nicks.append(nick)
                    if self.on_nick_leave:
                        self.on_nick_leave(nick)
                    del self.active_nicks[nick]

        if gone_nicks:
            logger.info(
                f"After removing directory {directory}, {len(gone_nicks)} nicks are gone: "
                f"{gone_nicks}"
            )

        return gone_nicks

    def sync_with_peerlist(self, directory: TDirectory, active_nicks: set[str]) -> None:
        """
        Synchronize nick tracking with a directory's peerlist.

        This is called after fetching a peerlist from a directory to update
        the nick tracking state. Nicks not in the peerlist are marked as gone
        from that directory.

        Args:
            directory: The directory reporting the peerlist
            active_nicks: Set of nicks currently active on this directory
        """
        # First, mark all nicks in the peerlist as present
        for nick in active_nicks:
            self.mark_nick_present(nick, directory)

        # Then, mark nicks we're tracking but not in this peerlist as gone from this directory
        for nick in list(self.active_nicks.keys()):
            if directory in self.active_nicks[nick] and nick not in active_nicks:
                self.mark_nick_gone(nick, directory)

    def __repr__(self) -> str:
        """String representation showing active nicks and their directories."""
        return f"NickTracker(active_nicks={len(self.get_all_active_nicks())})"
