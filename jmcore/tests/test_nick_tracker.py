"""
Tests for multi-directory aware nick tracking.

Verifies the behavior from JoinMarket reference implementation where a nick
is only considered "gone" when ALL directory connections report it as disconnected.
"""

from jmcore.nick_tracker import NickTracker


def test_nick_tracker_basic():
    """Test basic nick presence tracking."""
    tracker = NickTracker[str]()

    # Add nick to directory1
    tracker.mark_nick_present("maker1", "dir1")
    assert tracker.is_nick_active("maker1")
    assert tracker.get_active_directories_for_nick("maker1") == ["dir1"]

    # Add same nick to directory2
    tracker.mark_nick_present("maker1", "dir2")
    assert tracker.is_nick_active("maker1")
    assert set(tracker.get_active_directories_for_nick("maker1")) == {"dir1", "dir2"}


def test_nick_leave_single_directory():
    """Test that nick is NOT considered gone when it leaves one directory but remains on another."""
    left_nicks = []

    def on_leave(nick: str) -> None:
        left_nicks.append(nick)

    tracker = NickTracker[str](on_nick_leave=on_leave)

    # Nick present on two directories
    tracker.mark_nick_present("maker1", "dir1")
    tracker.mark_nick_present("maker1", "dir2")

    # Nick leaves dir1 but still on dir2
    tracker.mark_nick_gone("maker1", "dir1")

    # Should still be active
    assert tracker.is_nick_active("maker1")
    assert tracker.get_active_directories_for_nick("maker1") == ["dir2"]

    # Callback should NOT have been triggered
    assert len(left_nicks) == 0


def test_nick_leave_all_directories():
    """Test that nick IS considered gone when it leaves ALL directories."""
    left_nicks = []

    def on_leave(nick: str) -> None:
        left_nicks.append(nick)

    tracker = NickTracker[str](on_nick_leave=on_leave)

    # Nick present on two directories
    tracker.mark_nick_present("maker1", "dir1")
    tracker.mark_nick_present("maker1", "dir2")

    # Nick leaves dir1
    tracker.mark_nick_gone("maker1", "dir1")
    assert len(left_nicks) == 0

    # Nick leaves dir2 (last directory)
    tracker.mark_nick_gone("maker1", "dir2")

    # Should be gone
    assert not tracker.is_nick_active("maker1")
    assert tracker.get_active_directories_for_nick("maker1") == []

    # Callback should have been triggered once
    assert left_nicks == ["maker1"]


def test_nick_return_after_leaving():
    """Test that a nick can return to a directory after leaving."""
    left_nicks = []

    def on_leave(nick: str) -> None:
        left_nicks.append(nick)

    tracker = NickTracker[str](on_nick_leave=on_leave)

    # Nick on one directory
    tracker.mark_nick_present("maker1", "dir1")

    # Nick leaves
    tracker.mark_nick_gone("maker1", "dir1")
    assert len(left_nicks) == 1
    assert not tracker.is_nick_active("maker1")

    # Nick returns to the same directory
    tracker.mark_nick_present("maker1", "dir1")
    assert tracker.is_nick_active("maker1")

    # Still only one leave event
    assert len(left_nicks) == 1


def test_sync_with_peerlist():
    """Test synchronizing nick state with a directory's peerlist."""
    left_nicks = []

    def on_leave(nick: str) -> None:
        left_nicks.append(nick)

    tracker = NickTracker[str](on_nick_leave=on_leave)

    # Initial sync with dir1
    tracker.sync_with_peerlist("dir1", {"maker1", "maker2", "maker3"})
    assert tracker.get_all_active_nicks() == {"maker1", "maker2", "maker3"}

    # maker2 and maker3 disappear from dir1
    tracker.sync_with_peerlist("dir1", {"maker1"})

    # They should be marked gone (triggered callbacks)
    assert "maker2" in left_nicks
    assert "maker3" in left_nicks
    assert tracker.is_nick_active("maker1")
    assert not tracker.is_nick_active("maker2")
    assert not tracker.is_nick_active("maker3")


