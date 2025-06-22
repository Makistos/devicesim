#!/usr/bin/env python3
"""
Test Data Generator

Generates binary test data files based on definition files.

Usage: python generate_test_data.py <definition_file> <output_file> <count> [--bits {8,16,32}]

Definition file format:
- 0x<hex>: Hexadecimal values written as-is
- <number>: Decimal numbers (can be negative) converted to hex
- <function param1 param2 ...>: Function calls (placeholder for future implementation)
- # comment: Lines starting with # are ignored

The script generates <count> data points and writes them to a binary file.
"""

import argparse
import re
import struct
import sys
from typing import List, Union, Any
import random
import math


class DataGenerator:
    def __init__(self, bits: int = 8):
        """Initialize data generator with specified bit width."""
        self.bits = bits
        self.byte_format = {8: 'B', 16: 'H', 32: 'I'}[bits]
        self.signed_format = {8: 'b', 16: 'h', 32: 'i'}[bits]
        self.max_value = (2 ** bits) - 1
        self.min_value = -(2 ** (bits - 1))
        self.max_unsigned = (2 ** bits) - 1

        # Function state for stateful functions
        self.function_state = {}
        self.sample_index = 0
        self.current_sample_data = []  # For checksum calculations

    def parse_definition_file(self, filepath: str) -> List[str]:
        """Parse definition file and return list of field definitions."""
        fields = []
        try:
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    fields.append(line)

            return fields
        except FileNotFoundError:
            print(f"Error: Definition file '{filepath}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading definition file: {e}")
            sys.exit(1)

    def parse_hex_value(self, value: str) -> int:
        """Parse hexadecimal value (0x...)."""
        try:
            return int(value, 16)
        except ValueError:
            print(f"Error: Invalid hex value '{value}'")
            sys.exit(1)

    def parse_decimal_value(self, value: str) -> int:
        """Parse decimal value (can be negative)."""
        try:
            num = int(value)
            # Handle negative values for signed integers
            if num < 0:
                if num < self.min_value:
                    print(f"Warning: Value {num} too small for {self.bits}-bit signed integer, clamping to {self.min_value}")
                    num = self.min_value
                # Convert to unsigned representation
                num = num & self.max_unsigned
            elif num > self.max_unsigned:
                print(f"Warning: Value {num} too large for {self.bits}-bit integer, clamping to {self.max_unsigned}")
                num = self.max_unsigned
            return num
        except ValueError:
            print(f"Error: Invalid decimal value '{value}'")
            sys.exit(1)

    def parse_function_call(self, func_call: str) -> int:
        """Parse and execute function call <function param1 param2 ...>."""
        # Remove < and > brackets
        func_call = func_call.strip('<>')
        parts = func_call.split()

        if not parts:
            print("Error: Empty function call")
            sys.exit(1)

        func_name = parts[0].lower()
        params = parts[1:]

        # Convert numeric parameters
        numeric_params = []
        for param in params:
            try:
                if '.' in param:
                    numeric_params.append(float(param))
                else:
                    numeric_params.append(int(param))
            except ValueError:
                # Keep as string for non-numeric parameters
                numeric_params.append(param)

        # Placeholder function implementations
        if func_name == 'random':
            if len(numeric_params) >= 2:
                min_val, max_val = numeric_params[0], numeric_params[1]
                value = random.randint(int(min_val), int(max_val))
            else:
                value = random.randint(0, self.max_unsigned)
            return self.clamp_value(value)

        elif func_name == 'sine':
            if len(numeric_params) >= 2:
                min_val, max_val = numeric_params[0], numeric_params[1]
                # Simple sine wave implementation
                amplitude = (max_val - min_val) / 2
                offset = (max_val + min_val) / 2
                frequency = 0.1  # Default frequency
                value = int(offset + amplitude * math.sin(self.sample_index * frequency))
            else:
                value = int(127 * math.sin(self.sample_index * 0.1))
            return self.clamp_value(value)

        elif func_name == 'square':
            if len(numeric_params) >= 2:
                min_val, max_val = numeric_params[0], numeric_params[1]
                period = 20  # Default period
                value = max_val if (self.sample_index // period) % 2 == 0 else min_val
            else:
                value = 255 if (self.sample_index // 20) % 2 == 0 else 0
            return self.clamp_value(value)

        elif func_name == 'triangle':
            if len(numeric_params) >= 2:
                min_val, max_val = numeric_params[0], numeric_params[1]
                period = 40  # Default period
                position = (self.sample_index % period) / period
                if position < 0.5:
                    value = int(min_val + (max_val - min_val) * (position * 2))
                else:
                    value = int(max_val - (max_val - min_val) * ((position - 0.5) * 2))
            else:
                period = 40
                position = (self.sample_index % period) / period
                value = int(100 * (1 - 2 * abs(position - 0.5)))
            return self.clamp_value(value)

        elif func_name == 'sawtooth':
            if len(numeric_params) >= 2:
                min_val, max_val = numeric_params[0], numeric_params[1]
                period = 30  # Default period
                position = (self.sample_index % period) / period
                value = int(min_val + (max_val - min_val) * position)
            else:
                value = self.sample_index % 100
            return self.clamp_value(value)

        elif func_name == 'qrs':
            # QRS Complex: <qrs q_value q_samples r_value r_period s_value s_samples>
            if len(numeric_params) >= 6:
                q_val, q_samples, r_val, r_period, s_val, s_samples = numeric_params[:6]

                # Check if we're in an R wave cycle
                cycle_pos = self.sample_index % int(r_period)

                if cycle_pos == 0:  # R wave peak
                    value = int(r_val)
                elif cycle_pos <= int(q_samples):  # Q wave (before R)
                    value = int(q_val)
                elif cycle_pos <= int(q_samples) + int(s_samples):  # S wave (after R)
                    value = int(s_val)
                else:  # Baseline
                    value = 0
            else:
                # Default QRS pattern
                cycle_pos = self.sample_index % 16
                if cycle_pos == 0:
                    value = 1000  # R wave
                elif cycle_pos <= 2:
                    value = -100  # Q wave
                elif cycle_pos <= 4:
                    value = -150  # S wave
                else:
                    value = 0     # Baseline
            return self.clamp_value(value)

        elif func_name == 'checksum':
            # Simple checksum: sum of all other bytes in current sample
            if hasattr(self, 'current_sample_data') and self.current_sample_data:
                checksum = sum(self.current_sample_data) & self.max_unsigned
                return self.clamp_value(checksum)
            else:
                return 0

        elif func_name == 'inverse_checksum':
            # Inverse checksum: negative of sum of all other bytes in current sample
            if hasattr(self, 'current_sample_data') and self.current_sample_data:
                checksum = sum(self.current_sample_data)
                inverse_checksum = -checksum
                return self.clamp_value(inverse_checksum)
            else:
                return 0

        elif func_name == 'crc':
            # Placeholder for CRC implementation
            print(f"Warning: Function '{func_name}' not yet implemented, returning 0")
            return 0

        else:
            print(f"Warning: Unknown function '{func_name}', returning 0")
            return 0

    def clamp_value(self, value: int) -> int:
        """Clamp value to valid range for the specified bit width."""
        if value < 0:
            # Handle negative values for signed representation
            if value < self.min_value:
                value = self.min_value
            value = value & self.max_unsigned
        elif value > self.max_unsigned:
            value = self.max_unsigned
        return value

    def process_field(self, field: str) -> int:
        """Process a single field definition and return the value."""
        field = field.strip()

        # Hexadecimal value
        if field.startswith('0x') or field.startswith('0X'):
            return self.parse_hex_value(field)

        # Function call
        elif field.startswith('<') and field.endswith('>'):
            return self.parse_function_call(field)

        # Decimal number
        elif field.lstrip('-').isdigit():
            return self.parse_decimal_value(field)

        else:
            print(f"Error: Unrecognized field format: '{field}'")
            sys.exit(1)

    def generate_data(self, definition_file: str, output_file: str, count: int):
        """Generate test data based on definition file."""
        fields = self.parse_definition_file(definition_file)

        if not fields:
            print("Error: No valid fields found in definition file")
            sys.exit(1)

        print(f"Generating {count} data points with {self.bits}-bit values...")
        print(f"Fields found: {len(fields)}")

        # Identify checksum fields that need special handling
        checksum_fields = []
        regular_fields = []
        for i, field in enumerate(fields):
            if field.startswith('<') and field.endswith('>'):
                func_call = field.strip('<>')
                func_name = func_call.split()[0] if func_call.split() else ''
                if func_name in ['checksum', 'inverse_checksum']:
                    checksum_fields.append((i, field))
                else:
                    regular_fields.append((i, field))
            else:
                regular_fields.append((i, field))

        try:
            with open(output_file, 'wb') as f:
                for i in range(count):
                    self.sample_index = i
                    sample_values = [0] * len(fields)  # Initialize sample array
                    
                    # First pass: process all non-checksum fields
                    for field_idx, field in regular_fields:
                        value = self.process_field(field)
                        sample_values[field_idx] = value
                    
                    # Second pass: process checksum fields with access to other field data
                    self.current_sample_data = [sample_values[idx] for idx, _ in regular_fields]
                    for field_idx, field in checksum_fields:
                        value = self.process_field(field)
                        sample_values[field_idx] = value
                    
                    # Write all values in original field order
                    for value in sample_values:
                        # Pack value according to bit width
                        if value < 0:
                            # Use signed format for negative values
                            packed = struct.pack(f'<{self.signed_format}', value)
                        else:
                            # Use unsigned format for positive values
                            packed = struct.pack(f'<{self.byte_format}', value)

                        f.write(packed)

                    # Progress indicator
                    if (i + 1) % 100 == 0 or i == count - 1:
                        print(f"Generated {i + 1}/{count} samples...")

        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)

        print(f"Successfully generated {output_file}")

        # Print file size info
        file_size = count * len(fields) * (self.bits // 8)
        print(f"File size: {file_size} bytes ({count} samples × {len(fields)} fields × {self.bits//8} bytes)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate binary test data from definition files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_test_data.py graph_def.txt output.bin 1000
  python generate_test_data.py graph_def.txt output.bin 1000 --bits 16

Definition file format:
  0x80              # Hex value
  42                # Decimal value
  -100              # Negative decimal
  <random 0 100>    # Function call
  # comment         # Ignored
        """
    )

    parser.add_argument('definition_file', help='Input definition file')
    parser.add_argument('output_file', help='Output binary file')
    parser.add_argument('count', type=int, help='Number of data points to generate')
    parser.add_argument('--bits', choices=['8', '16', '32'], default='8',
                        help='Bit width for values (default: 8)')

    args = parser.parse_args()

    if args.count <= 0:
        print("Error: Count must be positive")
        sys.exit(1)

    generator = DataGenerator(bits=int(args.bits))
    generator.generate_data(args.definition_file, args.output_file, args.count)


if __name__ == "__main__":
    main()
