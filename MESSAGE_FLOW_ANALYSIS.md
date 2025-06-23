# Message Flow Analysis: config_request_response.yaml

## Configuration Summary
```yaml
Messages:
  - file name: start\.1\.bin    # repeat: -1, waitCount: 0
  - file name: start\.2\.bin    # repeat: -2, waitCount: 2
  - file name: start\.3\.bin    # repeat: 3,  waitCount: 1
```

## Detailed Message Flow

### Timeline of Events

```
TIME    CLIENT              SIMULATOR           DESCRIPTION
====    ======              =========           ===========

T1      [connects]          →                   Client connects to simulator

T2                          → start.1.bin      IMMEDIATE: waitCount=0, first send
                                               (repeat: -1 pattern starts)

T3      "ack_for_start1" →                     Client sends 1st message
                            → start.1.bin      RESPONSE: repeat=-1 (need 1 client msg)
                            → start.3.bin×3    TRIGGERED: waitCount=1 satisfied
                                               (sends 3 times, then stops)

T4      "trigger_start2" →                     Client sends 2nd message
                            → start.2.bin      TRIGGERED: waitCount=2 satisfied
                                               (repeat: -2 pattern starts)

T5      "ack1_for_start2" →                    Client sends 3rd message
T6      "ack2_for_start2" →                    Client sends 4th message
                            → start.2.bin      RESPONSE: repeat=-2 (needed 2 client msgs)

T7      "another_ack1" →                       Client sends 5th message
                            → start.1.bin      RESPONSE: repeat=-1 (need 1 client msg)
```

## Pattern Behavior Analysis

### 🔄 start.1.bin (repeat: -1, waitCount: 0)
- **Initial**: Sends immediately when client connects
- **Ongoing**: For each client message received → sends start.1.bin
- **Pattern**: 1:1 request-response ratio
- **Status**: Continues indefinitely

### 🔄 start.2.bin (repeat: -2, waitCount: 2)
- **Initial**: Waits for 2nd client message, then sends once
- **Ongoing**: For every 2 client messages received → sends start.2.bin
- **Pattern**: 2:1 request-response ratio
- **Status**: Continues indefinitely

### ✅ start.3.bin (repeat: 3, waitCount: 1)
- **Initial**: Waits for 1st client message
- **Behavior**: Sends exactly 3 times, then stops
- **Pattern**: Traditional finite repeat
- **Status**: Completed after 3 sends

## Message Count Summary

| Message Type | Total Sent | Trigger Condition | Status |
|-------------|------------|-------------------|--------|
| start.1.bin | 3 times    | Every 1 client msg | Ongoing |
| start.2.bin | 2 times    | Every 2 client msgs | Ongoing |
| start.3.bin | 3 times    | After 1st client msg | Completed |

## Client Message Requirements

```
Client Message #1: "ack_for_start1"
├── Triggers: start.1.bin response (repeat: -1)
└── Triggers: start.3.bin×3 (waitCount: 1)

Client Message #2: "trigger_start2"
├── Triggers: start.2.bin initial (waitCount: 2)
└── Counts toward start.2.bin repeat: -2 pattern

Client Message #3: "ack1_for_start2"
└── 1/2 messages needed for next start.2.bin

Client Message #4: "ack2_for_start2"
├── 2/2 messages needed for next start.2.bin
└── Triggers: start.2.bin response

Client Message #5: "another_ack1"
└── Triggers: start.1.bin response (repeat: -1)
```

## Key Insights

1. **Multiple Patterns Coexist**: All three repeat behaviors run simultaneously
2. **Request-Response Persistence**: Negative repeat patterns continue indefinitely
3. **Flexible Ratios**: Different request:response ratios (1:1, 2:1) possible
4. **Mixed Triggers**: waitCount and repeat work together seamlessly
5. **Real-time Interaction**: Simulator responds to client messages in real-time

## Use Cases

- **Device Testing**: Simulate devices that require acknowledgments
- **Flow Control**: Prevent message flooding with controlled responses
- **Protocol Simulation**: Model complex request-response protocols
- **Interactive Systems**: Create responsive communication patterns
