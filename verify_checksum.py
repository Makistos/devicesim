#!/usr/bin/env python3
"""
Verify Checksum Calculation

This script reads the generated binary data and verifies that the inverse_checksum
field is correctly calculated as the negative sum of all other bytes.
"""

import struct
import sys


def verify_checksum(binary_file, num_samples, num_fields):
    """Verify that inverse_checksum is correctly calculated."""

    with open(binary_file, 'rb') as f:
        data = f.read()

    print(f"Verifying checksum calculation in {binary_file}")
    print(f"Samples: {num_samples}, Fields per sample: {num_fields}")
    print("-" * 50)

    byte_format = 'B'  # Unsigned byte
    signed_format = 'b'  # Signed byte

    for sample in range(num_samples):
        sample_start = sample * num_fields
        sample_data = []

        # Read all fields for this sample
        for field in range(num_fields):
            offset = (sample_start + field)
            byte_val = data[offset]

            # Convert to signed if > 127
            if byte_val > 127:
                signed_val = byte_val - 256
            else:
                signed_val = byte_val

            sample_data.append(signed_val)

        # For our test case:
        # Field 0: 0x10 = 16
        # Field 1: 0x20 = 32
        # Field 2: 0x30 = 48
        # Field 3: inverse_checksum = -(16 + 32 + 48) = -96

        other_fields = sample_data[:-1]  # All except last (checksum field)
        checksum_field = sample_data[-1]  # Last field (checksum)

        expected_checksum = -sum(other_fields)

        print(f"Sample {sample}:")
        print(f"  Other fields: {other_fields} (sum = {sum(other_fields)})")
        print(f"  Expected inverse_checksum: {expected_checksum}")
        print(f"  Actual inverse_checksum: {checksum_field}")
        print(f"  Correct: {checksum_field == expected_checksum}")
        print()


if __name__ == '__main__':
    # Test our simple checksum example
    verify_checksum('test_checksum_simple.bin', 3, 4)
