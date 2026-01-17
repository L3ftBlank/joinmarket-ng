"""
Tests for jmcore.bitcoin module.
"""

import os

from jmcore.bitcoin import calculate_tx_vsize, estimate_vsize


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
