#!/usr/bin/env python3
"""
Detailed Period Parameter Verification Script

This script creates test data with specific period parameters and verifies
that the waveform functions are generating the expected frequencies.
"""

import struct
import os

def create_period_test_file():
    """Create a comprehensive test definition file for period verification."""
    test_def = """# Comprehensive period parameter test
# Testing different periods for all waveform functions

# Sine wave tests
<sine 0 100 4>
<sine 0 100 8>
<sine 0 100 16>

# Square wave tests
<square 0 100 6>
<square 0 100 12>

# Triangle wave tests
<triangle 0 100 5>
<triangle 0 100 10>

# Sawtooth wave tests
<sawtooth 0 100 3>
<sawtooth 0 100 9>

# QRS with different overall periods
<qrs 10 1 50 4 20 1 8>
<qrs 10 1 50 4 20 1 16>
"""

    with open('period_verification_def.txt', 'w') as f:
        f.write(test_def)

    return 'period_verification_def.txt'

def read_binary_data(filename, num_samples, num_fields, bits=8):
    """Read binary data from file."""
    if bits == 8:
        format_char = 'B'
        bytes_per_value = 1
    elif bits == 16:
        format_char = 'H'
        bytes_per_value = 2
    elif bits == 32:
        format_char = 'I'
        bytes_per_value = 4
    else:
        raise ValueError(f"Unsupported bit width: {bits}")

    data = []
    try:
        with open(filename, 'rb') as f:
            for sample in range(num_samples):
                sample_data = []
                for field in range(num_fields):
                    raw_bytes = f.read(bytes_per_value)
                    if len(raw_bytes) < bytes_per_value:
                        break
                    value = struct.unpack(f'<{format_char}', raw_bytes)[0]
                    sample_data.append(value)
                if len(sample_data) == num_fields:
                    data.append(sample_data)
                else:
                    break
        return data
    except FileNotFoundError:
        print(f"Error: Binary file '{filename}' not found.")
        return []

def verify_period(data_column, expected_period, field_name):
    """Verify that a data column has approximately the expected period."""
    if len(data_column) < expected_period * 2:
        print(f"  {field_name}: Not enough data to verify period {expected_period}")
        return False

    # For periodic functions, check if the pattern repeats
    pattern_matches = 0
    total_checks = 0

    for i in range(expected_period, len(data_column)):
        if abs(data_column[i] - data_column[i - expected_period]) <= 1:  # Allow small tolerance
            pattern_matches += 1
        total_checks += 1

    if total_checks == 0:
        print(f"  {field_name}: Cannot verify period {expected_period}")
        return False

    match_percentage = (pattern_matches / total_checks) * 100
    print(f"  {field_name}: Period {expected_period} - {match_percentage:.1f}% pattern match")

    # Consider it verified if at least 80% of values match the expected period
    return match_percentage >= 80.0

def main():
    print("Period Parameter Verification")
    print("=" * 40)

    # Create test definition file
    def_file = create_period_test_file()
    print(f"Created test definition file: {def_file}")

    # Generate test data
    bin_file = 'period_verification.bin'
    num_samples = 48  # Multiple of common periods for good verification

    print(f"\nGenerating {num_samples} samples...")
    os.system(f'python3 generate_test_data.py {def_file} {bin_file} {num_samples}')

    # Read and analyze the data
    print("\nReading and analyzing data...")
    data = read_binary_data(bin_file, num_samples, 11)  # 11 fields in our test

    if not data:
        print("Failed to read binary data!")
        return

    # Transpose data to get columns for each field
    columns = list(zip(*data))

    # Expected periods for each field
    field_info = [
        ("Sine (period 4)", 4),
        ("Sine (period 8)", 8),
        ("Sine (period 16)", 16),
        ("Square (period 6)", 6),
        ("Square (period 12)", 12),
        ("Triangle (period 5)", 5),
        ("Triangle (period 10)", 10),
        ("Sawtooth (period 3)", 3),
        ("Sawtooth (period 9)", 9),
        ("QRS (period 8)", 8),
        ("QRS (period 16)", 16)
    ]

    print("\nPeriod Verification Results:")
    print("-" * 40)

    all_verified = True
    for i, (field_name, expected_period) in enumerate(field_info):
        if i < len(columns):
            verified = verify_period(columns[i], expected_period, field_name)
            if not verified:
                all_verified = False
        else:
            print(f"  {field_name}: No data available")
            all_verified = False

    print("-" * 40)
    if all_verified:
        print("✅ All period parameters verified successfully!")
    else:
        print("❌ Some period parameters may not be working as expected.")

    # Show a sample of the data for manual inspection
    print(f"\nFirst 10 samples (showing first 6 fields):")
    print("Sample | Sine4 | Sine8 | Sine16| Sqr6  | Sqr12 | Tri5")
    print("-" * 55)
    for i in range(min(10, len(data))):
        values = data[i][:6]  # Show first 6 fields
        print(f"{i:6d} | {' | '.join(f'{v:5d}' for v in values)}")

    # Clean up
    os.remove(def_file)
    print(f"\nTest files created: {bin_file}")
    print("You can plot this data with:")
    print(f"python3 plot_functions.py {def_file} {bin_file} {num_samples}")

if __name__ == "__main__":
    main()
