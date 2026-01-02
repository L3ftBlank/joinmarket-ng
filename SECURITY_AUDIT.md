# Security Audit Report: JoinMarket-NG Maker Implementation

**Date:** January 2026
**Scope:** Maker implementation security analysis
**Focus:** Vulnerabilities where a malicious taker could cause loss of maker funds

---

## Executive Summary

This security audit analyzed the JoinMarket-NG maker implementation with focus on preventing fund loss from malicious takers. The codebase demonstrates **strong security practices** with proper transaction verification before signing.

**Overall Assessment:** The implementation correctly verifies all critical security properties before signing transactions. No vulnerabilities allowing direct fund theft were identified. Several recommendations are provided for defense-in-depth improvements.

**Test Status:** 134 maker tests passing, including 19 critical transaction verification tests.

---

## 1. Scope of Audit

### Files Analyzed

| File | Purpose | Risk Level |
|------|---------|------------|
| `maker/src/maker/tx_verification.py` | Transaction verification before signing | **CRITICAL** |
| `maker/src/maker/coinjoin.py` | CoinJoin session handling | **HIGH** |
| `maker/src/maker/bot.py` | Message handling, rate limiting | **MEDIUM** |
| `maker/src/maker/offers.py` | Offer creation, fee calculation | **MEDIUM** |
| `maker/src/maker/config.py` | Configuration validation | **LOW** |
| `jmcore/src/jmcore/podle.py` | PoDLE proof verification | **HIGH** |
| `jmcore/src/jmcore/bitcoin.py` | Amount/fee calculations | **HIGH** |
| `jmcore/src/jmcore/crypto.py` | Cryptographic operations | **HIGH** |

### Attack Vectors Considered

1. **Direct Fund Theft:** Taker tricks maker into signing transaction that steals funds
2. **Arithmetic Manipulation:** Integer overflow/underflow in fee calculations
3. **Output Manipulation:** Missing/incorrect outputs, duplicate addresses
4. **DoS Attacks:** Resource exhaustion, session manipulation
5. **Privacy Leaks:** Information disclosure through timing/errors

---

## 2. Critical Security Analysis

### 2.1 Transaction Verification (`tx_verification.py`)

This is the **most critical security component**. Any bug here results in direct fund loss.

#### Verification Checklist (All Implemented)

| Check | Status | Location |
|-------|--------|----------|
| All maker UTXOs included in tx | **PASS** | Line 103 |
| CJ output pays correct amount | **PASS** | Lines 133-139 |
| Change output pays correct amount | **PASS** | Lines 141-147 |
| Positive profit (cjfee - txfee > 0) | **PASS** | Lines 113-120 |
| CJ address appears exactly once | **PASS** | Lines 149-153 |
| Change address appears exactly once | **PASS** | Lines 155-159 |
| Transaction parses correctly | **PASS** | Lines 92-95 |

#### Key Formula Verification

```python
# Line 111: Change calculation
expected_change_value = my_total_in - amount - txfee + real_cjfee

# Line 113: Profit calculation
potentially_earned = real_cjfee - txfee
```

**Analysis:** These formulas are correct. The maker's balance sheet:
- **In:** `my_total_in` (UTXOs contributed)
- **Out:** `amount` (CJ output) + `expected_change_value` (change)
- **Net:** `real_cjfee - txfee` (profit)

The verification ensures `output_value >= expected` for both CJ and change outputs, preventing underpayment attacks.

### 2.2 Potential Issues Identified

#### Issue 1: Change Output Dust Scenario (MEDIUM RISK)

**Location:** `tx_verification.py:155-159`

**Issue:** The verification requires `times_seen_change_addr == 1`, but in edge cases where maker's change would be dust, the taker might legitimately not create a change output.

**Current Behavior:** If expected_change is below dust threshold, but no change output exists, verification fails with "Change address appears 0 times".

**Risk Assessment:** **MEDIUM** - This is a false negative (legitimate CoinJoins rejected), not a fund loss vulnerability. The maker loses potential earnings but not funds.

**Recommendation:** Consider adding dust-awareness:
```python
# Suggested improvement
if expected_change_value > DUST_THRESHOLD:
    if times_seen_change_addr != 1:
        return False, f"Change address appears {times_seen_change_addr} times (expected 1)"
elif times_seen_change_addr > 1:
    return False, f"Change address appears {times_seen_change_addr} times (expected 0 or 1)"
```

#### Issue 2: Output Value Inequality Direction (VERIFIED CORRECT)

**Location:** `tx_verification.py:135, 143`

**Code:**
```python
if output_value < amount:  # CJ output check
if output_value < expected_change_value:  # Change check
```

