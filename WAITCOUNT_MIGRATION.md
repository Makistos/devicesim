# waitCount Migration Summary

## What Changed

The device simulator has been simplified to use a **per-message waitCount parameter** instead of the global `WaitToStart` and `ReceiveCount` fields.

### Old Format (DEPRECATED)
```yaml
WaitToStart: Yes
ReceiveCount: 5

Replies:
  - reply_number: 1
    Messages:
      - file name: start\.1\.bin
        delay: 0
        repeat: 1
  - reply_number: 2
    Messages:
      - file name: start\.2\.bin
        delay: 0
        repeat: 1
```

### New Format (CURRENT)
```yaml
Messages:
  - file name: start\.1\.bin
    delay: 0
    repeat: 1
    waitCount: 1        # Send after 1st client message
  - file name: start\.2\.bin
    delay: 0
    repeat: 1
    waitCount: 2        # Send after 2nd client message
```

## waitCount Parameter

- **waitCount: 0** (or omitted) = Send immediately when client connects
- **waitCount: N** (N > 0) = Wait for N client messages before sending

## Benefits

1. **Simpler Configuration**: One flat Messages array instead of nested Replies
2. **Granular Control**: Each message can have its own trigger condition
3. **More Flexible**: Multiple messages can be triggered by the same waitCount
4. **Easier to Understand**: Clear semantic meaning of when messages are sent

## Migration Guide

### For Immediate Sending
Old:
```yaml
WaitToStart: No
```
New:
```yaml
Messages:
  - file name: myfile.bin
    waitCount: 0    # or omit waitCount entirely
```

### For Triggered Sending
Old:
```yaml
WaitToStart: Yes
ReceiveCount: 3
Replies:
  - reply_number: 1
    Messages: [...]
  - reply_number: 2
    Messages: [...]
  - reply_number: 3
    Messages: [...]
```
New:
```yaml
Messages:
  - file name: file1.bin
    waitCount: 1
  - file name: file2.bin
    waitCount: 2
  - file name: file3.bin
    waitCount: 3
```

## New Feature: Negative Repeat Values (Request-Response Mode)

In addition to the waitCount parameter, the simulator now supports **negative repeat values** for request-response communication patterns.

### Negative Repeat Behavior
```yaml
Messages:
  - file name: data\.bin
    repeat: -2          # Wait for 2 client messages between each send
    waitCount: 1        # Start after 1st client message
```

**How it works:**
1. **Initial Send**: Message is sent after `waitCount` condition is met
2. **Wait Phase**: Simulator waits for abs(repeat) client messages
3. **Response Phase**: Message is sent again
4. **Repeat**: Steps 2-3 continue indefinitely

### Repeat Parameter Summary
- **`repeat > 0`**: Send N times then stop
- **`repeat = 0`**: Send continuously with delay
- **`repeat < 0`**: Request-response mode (wait for abs(N) client messages between sends)

### Use Cases for Negative Repeat
- **Interactive Protocols**: Client must acknowledge each message
- **Flow Control**: Prevent message flooding
- **Handshake Patterns**: Synchronized communication
- **Testing**: Simulate real device acknowledgment requirements

## Updated Configuration Files

- `config_simple.yaml` - Immediate mode (waitCount: 0)
- `config_triggered.yaml` - Triggered mode (various waitCount values)
- `config_request_response.yaml` - Request-response mode (negative repeat values)
- `config_example.yaml` - Updated to use waitCount format
- `config_immediate.yaml` - Updated to use waitCount format

## Testing and Analysis

Run the demos and analyzers to see the new functionality:
```bash
# Basic waitCount functionality test
python3 test_waitcount.py

# Request-response functionality test (negative repeat)
python3 test_request_response.py

# Comprehensive test of all modes
python3 test_comprehensive.py

# Analyze message flow for any configuration
python3 analyze_message_flow.py config_simple.yaml
python3 analyze_message_flow.py config_request_response.yaml 8
python3 analyze_message_flow.py config_triggered.yaml 12

# Interactive demos
python3 demo_waitcount.py
python3 debug_client_new.py
```

## Message Flow Analyzer

The `analyze_message_flow.py` tool provides detailed analysis of simulator behavior for any YAML configuration:

### Features
- **Automatic Configuration Analysis**: Parses any YAML config and explains behavior
- **Real-time Message Tracking**: Shows exact message exchanges with timestamps
- **Pattern Recognition**: Identifies immediate, triggered, and request-response patterns
- **Comprehensive Reporting**: Provides timeline and pattern analysis
- **Generic Support**: Works with any valid simulator configuration

### Usage
```bash
# Basic analysis (default: 10 client messages)
python3 analyze_message_flow.py <config.yaml>

# Extended analysis with custom message count
python3 analyze_message_flow.py <config.yaml> <max_client_messages>

# Examples
python3 analyze_message_flow.py config_simple.yaml
python3 analyze_message_flow.py config_request_response.yaml 15
python3 analyze_message_flow.py config_triggered.yaml 8
```

### Output Includes
- Configuration parameter breakdown
- Expected trigger conditions and behaviors
- Real-time message timeline with timestamps
- Pattern analysis and recommendations
- Complete message flow summary

This tool is essential for understanding complex configurations and debugging communication patterns.

## Backward Compatibility

The load_config() function still supports the old format but will issue deprecation warnings. Update your configurations to the new format for best results.
