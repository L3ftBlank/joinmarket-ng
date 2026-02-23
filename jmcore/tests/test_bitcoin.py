"""
Tests for jmcore.bitcoin module.
"""

import base64
import os

from jmcore.bitcoin import (
    PSBT_MAGIC,
    PSBTInput,
    TxInput,
    TxOutput,
    calculate_tx_vsize,
    create_psbt,
    decode_varint,
    estimate_vsize,
    parse_transaction,
    psbt_to_base64,
    script_to_p2wsh_scriptpubkey,
)


def create_synthetic_segwit_tx(num_inputs: int, num_outputs: int) -> bytes:
    """
    Create a synthetic SegWit transaction for testing vsize calculation.

    This creates a valid transaction structure with random data for testing.
    """
    parts = []

    # Version (4 bytes)
    parts.append(b"\x02\x00\x00\x00")

    # SegWit marker and flag
    parts.append(b"\x00\x01")

    # Input count (varint)
    parts.append(bytes([num_inputs]))

    # Inputs: each has txid(32) + vout(4) + scriptSig_len(1, =0 for segwit) + seq(4)
    for _ in range(num_inputs):
        parts.append(os.urandom(32))  # Random txid
        parts.append(b"\x00\x00\x00\x00")  # vout = 0
        parts.append(b"\x00")  # Empty scriptSig
        parts.append(b"\xff\xff\xff\xff")  # sequence

    # Output count (varint)
    parts.append(bytes([num_outputs]))

    # Outputs: each has value(8) + script_len(1) + P2WPKH script(22)
    for _ in range(num_outputs):
        parts.append(os.urandom(8))  # Random value
        parts.append(b"\x16")  # Script length = 22
        parts.append(b"\x00\x14")  # OP_0 PUSH20
        parts.append(os.urandom(20))  # Random pubkey hash

    # Witness data: for each input, standard P2WPKH witness
    for _ in range(num_inputs):
        parts.append(b"\x02")  # 2 stack items
        # Signature (~71-72 bytes, use 71)
        parts.append(b"\x47")  # 71 bytes
        parts.append(os.urandom(71))
        # Compressed pubkey (33 bytes)
        parts.append(b"\x21")  # 33 bytes
        parts.append(b"\x02")  # Compressed pubkey prefix
        parts.append(os.urandom(32))

    # Locktime (4 bytes)
    parts.append(b"\x00\x00\x00\x00")

    return b"".join(parts)


def create_synthetic_legacy_tx(num_inputs: int, num_outputs: int) -> bytes:
    """
    Create a synthetic legacy (non-SegWit) transaction for testing.
    """
    parts = []

    # Version (4 bytes)
    parts.append(b"\x01\x00\x00\x00")

    # Input count (varint)
    parts.append(bytes([num_inputs]))

    # Inputs: each has txid(32) + vout(4) + scriptSig + seq(4)
    for _ in range(num_inputs):
        parts.append(os.urandom(32))  # Random txid
        parts.append(b"\x00\x00\x00\x00")  # vout = 0
        # P2PKH scriptSig: sig(~71) + pubkey(33) + push opcodes
        parts.append(b"\x6a")  # Script length = 106
        parts.append(b"\x47")  # Push 71 bytes (signature)
        parts.append(os.urandom(71))
        parts.append(b"\x21")  # Push 33 bytes (pubkey)
        parts.append(b"\x02")  # Compressed pubkey prefix
        parts.append(os.urandom(32))
        parts.append(b"\xff\xff\xff\xff")  # sequence

    # Output count (varint)
    parts.append(bytes([num_outputs]))

    # Outputs: each has value(8) + script_len(1) + P2PKH script(25)
    for _ in range(num_outputs):
        parts.append(os.urandom(8))  # Random value
        parts.append(b"\x19")  # Script length = 25
        parts.append(b"\x76\xa9\x14")  # OP_DUP OP_HASH160 PUSH20
        parts.append(os.urandom(20))  # Random pubkey hash
        parts.append(b"\x88\xac")  # OP_EQUALVERIFY OP_CHECKSIG

    # Locktime (4 bytes)
    parts.append(b"\x00\x00\x00\x00")

    return b"".join(parts)


