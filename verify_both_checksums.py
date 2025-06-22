#!/usr/bin/env python3
"""
Verify Both Checksum Types

This script verifies both regular checksum and inverse_checksum calculations.
"""

import struct


def verify_both_checksums(binary_file, num_samples, num_fields):
    """Verify both checksum types."""
    
    with open(binary_file, 'rb') as f:
        data = f.read()
    
    print(f"Verifying both checksum types in {binary_file}")
    print(f"Samples: {num_samples}, Fields per sample: {num_fields}")
    print("-" * 60)
    
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
        # Field 0: 0x15 = 21
        # Field 1: 0x25 = 37
        # Field 2: random value
        # Field 3: checksum = (21 + 37 + random) & 255
        # Field 4: inverse_checksum = -(21 + 37 + random)
        
        field_0 = sample_data[0]  # 0x15
        field_1 = sample_data[1]  # 0x25  
        field_2 = sample_data[2]  # random
        checksum = sample_data[3]
        inverse_checksum = sample_data[4]
        
        # Non-checksum fields (first 3 fields)
        other_fields = sample_data[:3]
        sum_other = sum(other_fields)
        
        expected_checksum = sum_other & 255  # Regular checksum (unsigned)
        expected_inverse = -sum_other        # Inverse checksum (signed)
        
        print(f"Sample {sample}:")
        print(f"  Fields 0-2: {other_fields} (sum = {sum_other})")
        print(f"  Expected checksum: {expected_checksum}")
        print(f"  Actual checksum: {checksum}")
        print(f"  Checksum correct: {checksum == expected_checksum}")
        print(f"  Expected inverse_checksum: {expected_inverse}")
        print(f"  Actual inverse_checksum: {inverse_checksum}")
        print(f"  Inverse checksum correct: {inverse_checksum == expected_inverse}")
        print()


if __name__ == '__main__':
    verify_both_checksums('test_both_checksums.bin', 5, 5)
