# Device Simulator - Data Generation and Visualization

A comprehensive Python toolkit for generating binary test data and creating advanced visualizations of various function outputs including sine waves, square waves, triangular patterns, QRS complexes, and more. Also includes a device simulation system using UNIX sockets.

## 🚀 Features

### Data Generation and Visualization
- **Multiple Function Types**: sine, square, triangle, sawtooth, random, QRS complex patterns
- **Flexible Data Formats**: Support for 8, 16, and 32-bit data widths
- **Definition File Based**: Easy-to-use text-based configuration
- **Advanced Visualization**: Individual function plots with statistical analysis
- **Professional Output**: High-resolution PNG plots suitable for reports
- **Headless Compatible**: Works in server environments without display

### Device Simulation
- **UNIX Socket Communication**: Simulate device communication patterns
- **Configurable Timing**: Precise timing and repetition patterns
- **Multiple Data Sources**: Rotate through multiple data files
- **Immediate and Triggered Modes**: Flexible response patterns

### Supported Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `sine` | Sinusoidal wave | `<sine min_value max_value [period]>` |
| `square` | Square wave | `<square min_value max_value [period]>` |
| `triangle` | Triangle wave | `<triangle min_value max_value [period]>` |
| `sawtooth` | Sawtooth wave | `<sawtooth min_value max_value [period]>` |
| `random` | Random values | `<random min_value max_value>` |
| `qrs` | QRS ECG pattern | `<qrs q_val q_samples r_val r_period s_val s_samples [overall_period]>` |
| `checksum` | Sum of all other bytes | `<checksum>` |
| `inverse_checksum` | Negative sum of other bytes | `<inverse_checksum>` |

## 📦 Installation

### Prerequisites
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3-matplotlib python3-numpy python3-yaml

# Or using pip
pip3 install -r requirements.txt
```

### Clone Repository
```bash
git clone https://github.com/Makistos/devicesim.git
cd devicesim
```

## 🎯 Quick Start

### Data Generation and Plotting
```bash
# Run the complete demo
python3 simple_test_demo.py

# Generate separate message files (each sample in its own file)
python3 generate_test_data.py your_def.txt messages 100
# Creates: messages.1.bin, messages.2.bin, ..., messages.100.bin

# Create plots (Note: plotting tools work with single combined files)
python3 plot_functions.py your_def.txt output.bin 100 --output-dir plots

# Analyze data
python3 plot_test_data.py your_def.txt output.bin 100
```

### Device Simulation
```bash
# Start the device simulator
python3 simple_devicesim.py config_example.yaml

# In another terminal, test with client
python3 test_client.py
```

## 📋 Definition File Format

Create a text file defining your data structure:

```
# Comments start with #
0x55                           # Hexadecimal constant
100                            # Decimal constant
-50                            # Negative decimal
<random 0 255>                 # Random values 0-255
<sine -100 100 15>             # Sine wave -100 to 100 with period of 15 samples
<square 10 200 8>              # Square wave 10 to 200 with period of 8 samples
<triangle 0 150 20>            # Triangle wave 0-150 with period of 20 samples
<sawtooth 20 80 12>            # Sawtooth 20-80 with period of 12 samples
<qrs -100 2 1000 16 -150 2 24> # QRS complex with overall period of 24 samples
```

## � File Output Format

### Individual Message Files
The data generator creates **separate binary files for each sample**:
- Input: `python3 generate_test_data.py def.txt messages 100`
- Output: `messages.1.bin`, `messages.2.bin`, ..., `messages.100.bin`
- Each file contains one complete message with all defined fields
- File size = number_of_fields × bytes_per_field

### Binary File Structure
Each binary file contains the fields in definition order:
```
[Field1][Field2][Field3]...[FieldN]
```
- 8-bit mode: Each field = 1 byte
- 16-bit mode: Each field = 2 bytes (little-endian)
- 32-bit mode: Each field = 4 bytes (little-endian)

## �📁 Project Structure

### Data Generation and Visualization

| File | Description |
|------|-------------|
| `generate_test_data.py` | Generate binary test data with various function types |
| `plot_functions.py` | Create individual function visualizations |
| `plot_test_data.py` | Statistical analysis and comprehensive plotting |
| `simple_test_demo.py` | Complete demonstration workflow |
| `PLOTTING_README.md` | Detailed plotting documentation |
| `requirements.txt` | Python dependencies |

### Device Simulation Components

| File | Description |
|------|-------------|
| `simple_devicesim.py` | Main server script for socket communication |
| `config_example.yaml` | Main configuration file |
| `config_immediate.yaml` | Alternative immediate-start configuration |

### Test Clients

| File | Description |
|------|-------------|
| `test_complete.py` | Comprehensive test client |
| `test_immediate.py` | Test client for immediate start mode |
| `debug_client.py` | Debug client for troubleshooting |

### Example Data Files

| File | Description |
|------|-------------|
| `graph_def.txt` | Complex example with multiple function types |
| `test_def.txt` | Simple example for basic testing |
| `demo_def.txt` | Generated by demo script |

## 🛠️ Usage Examples

### Basic Data Generation Workflow
```bash
# Create definition file
echo "<sine -100 100>" > my_functions.txt
echo "<square 0 255>" >> my_functions.txt

