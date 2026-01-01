"""
Tests for the rate limiter module.
"""

from __future__ import annotations

import time
from unittest.mock import patch

from jmcore.rate_limiter import RateLimitAction, RateLimiter, TokenBucket


class TestTokenBucket:
    """Tests for TokenBucket class."""

    def test_initial_capacity(self) -> None:
        """Bucket starts at full capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.tokens == 10.0

    def test_consume_success(self) -> None:
        """Consuming tokens when available returns True."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.consume(1) is True
        assert bucket.tokens == 9.0

    def test_consume_multiple(self) -> None:
        """Can consume multiple tokens at once."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.consume(5) is True
        assert bucket.tokens == 5.0

    def test_consume_failure_empty(self) -> None:
        """Consuming when empty returns False."""
        bucket = TokenBucket(capacity=1, refill_rate=1.0)
        assert bucket.consume(1) is True
        assert bucket.consume(1) is False

    def test_refill_over_time(self) -> None:
        """Tokens refill based on elapsed time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/sec

        # Consume all tokens
        for _ in range(10):
            bucket.consume(1)
        assert bucket.tokens < 1.0

        # Mock time passing
        with patch.object(time, "monotonic", return_value=bucket.last_refill + 0.5):
            # After 0.5 seconds at 10/sec, should have ~5 tokens
            assert bucket.consume(1) is True
            # tokens = min(10, old_tokens + 0.5 * 10) - 1 = min(10, ~5) - 1 = ~4
            assert 3.0 < bucket.tokens < 5.0

    def test_capacity_limit(self) -> None:
        """Tokens don't exceed capacity after refill."""
        bucket = TokenBucket(capacity=10, refill_rate=100.0)

        # Mock lots of time passing
        with patch.object(time, "monotonic", return_value=bucket.last_refill + 1000):
            bucket.consume(1)
            assert bucket.tokens == 9.0  # capped at capacity

    def test_reset(self) -> None:
        """Reset restores full capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        bucket.consume(5)
        bucket.reset()
        assert bucket.tokens == 10.0


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allows_initial_messages(self) -> None:
        """New peers can send messages immediately."""
        limiter = RateLimiter(rate_limit=10, burst_limit=20)
        for _ in range(20):
            action, _ = limiter.check("peer1")
            assert action == RateLimitAction.ALLOW

    def test_blocks_after_burst(self) -> None:
        """Blocks messages after burst is exhausted."""
        limiter = RateLimiter(rate_limit=10, burst_limit=5)
        for _ in range(5):
            action, _ = limiter.check("peer1")
            assert action == RateLimitAction.ALLOW
        action, _ = limiter.check("peer1")
        assert action == RateLimitAction.DELAY

    def test_independent_peers(self) -> None:
        """Different peers have independent rate limits."""
        limiter = RateLimiter(rate_limit=10, burst_limit=5)

        # Exhaust peer1's burst
        for _ in range(5):
            limiter.check("peer1")
        action, _ = limiter.check("peer1")
        assert action == RateLimitAction.DELAY

        # peer2 should still be allowed
        action, _ = limiter.check("peer2")
        assert action == RateLimitAction.ALLOW

    def test_violation_counting(self) -> None:
        """Violations are counted per peer."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2)

        # Exhaust burst
        limiter.check("peer1")
        limiter.check("peer1")

        assert limiter.get_violation_count("peer1") == 0

        # These should be violations
        limiter.check("peer1")
        limiter.check("peer1")
        limiter.check("peer1")

        assert limiter.get_violation_count("peer1") == 3

    def test_remove_peer(self) -> None:
        """Removing peer clears their state."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2)

        # Create state for peer
        limiter.check("peer1")
        limiter.check("peer1")
        limiter.check("peer1")  # violation

        assert limiter.get_violation_count("peer1") == 1

        limiter.remove_peer("peer1")

        assert limiter.get_violation_count("peer1") == 0
        # New bucket created on next check
        action, _ = limiter.check("peer1")
        assert action == RateLimitAction.ALLOW

    def test_stats(self) -> None:
        """Stats returns summary information."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2)

        # Create some activity
        for _ in range(5):
            limiter.check("peer1")  # 2 allowed, 3 violations
        for _ in range(3):
            limiter.check("peer2")  # 2 allowed, 1 violation

        stats = limiter.get_stats()
        assert stats["tracked_peers"] == 2
        assert stats["total_violations"] == 4
        assert len(stats["top_violators"]) == 2

    def test_default_burst_limit(self) -> None:
        """Default burst limit is 10x rate limit."""
        limiter = RateLimiter(rate_limit=50)
        # Should allow 500 messages (10x rate)
        for i in range(500):
            action, _ = limiter.check("peer1")
            assert action == RateLimitAction.ALLOW, f"Failed at message {i}"
        action, _ = limiter.check("peer1")
        assert action == RateLimitAction.DELAY

    def test_clear(self) -> None:
        """Clear removes all state."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2)

        limiter.check("peer1")
        limiter.check("peer2")

        limiter.clear()

        assert limiter.get_stats()["tracked_peers"] == 0
        assert limiter.get_stats()["total_violations"] == 0


class TestRateLimiterActions:
    """Tests for check and action-based behavior."""

    def test_allow_action_on_success(self) -> None:
        """Returns ALLOW action when tokens available."""
        limiter = RateLimiter(rate_limit=10, burst_limit=5)
        action, delay = limiter.check("peer1")
        assert action == RateLimitAction.ALLOW
        assert delay == 0.0

    def test_delay_action_on_rate_limit(self) -> None:
        """Returns DELAY action when rate limited."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2)

        # Exhaust burst
        limiter.check("peer1")
        limiter.check("peer1")

        # Next message should be delayed
        action, delay = limiter.check("peer1")
        assert action == RateLimitAction.DELAY
        assert delay > 0.0

    def test_disconnect_action_on_threshold(self) -> None:
        """Returns DISCONNECT action after threshold violations."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2, disconnect_threshold=3)

        # Exhaust burst
        limiter.check("peer1")
        limiter.check("peer1")

        # First two violations should DELAY
        action1, _ = limiter.check("peer1")
        action2, _ = limiter.check("peer1")
        assert action1 == RateLimitAction.DELAY
        assert action2 == RateLimitAction.DELAY

        # Third violation should DISCONNECT
        action3, delay3 = limiter.check("peer1")
        assert action3 == RateLimitAction.DISCONNECT
        assert delay3 == 0.0

    def test_no_disconnect_when_threshold_none(self) -> None:
        """Never disconnects when disconnect_threshold is None."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2, disconnect_threshold=None)

        # Exhaust burst
        limiter.check("peer1")
        limiter.check("peer1")

        # Even after many violations, should only DELAY
        for _ in range(100):
            action, _ = limiter.check("peer1")
            assert action == RateLimitAction.DELAY

    def test_get_delay_for_peer(self) -> None:
        """get_delay_for_peer returns recommended wait time."""
        limiter = RateLimiter(rate_limit=10, burst_limit=2)

        # New peer should have no delay
        assert limiter.get_delay_for_peer("peer1") == 0.0

        # Exhaust burst
        limiter.check("peer1")
        limiter.check("peer1")
        limiter.check("peer1")  # Rate limited

        # Should have delay
        delay = limiter.get_delay_for_peer("peer1")
        assert delay > 0.0
        # At 10 msg/sec, delay should be ~0.1s per token
        assert 0.05 < delay < 0.2

    def test_token_bucket_get_delay_seconds(self) -> None:
        """TokenBucket.get_delay_seconds calculates wait time correctly."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)

        # Full bucket should have no delay
        assert bucket.get_delay_seconds() == 0.0

        # Consume all tokens
        for _ in range(10):
            bucket.consume(1)

        # Should need time to refill 1 token
        delay = bucket.get_delay_seconds()
        # At 10 tokens/sec, need 0.1s per token
        assert 0.09 < delay < 0.11

        # Partially consumed bucket
        bucket.reset()
        bucket.consume(9)  # 1 token left
        assert bucket.get_delay_seconds() == 0.0