def test_sync_multi_directory_peerlist():
    """Test that sync doesn't prematurely mark nicks as gone when on multiple directories."""
    left_nicks = []

    def on_leave(nick: str) -> None:
        left_nicks.append(nick)

    tracker = NickTracker[str](on_nick_leave=on_leave)

    # maker1 on both directories
    tracker.sync_with_peerlist("dir1", {"maker1", "maker2"})
    tracker.sync_with_peerlist("dir2", {"maker1", "maker3"})

    assert tracker.get_all_active_nicks() == {"maker1", "maker2", "maker3"}

    # maker1 disappears from dir1 but still on dir2
    tracker.sync_with_peerlist("dir1", {"maker2"})

    # maker1 should still be active (on dir2)
    assert tracker.is_nick_active("maker1")
    assert "maker1" not in left_nicks

    # maker1 also disappears from dir2
    tracker.sync_with_peerlist("dir2", {"maker3"})

    # NOW maker1 should be gone
    assert not tracker.is_nick_active("maker1")
    assert "maker1" in left_nicks


def test_remove_directory():
    """Test removing a directory from tracking."""
    left_nicks = []

    def on_leave(nick: str) -> None:
        left_nicks.append(nick)

    tracker = NickTracker[str](on_nick_leave=on_leave)

    # Set up nicks across directories
    tracker.mark_nick_present("maker1", "dir1")  # Only on dir1
    tracker.mark_nick_present("maker2", "dir1")  # On both
    tracker.mark_nick_present("maker2", "dir2")
    tracker.mark_nick_present("maker3", "dir2")  # Only on dir2

    # Remove dir1
    gone_nicks = tracker.remove_directory("dir1")

    # maker1 should be gone (was only on dir1)
    # maker2 should still be active (still on dir2)
    # maker3 unaffected (never on dir1)
    assert "maker1" in gone_nicks
    assert "maker2" not in gone_nicks
    assert "maker3" not in gone_nicks

    assert not tracker.is_nick_active("maker1")
    assert tracker.is_nick_active("maker2")
    assert tracker.is_nick_active("maker3")

    assert "maker1" in left_nicks
    assert "maker2" not in left_nicks


def test_multiple_nicks_multiple_directories():
    """Test complex scenario with multiple nicks across multiple directories."""
    left_nicks = []

    def on_leave(nick: str) -> None:
        left_nicks.append(nick)

    tracker = NickTracker[str](on_nick_leave=on_leave)

    # Simulate real-world scenario
    # dir1: maker1, maker2, maker3
    # dir2: maker1, maker2, maker4
    # dir3: maker1, maker5

    tracker.sync_with_peerlist("dir1", {"maker1", "maker2", "maker3"})
    tracker.sync_with_peerlist("dir2", {"maker1", "maker2", "maker4"})
    tracker.sync_with_peerlist("dir3", {"maker1", "maker5"})

    assert tracker.get_all_active_nicks() == {"maker1", "maker2", "maker3", "maker4", "maker5"}

    # maker3 leaves dir1 (only directory)
    tracker.sync_with_peerlist("dir1", {"maker1", "maker2"})
    assert "maker3" in left_nicks

    # maker1 leaves dir1 (but still on dir2 and dir3)
    tracker.sync_with_peerlist("dir1", {"maker2"})
    assert "maker1" not in left_nicks  # Still on other directories
    assert tracker.is_nick_active("maker1")

    # maker1 leaves dir2 (but still on dir3)
    tracker.sync_with_peerlist("dir2", {"maker2", "maker4"})
    assert "maker1" not in left_nicks  # Still on dir3
    assert tracker.is_nick_active("maker1")

    # maker1 leaves dir3 (last directory)
    tracker.sync_with_peerlist("dir3", {"maker5"})
    assert "maker1" in left_nicks  # NOW it's gone from all
    assert not tracker.is_nick_active("maker1")


def test_get_all_active_nicks():
    """Test getting all currently active nicks."""
    tracker = NickTracker[str]()

    tracker.mark_nick_present("maker1", "dir1")
    tracker.mark_nick_present("maker2", "dir1")
    tracker.mark_nick_present("maker2", "dir2")
    tracker.mark_nick_present("maker3", "dir2")

    active = tracker.get_all_active_nicks()
    assert active == {"maker1", "maker2", "maker3"}

    # Mark maker2 as gone from both directories
    tracker.mark_nick_gone("maker2", "dir1")
    tracker.mark_nick_gone("maker2", "dir2")

    active = tracker.get_all_active_nicks()
    assert active == {"maker1", "maker3"}


def test_no_callback():
    """Test that tracker works fine without a callback."""
    tracker = NickTracker[str]()  # No on_nick_leave callback

    tracker.mark_nick_present("maker1", "dir1")
    tracker.mark_nick_gone("maker1", "dir1")

    # Should not crash
    assert not tracker.is_nick_active("maker1")
