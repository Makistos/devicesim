#!/usr/bin/env python3
"""
Simple Test Script for Function Plotting

This script demonstrates how to:
1. Generate test data with different function types
2. Read and plot the generated binary data
3. Analyze function outputs

Usage: python simple_test_demo.py
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and show progress."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ Success!")
        if result.stdout:
            print(result.stdout)
    else:
        print("✗ Error!")
        if result.stderr:
            print(result.stderr)
        return False
    return True


def create_demo_definition():
    """Create a simple demonstration definition file."""
    demo_def = """# Demo definition file - Various function types
0x55
100
-50
<random 0 255>
<sine -100 100>
<square 10 200>
<triangle 0 150>
<sawtooth 20 80>
"""

    with open('demo_def.txt', 'w') as f:
        f.write(demo_def)

    print("Created demo_def.txt with the following functions:")
    print("- Constant hex value (0x55)")
    print("- Constant decimal values (100, -50)")
    print("- Random values (0 to 255)")
    print("- Sine wave (-100 to 100)")
    print("- Square wave (10 to 200)")
    print("- Triangle wave (0 to 150)")
    print("- Sawtooth wave (20 to 80)")


def main():
    print("Function Plotting Demo")
    print("=" * 60)

    # Step 1: Create demo definition file
    print("\n1. Creating demonstration definition file...")
    create_demo_definition()

    # Step 2: Generate test data
    if not run_command([
        '/bin/python3', 'generate_test_data.py',
        'demo_def.txt', 'demo_output.bin', '200'
    ], "Generate 200 samples of test data"):
        return

    # Step 3: Create function plots
    if not run_command([
        '/bin/python3', 'plot_functions.py',
        'demo_def.txt', 'demo_output.bin', '200',
        '--output-dir', 'demo_plots'
    ], "Generate function plots"):
        return

    # Step 4: Run analysis with existing plot script
    if not run_command([
        '/bin/python3', 'plot_test_data.py',
        'demo_def.txt', 'demo_output.bin', '200'
    ], "Run detailed data analysis"):
        return

    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("- demo_def.txt        : Definition file with various functions")
    print("- demo_output.bin     : Binary data file (200 samples)")
    print("- demo_plots/         : Directory with individual function plots")
    print("  - functions_overview.png : Overview of all functions")
    print("  - sine_function.png      : Sine wave plot")
    print("  - square_function.png    : Square wave plot")
    print("  - triangle_function.png  : Triangle wave plot")
    print("  - sawtooth_function.png  : Sawtooth wave plot")
    print("  - random_function.png    : Random values plot")
    print("\nYou can view the PNG files to see the plotted functions!")


if __name__ == '__main__':
    main()
