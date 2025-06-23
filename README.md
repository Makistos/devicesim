# Device Simulator - Data Generation and Visualization

A comprehensive Python toolkit for generati## 📄 File Output Format

### Individual Message Files
The data generator creates **separate binary files for each sample**:
- Input: `python3 generate_test_data.py def.txt messages 100`
- Output: `messages.1.bin`, `messages.2.bin`, ..., `messages.100.bin`
- Each file contains one complete message with all defined fields
- File size = number_of_fields × bytes_per_field

### Directory Structure Support
Supports automatic directory creation for organized output:
```bash
# Creates output/batch1/ directory automatically
python3 generate_test_data.py def.txt output/batch1/data 50

# Creates nested directories as needed
python3 generate_test_data.py def.txt experiments/2025/june/test 25
```

### Binary File Structure
Each binary file contains the fields in definition order:est data and creating advanced visualizations of various function outputs including sine waves, square waves, triangular patterns, QRS complexes, and more. Also includes a device simulation system using UNIX sockets.

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
| `sine` | Sinusoidal wave | `<sine min_value max_value [period] [noise_level]>` |
| `square` | Square wave | `<square min_value max_value [period] [noise_level]>` |
| `triangle` | Triangle wave | `<triangle min_value max_value [period] [noise_level]>` |
| `sawtooth` | Sawtooth wave | `<sawtooth min_value max_value [period] [noise_level]>` |
| `random` | Random values | `<random min_value max_value>` |
| `qrs` | QRS ECG pattern | `<qrs q_val q_samples r_val r_period s_val s_samples [overall_period] [noise_level]>` |
| `checksum` | Sum of all other bytes | `<checksum>` |
| `inverse_checksum` | Negative sum of other bytes | `<inverse_checksum>` |

**Noise Parameter**: Optional parameter (0-100) where 0=no noise, 100=completely random

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

# Generate files with directory structure (auto-creates directories)
python3 generate_test_data.py def.txt output/test_batch/data 50
# Creates: output/test_batch/data.1.bin, ..., output/test_batch/data.50.bin

# Create plots (Note: plotting tools work with single combined files)
python3 plot_functions.py your_def.txt output.bin 100 --output-dir plots

# Analyze data
python3 plot_test_data.py your_def.txt output.bin 100
```

### Device Simulation
```bash
# Start the device simulator
python3 simple_devicesim.py config_example.yaml

# In another terminal, test with debug client
python3 debug_client.py
```

## 🔧 Device Simulator

The device simulator creates a UNIX socket server that simulates device communication patterns. It reads binary data files and sends them according to configurable timing and trigger patterns.

### Key Features
- **UNIX Socket Communication**: Uses `/tmp/test_socket.sock` for inter-process communication
- **YAML Configuration**: Flexible rule-based message sending
- **File Pattern Matching**: Supports regex patterns for dynamic file selection
- **Timing Control**: Configurable delays between messages
- **Repeat Patterns**: Control message repetition (finite or infinite)
- **Trigger-Based**: Can wait for client triggers or start immediately

### Simulator Workflow
1. **Startup**: Reads YAML configuration and creates socket
2. **Client Connection**: Waits for client to connect
3. **Trigger Handling**: Optionally waits for trigger messages
4. **Message Dispatch**: Sends binary files according to configuration rules
5. **File Rotation**: Cycles through matching files for continuous operation

## 📝 YAML Configuration Format

The simulator uses YAML files to define communication behavior:

### Basic Structure
```yaml
Messages:                    # List of messages to send
  - file name: pattern       # File pattern (regex supported)
    delay: 0                 # Delay in milliseconds before sending
    repeat: 1                # Repeat count (0 = infinite)
    waitCount: 0             # Optional: wait for this many incoming messages (default: 0)
```

### Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `file name` | String | File pattern (supports regex)<br>Example: `start\.1\.bin` or `graph\..*\.bin` |
| `delay` | Integer | Delay in milliseconds before sending |
| `repeat` | Integer | Repeat behavior:<br>`> 0` = send N times<br>`0` = infinite repeat<br>`< 0` = request-response mode (wait for abs(N) client messages between sends) |
| `waitCount` | Integer | *(Optional)* Wait for this many incoming messages before sending<br>`0` = send immediately (default) |

### Repeat Parameter Behavior

The `repeat` parameter controls how messages are sent and supports three distinct modes:

#### Positive Values (`repeat > 0`)
- **Behavior**: Send the message exactly N times
- **Timing**: Uses `delay` parameter between sends
- **Example**: `repeat: 3` sends the message 3 times then stops

#### Zero Value (`repeat: 0`) 
- **Behavior**: Send the message continuously (infinite loop)
- **Timing**: Uses `delay` parameter between sends
- **Example**: `repeat: 0` sends the message forever with specified delay
- **Note**: Suitable for continuous data streaming

#### Negative Values (`repeat < 0`) - Request-Response Mode
- **Behavior**: Creates a request-response pattern
- **Process**: 
  1. Send message immediately (respecting `waitCount` if specified)
  2. Wait for abs(repeat) client messages
  3. Send message again
  4. Repeat steps 2-3 indefinitely
- **Example**: `repeat: -2` means wait for 2 client messages between each send
- **Use Cases**: Interactive protocols, acknowledgment-based communication

#### Combining with waitCount
- **waitCount + positive repeat**: Wait for trigger, then send N times
- **waitCount + zero repeat**: Wait for trigger, then send continuously  
- **waitCount + negative repeat**: Wait for trigger, send once, then enter request-response mode

### Example Configurations

#### Simple Immediate Mode
```yaml
Messages:
  - file name: start\.1\.bin    # Send immediately on connection
    delay: 0
    repeat: 1
  - file name: graph\..*\.bin   # Send all graph files continuously
    delay: 16                   # 16ms between files
    repeat: 0                   # Infinite repeat