class TestCalculateTxVsize:
    """Tests for calculate_tx_vsize function."""

    def test_calculate_vsize_segwit_single_input_output(self) -> None:
        """Test vsize calculation for minimal SegWit transaction."""
        tx_bytes = create_synthetic_segwit_tx(1, 1)

        vsize = calculate_tx_vsize(tx_bytes)

        # For a SegWit transaction, vsize should be less than serialized size
        assert vsize < len(tx_bytes)

        # 1 P2WPKH input: ~68 vbytes, 1 P2WPKH output: ~31 vbytes, overhead: ~11
        # Expected: ~110 vbytes
        expected = estimate_vsize(["p2wpkh"], ["p2wpkh"])
        # Allow some variance due to signature size differences
        assert abs(vsize - expected) < 15, f"vsize {vsize} too far from expected {expected}"

    def test_calculate_vsize_segwit_coinjoin_like(self) -> None:
        """Test vsize calculation for CoinJoin-like transaction (10 in, 13 out)."""
        tx_bytes = create_synthetic_segwit_tx(10, 13)

        vsize = calculate_tx_vsize(tx_bytes)

        # For a SegWit transaction, vsize should be less than serialized size
        assert vsize < len(tx_bytes)

        # Expected: 10*68 + 13*31 + 11 = 1094 vbytes
        expected = estimate_vsize(["p2wpkh"] * 10, ["p2wpkh"] * 13)
        # Allow some variance
        assert abs(vsize - expected) < 30, f"vsize {vsize} too far from expected {expected}"

    def test_calculate_vsize_scales_with_inputs(self) -> None:
        """Test that vsize scales properly with number of inputs."""
        vsize_1 = calculate_tx_vsize(create_synthetic_segwit_tx(1, 1))
        vsize_2 = calculate_tx_vsize(create_synthetic_segwit_tx(2, 1))
        vsize_5 = calculate_tx_vsize(create_synthetic_segwit_tx(5, 1))

        # Each additional P2WPKH input adds ~68 vbytes
        diff_1_to_2 = vsize_2 - vsize_1
        diff_2_to_5 = vsize_5 - vsize_2

        assert 60 < diff_1_to_2 < 80, f"Input diff {diff_1_to_2} outside range"
        # 3 inputs difference
        assert 180 < diff_2_to_5 < 240, f"3-input diff {diff_2_to_5} outside range"

    def test_calculate_vsize_scales_with_outputs(self) -> None:
        """Test that vsize scales properly with number of outputs."""
        vsize_1 = calculate_tx_vsize(create_synthetic_segwit_tx(1, 1))
        vsize_2 = calculate_tx_vsize(create_synthetic_segwit_tx(1, 2))
        vsize_5 = calculate_tx_vsize(create_synthetic_segwit_tx(1, 5))

        # Each additional P2WPKH output adds ~31 vbytes
        diff_1_to_2 = vsize_2 - vsize_1
        diff_2_to_5 = vsize_5 - vsize_2

        assert 25 < diff_1_to_2 < 40, f"Output diff {diff_1_to_2} outside range"
        # 3 outputs difference
        assert 80 < diff_2_to_5 < 120, f"3-output diff {diff_2_to_5} outside range"

    def test_calculate_vsize_legacy_transaction(self) -> None:
        """Test vsize calculation for legacy (non-SegWit) transaction."""
        tx_bytes = create_synthetic_legacy_tx(1, 1)

        vsize = calculate_tx_vsize(tx_bytes)

        # For legacy transactions, vsize equals serialized size
        assert vsize == len(tx_bytes)

    def test_calculate_vsize_legacy_multiple_inputs(self) -> None:
        """Test legacy transaction vsize scales with inputs."""
        vsize_1 = calculate_tx_vsize(create_synthetic_legacy_tx(1, 1))
        vsize_3 = calculate_tx_vsize(create_synthetic_legacy_tx(3, 1))

        # For legacy, each P2PKH input adds ~148 bytes
        diff = vsize_3 - vsize_1
        # 2 additional inputs
        assert 280 < diff < 320, f"Legacy input diff {diff} outside range"


class TestEstimateVsize:
    """Tests for estimate_vsize function."""

    def test_estimate_vsize_p2wpkh(self) -> None:
        """Test vsize estimation for P2WPKH inputs/outputs."""
        vsize = estimate_vsize(["p2wpkh"], ["p2wpkh"])
        # 1 input (68) + 1 output (31) + overhead (~11) = ~110 vbytes
        assert 100 < vsize < 120

    def test_estimate_vsize_multiple_inputs(self) -> None:
        """Test vsize estimation scales with inputs."""
        vsize_1 = estimate_vsize(["p2wpkh"], ["p2wpkh"])
        vsize_2 = estimate_vsize(["p2wpkh", "p2wpkh"], ["p2wpkh"])

        # Adding one input should add ~68 vbytes
        diff = vsize_2 - vsize_1
        assert 60 < diff < 75

    def test_estimate_vsize_coinjoin_like(self) -> None:
        """Test vsize estimation for CoinJoin-like transaction."""
        # 10 inputs, 13 outputs
        vsize = estimate_vsize(["p2wpkh"] * 10, ["p2wpkh"] * 13)

        # 10 * 68 + 13 * 31 + 11 = 680 + 403 + 11 = 1094 vbytes
        expected = 10 * 68 + 13 * 31 + 11
        assert vsize == expected