# Generate binary data
python3 generate_test_data.py my_functions.txt data.bin 200

# Create visualizations
python3 plot_functions.py my_functions.txt data.bin 200 --output-dir plots

# View statistical analysis
python3 plot_test_data.py my_functions.txt data.bin 200
```

### Different Bit Widths
```bash
# Generate 16-bit data
python3 generate_test_data.py test.txt data16.bin 100 --bits 16
python3 plot_functions.py test.txt data16.bin 100 --bits 16

# Generate 32-bit data
python3 generate_test_data.py test.txt data32.bin 100 --bits 32
python3 plot_functions.py test.txt data32.bin 100 --bits 32
```

## 📊 Visualization Features

The plotting tools create professional visualizations with:

- **Individual Function Plots**: One plot per function type
- **Overview Plots**: Combined visualization of all functions
- **Statistical Analysis**: Mean, standard deviation, min/max values
- **Function Annotations**: Automatic marking of peaks, valleys, transitions
- **R-peak Detection**: For QRS complex patterns
- **High-Resolution Output**: PNG files suitable for reports

### Plot Types Generated
- `sine_function.png` - Sine wave with peak/valley markers
- `square_function.png` - Square wave with transition points
- `triangle_function.png` - Triangle wave patterns
- `sawtooth_function.png` - Sawtooth wave visualization
- `random_function.png` - Random value distribution
- `qrs_function.png` - QRS complex with R-peak detection
- `functions_overview.png` - Combined overview of all functions

## 🔧 Advanced Configuration

### Multi-bit Data Support
- **8-bit**: Standard byte values (-128 to 127)
- **16-bit**: Short integer values (-32768 to 32767)
- **32-bit**: Full integer values

### Customizable Parameters
- Sample counts and timing
- Function amplitude and frequency
- Statistical analysis depth
- Plot styling and output formats

## 🧪 Testing

### Available Test Scripts
```bash
# Run plotting demo
python3 simple_test_demo.py

# Test device simulation
python3 test_complete.py

# Debug connections
python3 debug_client.py
```

### Data Validation
- Automatic file size validation
- Data integrity checking
- Statistical significance testing
- Function pattern recognition

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🐛 Issues and Support

- Report bugs via [GitHub Issues](https://github.com/Makistos/devicesim/issues)
- Check [PLOTTING_README.md](PLOTTING_README.md) for detailed plotting documentation
- Review example files for usage patterns
- Test with the demo script first

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version History

- **v1.0.0** - Initial release
  - Comprehensive data generation with multiple function types
  - Advanced visualization and statistical analysis
  - Device simulation with UNIX socket communication
  - Professional plot output with annotations
  - MIT license and full documentation

---

**Keywords**: data-generation, visualization, matplotlib, signal-processing, testing, binary-data, python, plotting, statistical-analysis, device-simulation, unix-sockets