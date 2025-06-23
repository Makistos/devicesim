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

## Updated Configuration Files

- `config_simple.yaml` - Immediate mode (waitCount: 0)
- `config_triggered.yaml` - Triggered mode (various waitCount values)
- `config_example.yaml` - Updated to use waitCount format
- `config_immediate.yaml` - Updated to use waitCount format

## Testing

Run the demos to see the new functionality:
```bash
# Basic functionality test
python3 test_waitcount.py

# Comprehensive demonstration
python3 demo_waitcount.py

# Updated debug client
python3 debug_client_new.py
```

## Backward Compatibility

The load_config() function still supports the old format but will issue deprecation warnings. Update your configurations to the new format for best results.
