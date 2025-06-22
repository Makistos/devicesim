#!/usr/bin/env python3
"""
Combine Individual Binary Files

Combines numbered binary files (file.1.bin, file.2.bin, ...) into a single file
for use with plotting tools that expect all samples in one file.
"""

import argparse
import os
import sys

def combine_files(base_filename, count, output_file):
    """Combine numbered binary files into a single file."""

    # Extract base filename (remove .bin extension if present)
    if base_filename.endswith('.bin'):
        base_filename = base_filename[:-4]

    combined_data = bytearray()
    files_found = 0

    try:
        for i in range(1, count + 1):
            input_file = f"{base_filename}.{i}.bin"

            if os.path.exists(input_file):
                with open(input_file, 'rb') as f:
                    data = f.read()
                    combined_data.extend(data)
                    files_found += 1
            else:
                print(f"Warning: File {input_file} not found")

        if files_found == 0:
            print("Error: No input files found")
            return False

        with open(output_file, 'wb') as f:
            f.write(combined_data)

        print(f"Combined {files_found} files into {output_file}")
        print(f"Total size: {len(combined_data)} bytes")
        return True

    except Exception as e:
        print(f"Error combining files: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Combine numbered binary files into a single file")
    parser.add_argument('base_filename', help='Base filename (without .1.bin suffix)')
    parser.add_argument('count', type=int, help='Number of files to combine')
    parser.add_argument('output_file', help='Output combined file')

    args = parser.parse_args()

    if not combine_files(args.base_filename, args.count, args.output_file):
        sys.exit(1)

if __name__ == "__main__":
    main()
