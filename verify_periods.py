#!/usr/bin/env python3
"""
Verify Period Functionality

This script reads the generated binary data and verifies that the period
parameters are working correctly for each function type.
"""

import struct
import math


def verify_periods(binary_file, num_samples, num_fields):
    """Verify that period parameters are working correctly."""
    
    with open(binary_file, 'rb') as f:
        data = f.read()
    
    print(f"Verifying period functionality in {binary_file}")
    print(f"Samples: {num_samples}, Fields per sample: {num_fields}")
    print("-" * 60)
    
    # Extract data for each field
    fields_data = [[] for _ in range(num_fields)]
    
    for sample in range(num_samples):
        sample_start = sample * num_fields
        
        for field in range(num_fields):
            offset = sample_start + field
            byte_val = data[offset]
            
            # Convert to signed if > 127
            if byte_val > 127:
                signed_val = byte_val - 256
            else:
                signed_val = byte_val
                
            fields_data[field].append(signed_val)
    
    # Verify each function's period
    print("Field 0: Sine wave (period = 10 samples)")
    sine_data = fields_data[0]
    print(f"  Values at samples 0, 10, 20, 30, 40: {[sine_data[i] for i in [0, 10, 20, 30, 40] if i < len(sine_data)]}")
    print(f"  Should repeat every 10 samples")
    
    print("\nField 1: Square wave (period = 8 samples)")
    square_data = fields_data[1]
    print(f"  Values at samples 0, 8, 16, 24, 32, 40: {[square_data[i] for i in [0, 8, 16, 24, 32, 40] if i < len(square_data)]}")
    print(f"  Should repeat every 8 samples")
    
    print("\nField 2: Triangle wave (period = 12 samples)")
    triangle_data = fields_data[2]
    print(f"  Values at samples 0, 12, 24, 36, 48: {[triangle_data[i] for i in [0, 12, 24, 36, 48] if i < len(triangle_data)]}")
    print(f"  Should repeat every 12 samples")
    
    print("\nField 3: Sawtooth wave (period = 6 samples)")
    sawtooth_data = fields_data[3]
    print(f"  Values at samples 0, 6, 12, 18, 24, 30, 36, 42, 48: {[sawtooth_data[i] for i in [0, 6, 12, 18, 24, 30, 36, 42, 48] if i < len(sawtooth_data)]}")
    print(f"  Should repeat every 6 samples")
    
    print("\nField 4: QRS complex (period = 24 samples)")
    qrs_data = fields_data[4]
    print(f"  Values at samples 0, 24, 48: {[qrs_data[i] for i in [0, 24, 48] if i < len(qrs_data)]}")
    print(f"  Should repeat every 24 samples")
    
    # Check for periodicity
    print("\n" + "="*60)
    print("PERIODICITY VERIFICATION:")
    print("="*60)
    
    # Check sine (period 10)
    if len(sine_data) >= 20:
        period_match = sine_data[0] == sine_data[10]
        print(f"Sine period check (sample 0 vs 10): {sine_data[0]} == {sine_data[10]} -> {period_match}")
    
    # Check square (period 8)
    if len(square_data) >= 16:
        period_match = square_data[0] == square_data[8]
        print(f"Square period check (sample 0 vs 8): {square_data[0]} == {square_data[8]} -> {period_match}")
    
    # Check triangle (period 12)
    if len(triangle_data) >= 24:
        period_match = triangle_data[0] == triangle_data[12]
        print(f"Triangle period check (sample 0 vs 12): {triangle_data[0]} == {triangle_data[12]} -> {period_match}")
    
    # Check sawtooth (period 6)
    if len(sawtooth_data) >= 12:
        period_match = sawtooth_data[0] == sawtooth_data[6]
        print(f"Sawtooth period check (sample 0 vs 6): {sawtooth_data[0]} == {sawtooth_data[6]} -> {period_match}")
    
    # Check QRS (period 24)
    if len(qrs_data) >= 48:
        period_match = qrs_data[0] == qrs_data[24]
        print(f"QRS period check (sample 0 vs 24): {qrs_data[0]} == {qrs_data[24]} -> {period_match}")


if __name__ == '__main__':
    verify_periods('test_periods_output.bin', 50, 5)