# =============================================================================
# PSBT Tests
# =============================================================================

# Deterministic test data for reproducible PSBT tests
TEST_TXID = "a" * 64  # 32 bytes of 0xaa when reversed
TEST_PUBKEY_HEX = "02" + "bb" * 32  # Fake compressed pubkey
TEST_LOCKTIME = 1672531200  # 2023-01-01 00:00:00 UTC


def _make_witness_script() -> bytes:
    """Create a deterministic CLTV witness script for testing."""
    from jmcore.btc_script import mk_freeze_script

    return mk_freeze_script(TEST_PUBKEY_HEX, TEST_LOCKTIME)


def _make_p2wsh_scriptpubkey(witness_script: bytes) -> bytes:
    """Derive P2WSH scriptPubKey from witness script."""
    return script_to_p2wsh_scriptpubkey(witness_script)


class TestPSBTMagic:
    """Verify PSBT magic constant."""

    def test_magic_bytes(self) -> None:
        assert PSBT_MAGIC == b"psbt\xff"

    def test_magic_length(self) -> None:
        assert len(PSBT_MAGIC) == 5


class TestCreatePSBT:
    """Tests for create_psbt function."""

    def test_psbt_starts_with_magic(self) -> None:
        """PSBT must begin with the BIP-174 magic bytes."""
        ws = _make_witness_script()
        spk = _make_p2wsh_scriptpubkey(ws)

        tx_in = TxInput.from_hex(TEST_TXID, 0, sequence=0xFFFFFFFE, value=100_000)
        tx_out = TxOutput(value=99_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)
        pi = PSBTInput(
            witness_utxo_value=100_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )

        psbt = create_psbt(
            version=2,
            inputs=[tx_in],
            outputs=[tx_out],
            locktime=TEST_LOCKTIME,
            psbt_inputs=[pi],
        )
        assert psbt[:5] == PSBT_MAGIC

    def test_psbt_contains_unsigned_tx(self) -> None:
        """Global map must contain the unsigned transaction."""
        ws = _make_witness_script()
        spk = _make_p2wsh_scriptpubkey(ws)

        tx_in = TxInput.from_hex(TEST_TXID, 0, sequence=0xFFFFFFFE, value=100_000)
        tx_out = TxOutput(value=99_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)
        pi = PSBTInput(
            witness_utxo_value=100_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )

        psbt = create_psbt(
            version=2,
            inputs=[tx_in],
            outputs=[tx_out],
            locktime=TEST_LOCKTIME,
            psbt_inputs=[pi],
        )

        # After magic (5 bytes), the first key-value pair should be the unsigned tx
        # Key: <varint 1> <0x00>  (type 0x00, global unsigned tx)
        assert psbt[5] == 0x01  # key length = 1
        assert psbt[6] == 0x00  # key type = PSBT_GLOBAL_UNSIGNED_TX

        # The unsigned tx should be parseable
        # Read value length
        val_len, offset = decode_varint(psbt, 7)
        unsigned_tx_bytes = psbt[offset : offset + val_len]

        # Parse it and verify structure
        parsed = parse_transaction(unsigned_tx_bytes.hex())
        assert parsed.version == 2
        assert len(parsed.inputs) == 1
        assert len(parsed.outputs) == 1
        assert parsed.locktime == TEST_LOCKTIME
        assert parsed.inputs[0].sequence == 0xFFFFFFFE
        assert parsed.outputs[0].value == 99_000

    def test_psbt_roundtrip_base64(self) -> None:
        """PSBT should survive base64 encode/decode roundtrip."""
        ws = _make_witness_script()
        spk = _make_p2wsh_scriptpubkey(ws)

        tx_in = TxInput.from_hex(TEST_TXID, 0, sequence=0xFFFFFFFE, value=50_000)
        tx_out = TxOutput(value=49_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)
        pi = PSBTInput(
            witness_utxo_value=50_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )

        psbt = create_psbt(
            version=2,
            inputs=[tx_in],
            outputs=[tx_out],
            locktime=TEST_LOCKTIME,
            psbt_inputs=[pi],
        )

        b64 = psbt_to_base64(psbt)
        decoded = base64.b64decode(b64)
        assert decoded == psbt

    def test_psbt_mismatched_inputs_raises(self) -> None:
        """create_psbt must raise ValueError when input counts mismatch."""
        import pytest

        tx_in = TxInput.from_hex(TEST_TXID, 0, sequence=0xFFFFFFFE, value=100_000)
        tx_out = TxOutput(value=99_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)

        with pytest.raises(ValueError, match="same length"):
            create_psbt(
                version=2,
                inputs=[tx_in],
                outputs=[tx_out],
                locktime=0,
                psbt_inputs=[],  # Empty - mismatch!
            )

    def test_psbt_multiple_inputs(self) -> None:
        """PSBT with multiple inputs should have per-input maps for each."""
        ws = _make_witness_script()
        spk = _make_p2wsh_scriptpubkey(ws)

        tx_in1 = TxInput.from_hex("aa" * 32, 0, sequence=0xFFFFFFFE, value=50_000)
        tx_in2 = TxInput.from_hex("bb" * 32, 1, sequence=0xFFFFFFFE, value=60_000)
        tx_out = TxOutput(value=109_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)

        pi1 = PSBTInput(
            witness_utxo_value=50_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )
        pi2 = PSBTInput(
            witness_utxo_value=60_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )

        psbt = create_psbt(
            version=2,
            inputs=[tx_in1, tx_in2],
            outputs=[tx_out],
            locktime=TEST_LOCKTIME,
            psbt_inputs=[pi1, pi2],
        )

        # Verify the unsigned tx has 2 inputs
        # Skip magic, read global unsigned tx
        assert psbt[5] == 0x01  # key len
        assert psbt[6] == 0x00  # key type
        val_len, offset = decode_varint(psbt, 7)
        unsigned_tx_bytes = psbt[offset : offset + val_len]

        parsed = parse_transaction(unsigned_tx_bytes.hex())
        assert len(parsed.inputs) == 2
        assert parsed.inputs[0].txid == "aa" * 32
        assert parsed.inputs[1].txid == "bb" * 32
        assert parsed.inputs[1].vout == 1

    def test_psbt_witness_script_included(self) -> None:
        """Per-input map must contain the witness script."""
        ws = _make_witness_script()
        spk = _make_p2wsh_scriptpubkey(ws)

        tx_in = TxInput.from_hex(TEST_TXID, 0, sequence=0xFFFFFFFE, value=100_000)
        tx_out = TxOutput(value=99_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)
        pi = PSBTInput(
            witness_utxo_value=100_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )

        psbt = create_psbt(
            version=2,
            inputs=[tx_in],
            outputs=[tx_out],
            locktime=TEST_LOCKTIME,
            psbt_inputs=[pi],
        )

        # The witness script bytes must appear in the PSBT
        assert ws in psbt

    def test_psbt_locktime_in_unsigned_tx(self) -> None:
        """The unsigned tx inside the PSBT must have the correct nLockTime."""
        ws = _make_witness_script()
        spk = _make_p2wsh_scriptpubkey(ws)
        custom_locktime = 1735689600  # 2025-01-01

        tx_in = TxInput.from_hex(TEST_TXID, 0, sequence=0xFFFFFFFE, value=100_000)
        tx_out = TxOutput(value=99_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)
        pi = PSBTInput(
            witness_utxo_value=100_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )

        psbt = create_psbt(
            version=2,
            inputs=[tx_in],
            outputs=[tx_out],
            locktime=custom_locktime,
            psbt_inputs=[pi],
        )

        # Parse the embedded unsigned tx to verify locktime
        val_len, offset = decode_varint(psbt, 7)
        unsigned_tx_bytes = psbt[offset : offset + val_len]
        parsed = parse_transaction(unsigned_tx_bytes.hex())
        assert parsed.locktime == custom_locktime

    def test_psbt_sequence_enables_locktime(self) -> None:
        """Input sequence in unsigned tx must be < 0xFFFFFFFF for locktime."""
        ws = _make_witness_script()
        spk = _make_p2wsh_scriptpubkey(ws)

        tx_in = TxInput.from_hex(TEST_TXID, 0, sequence=0xFFFFFFFE, value=100_000)
        tx_out = TxOutput(value=99_000, script=bytes([0x00, 0x14]) + b"\x00" * 20)
        pi = PSBTInput(
            witness_utxo_value=100_000,
            witness_utxo_script=spk,
            witness_script=ws,
        )

        psbt = create_psbt(
            version=2,
            inputs=[tx_in],
            outputs=[tx_out],
            locktime=TEST_LOCKTIME,
            psbt_inputs=[pi],
        )

        val_len, offset = decode_varint(psbt, 7)
        unsigned_tx_bytes = psbt[offset : offset + val_len]
        parsed = parse_transaction(unsigned_tx_bytes.hex())
        assert parsed.inputs[0].sequence == 0xFFFFFFFE


class TestPSBTToBase64:
    """Tests for psbt_to_base64 function."""

    def test_returns_valid_base64(self) -> None:
        """Output must be valid base64 that decodes back to original."""
        raw = PSBT_MAGIC + b"\x00" * 10
        b64 = psbt_to_base64(raw)
        assert base64.b64decode(b64) == raw

    def test_returns_ascii_string(self) -> None:
        """Output must be a pure ASCII string."""
        raw = PSBT_MAGIC + os.urandom(50)
        b64 = psbt_to_base64(raw)
        assert isinstance(b64, str)
        b64.encode("ascii")  # Should not raise