```

#### Triggered Response Mode
```yaml
Messages:
  - file name: start\.1\.bin    # Send after 1st incoming message
    delay: 0
    repeat: 1
    waitCount: 1
  - file name: start\.2\.bin    # Send after 2nd incoming message
    delay: 0
    repeat: 1
    waitCount: 2
  - file name: graph\..*\.bin   # Send after 5th incoming message
    delay: 16                   # Then repeat continuously
    repeat: 0
    waitCount: 5
  - file name: numeric\..*\.bin # Also send after 5th message
    delay: 50                   # Different timing
    repeat: 0
    waitCount: 5
```

#### Request-Response Mode
```yaml
Messages:
  - file name: start\.1\.bin    # Send immediately, then wait for 1 client message
    delay: 0                    # before each subsequent send
    repeat: -1                  # Request-response: wait for 1 client message
    waitCount: 0                # Start immediately
  - file name: start\.2\.bin    # Send after 2nd client message, then wait for
    delay: 100                  # 2 client messages between each send
    repeat: -2                  # Request-response: wait for 2 client messages
    waitCount: 2                # Start after 2nd client message
```

### File Pattern Matching

The simulator supports regex patterns for flexible file selection:

| Pattern | Matches | Example |
|---------|---------|---------|
| `start\.1\.bin` | Exact file | `start.1.bin` |
| `graph\..*\.bin` | All graph files | `graph.1.bin`, `graph.2.bin`, etc. |
| `data_.*\.bin` | Pattern prefix | `data_test.bin`, `data_demo.bin` |
| `.*\.bin` | All binary files | Any `.bin` file |

### Communication Protocol

1. **Client Connection**: Client connects to `/tmp/test_socket.sock`
2. **Message Processing**: For each message definition:
   - If `waitCount > 0`: Wait for that many incoming client messages
   - If `waitCount = 0` (or omitted): Send immediately after connection
3. **File Transmission**: Send matching files with specified `delay` and `repeat` settings
4. **File Rotation**: For `repeat: 0`, cycles through matching files infinitely
5. **Timing**: Respects `delay` parameters between transmissions

### Usage Examples

```bash
# Create test data files
python3 generate_test_data.py my_def.txt start 5
python3 generate_test_data.py graph_def.txt graph 10
python3 generate_test_data.py numeric_def.txt numeric 8

# Start simulator with triggered mode
python3 simple_devicesim.py config_example.yaml

# Test with debug client (sends trigger and receives data)
python3 debug_client.py
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
<sine -100 100 15 25>          # Same sine wave with 25% uniform noise
<square 10 200 8>              # Square wave 10 to 200 with period of 8 samples
<square 10 200 8 50>           # Same square wave with 50% noise
<triangle 0 150 20>            # Triangle wave 0-150 with period of 20 samples
<triangle 0 150 20 30>         # Triangle wave with 30% noise
<sawtooth 20 80 12>            # Sawtooth 20-80 with period of 12 samples
<sawtooth 20 80 12 40>         # Sawtooth with 40% noise
<qrs -100 2 1000 16 -150 2 24> # QRS complex with overall period of 24 samples
<qrs -100 2 1000 16 -150 2 24 20> # QRS complex with 20% noise
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
| `combine_files.py` | Utility to combine numbered files for plotting |
| `PLOTTING_README.md` | Detailed plotting documentation |
| `requirements.txt` | Python dependencies |

### Device Simulation Components

| File | Description |
|------|-------------|
| `simple_devicesim.py` | UNIX socket server for device simulation |
| `config_example.yaml` | Triggered response configuration example |
| `config_immediate.yaml` | Immediate start configuration example |
| `debug_client.py` | Debug client for simulator testing |

### Example Data Files

| File | Description |
|------|-------------|
| `graph_def.txt` | Complex example with multiple function types |
| `test_def.txt` | Simple example for basic testing |
| `demo_def.txt` | Generated by demo script |
| `noise_test_def.txt` | Comprehensive noise parameter testing |
| `simple_noise_test.txt` | Simple noise demonstration |
| `period_demo_def.txt` | Period parameter demonstration |

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