**Analysis:** Using `<` (less than) is correct. The maker accepts if they receive **at least** the expected amount. Receiving more is acceptable (extra goes to miner fee from taker's perspective).

#### Issue 3: Integer Overflow Potential (LOW RISK)

**Location:** `tx_verification.py:107-111`

**Analysis:** Python 3 uses arbitrary-precision integers, eliminating integer overflow. All values are in satoshis (max ~21 trillion), well within 64-bit bounds even in other languages.

**Status:** No vulnerability in Python. Consider bounds validation for defense-in-depth.

### 2.3 CoinJoin Session Security (`coinjoin.py`)

#### PoDLE Verification (Lines 198-213)

**Analysis:** Properly verifies PoDLE proof before accepting taker's commitment. Uses `verify_podle()` from jmcore with configurable retry index range.

**Security Properties Verified:**
- Commitment matches revelation
- Signature is valid over NUMS point
- UTXO exists on blockchain
- UTXO meets age and amount requirements

#### Taker UTXO Validation (Lines 254-272)

**Analysis:** Verifies taker's UTXO before proceeding:
- UTXO exists (blockchain lookup)
- Sufficient confirmations (`taker_utxo_age`)
- Sufficient value (`taker_utxo_amtpercent` of CJ amount)

**Status:** Proper anti-sybil measures implemented.

#### Signing Safety (Lines 508-513)

```python
if utxo_info.is_p2wsh:
    raise TransactionSigningError(
        f"Cannot sign P2WSH UTXO {txid}:{vout} in CoinJoin - "
        f"fidelity bond UTXOs cannot be used in CoinJoins"
    )
```

**Analysis:** Excellent safety check preventing fidelity bond UTXOs from being accidentally spent in CoinJoins.

---

## 3. DoS Attack Analysis

### 3.1 Rate Limiting (`bot.py`)

#### Generic Message Rate Limiter (Lines 299-304)

```python
self._message_rate_limiter = RateLimiter(
    rate_limit=config.message_rate_limit,
    burst_limit=config.message_burst_limit,
)
```

**Analysis:** Token bucket algorithm with configurable burst. Prevents basic flooding.

#### Orderbook Rate Limiter (Lines 63-258)

**Analysis:** Sophisticated multi-tier protection:

| Tier | Violations | Interval | Protection |
|------|------------|----------|------------|
| Normal | 0-10 | 10s | Base rate |
| Moderate | 11-50 | 60s | 6x backoff |
| Severe | 51-99 | 300s | 30x backoff |
| Ban | 100+ | 1 hour | Complete block |

**Status:** Excellent DoS protection. Prevents log flooding and resource exhaustion.

### 3.2 Session Timeout (Lines 101-103)

```python
def is_timed_out(self) -> bool:
    return time.time() - self.created_at > self.session_timeout_sec
```

**Analysis:** Sessions expire after configurable timeout (default 300s). Prevents resource exhaustion from abandoned sessions.

### 3.3 Commitment Blacklisting (`bot.py:1319-1326`)

```python
if not check_commitment(commitment):
    logger.warning(f"Rejecting !fill from {taker_nick}: commitment already used")
    return
```

**Analysis:** Proper blacklist checking prevents PoDLE commitment reuse attacks.

---

## 4. Test Coverage Analysis

### Transaction Verification Tests (`test_tx_verification.py`)

| Test | Security Property | Status |
|------|------------------|--------|
| `test_verify_transaction_negative_profit` | Rejects negative profit | **PASS** |
| `test_verify_transaction_missing_utxo` | Requires all UTXOs | **PASS** |
| `test_verify_transaction_cj_output_too_low` | CJ amount verification | **PASS** |
| `test_verify_transaction_change_output_too_low` | Change amount verification | **PASS** |
| `test_verify_transaction_cj_address_missing` | CJ address required | **PASS** |
| `test_verify_transaction_change_address_missing` | Change address required | **PASS** |
| `test_verify_transaction_duplicate_cj_address` | No duplicate CJ address | **PASS** |
| `test_verify_transaction_parse_failure` | Malformed tx handling | **PASS** |
| `test_verify_transaction_exception_handling` | Exception safety | **PASS** |

### Missing Test Coverage (Recommendations)

1. **Zero expected change scenario** - Test when `expected_change_value = 0`
2. **Dust-level change scenario** - Test when change is below dust threshold
3. **Maximum value edge cases** - Test with values near 21M BTC
4. **Negative fee edge cases** - Test cjfee=0 scenarios
5. **Multiple maker UTXOs** - More coverage for multi-input scenarios

---

## 5. Recommendations

### Critical Priority

| # | Recommendation | Impact |
|---|---------------|--------|
| 1 | Add dust-aware change verification | Prevents false negatives |
| 2 | Add explicit bounds validation on amounts | Defense-in-depth |

### High Priority

| # | Recommendation | Impact |
|---|---------------|--------|
| 3 | Add test for zero/dust change scenarios | Coverage improvement |
| 4 | Log transaction details on verification failure | Debugging/auditing |
| 5 | Consider adding max value bounds checks | Future-proofing |

### Medium Priority

| # | Recommendation | Impact |
|---|---------------|--------|
| 6 | Add metrics for verification failures | Monitoring |
| 7 | Consider fuzz testing tx parser | Robustness |
| 8 | Document security assumptions | Maintainability |

---

## 6. Conclusion

The JoinMarket-NG maker implementation demonstrates **solid security engineering** with:

1. **Correct transaction verification** - All critical checks implemented
2. **Proper arithmetic** - No overflow/underflow vulnerabilities
3. **Strong DoS protection** - Multi-tier rate limiting with bans
4. **Good test coverage** - 19 critical security tests passing

**No vulnerabilities allowing direct fund theft were identified.**

The primary recommendation is to add dust-awareness to change verification to prevent false negatives in edge cases where makers' change would be below dust threshold.

---

## Appendix: Key Security Code Locations

```
maker/src/maker/tx_verification.py:61   # verify_unsigned_transaction()
maker/src/maker/tx_verification.py:111  # Change calculation formula
maker/src/maker/tx_verification.py:113  # Profit check
maker/src/maker/coinjoin.py:342         # handle_tx() - calls verification
maker/src/maker/coinjoin.py:202         # PoDLE verification
maker/src/maker/bot.py:63               # OrderbookRateLimiter class
maker/src/maker/bot.py:1319             # Commitment blacklist check
```

---

*This audit was conducted on the JoinMarket-NG codebase as of January 2026. Future code changes may invalidate these findings.*
