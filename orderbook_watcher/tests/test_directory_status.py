"""
Tests for DirectoryNodeStatus uptime calculations.
"""

from datetime import datetime, timedelta

from orderbook_watcher.aggregator import DirectoryNodeStatus


def test_uptime_accumulates_across_disconnects() -> None:
    status = DirectoryNodeStatus("node.test")
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    status.mark_connected(start_time)

    mid_time = start_time + timedelta(minutes=5)
    status.mark_disconnected(mid_time)

    status.mark_connected(mid_time + timedelta(minutes=10))
    second_end = mid_time + timedelta(minutes=20)
    status.mark_disconnected(second_end)

    uptime = status.get_uptime_percentage(second_end)
    assert uptime == 60.0


def test_uptime_updates_when_session_in_progress() -> None:
    status = DirectoryNodeStatus("node.test")
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    status.mark_connected(start_time)

    now = start_time + timedelta(minutes=5)
    uptime = status.get_uptime_percentage(now)

    assert uptime == 100.0
