#!/usr/bin/env python3
"""
Comprehensive test client for the reply-based device simulator
Tests the complete sequence as defined in config_example.yaml
"""

import socket
import sys
import time


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_complete.py <socket_file>")
        sys.exit(1)

    socket_file = sys.argv[1]
    client_socket = None

    try:
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(socket_file)
        print(f"Connected to {socket_file}")

        # Send initial trigger to start the simulator (WaitToStart: Yes)
        client_socket.send(b"initial_trigger")
        print("Sent initial trigger message")
        time.sleep(0.5)  # Give it time to process

        # Based on config_example.yaml, we have 5 replies for ReceiveCount: 5
        # Then reply 6 starts continuous sending
        test_messages = [
            ("message_1", "Reply 1: start.1.bin (single send)"),
            ("message_2", "Reply 2: start.2.bin (single send)"),
            ("message_3", "Reply 3: start.3.bin (single send)"),
            ("message_4", "Reply 4: start.4.bin (single send)"),
            ("message_5", "Reply 5: start.5.bin (single send)"),
        ]

        start_time = time.time()

        # Phase 1: Send the 5 messages that trigger specific replies
        for i, (message, description) in enumerate(test_messages, 1):
            print(f"\n--- Test {i}: {description} ---")

            # Send the message
            client_socket.send(message.encode())
            print(f"Sent: {message}")

            # Wait for the response (should be immediate based on delay: 0)
            message_count = 0
            collect_start = time.time()
            collect_time = 0.5  # Give enough time for response

            while time.time() - collect_start < collect_time:
                try:
                    client_socket.settimeout(0.1)
                    data = client_socket.recv(4096)
                    if data:
                        elapsed = int((time.time() - start_time) * 1000)
                        message_count += 1
                        # Try to decode as text, but show hex if binary
                        try:
                            content = data.decode('utf-8', errors='strict')
                            print(f"  [{elapsed:5d}ms] #{message_count}: "
                                  f"{len(data):2d} bytes: {content}")
                        except UnicodeDecodeError:
                            print(f"  [{elapsed:5d}ms] #{message_count}: "
                                  f"{len(data):2d} bytes: [binary data: {data[:20].hex()}...]")
                        break  # Got the response, move to next message
                except socket.timeout:
                    continue
                except (OSError, ConnectionError):
                    print("Connection error during receive")
                    break

            if message_count == 0:
                print(f"  No response received for message {i}")
            else:
                print(f"  Received response for message {i}")

        # Phase 2: After 5 messages, reply 6 should start continuous sending
        print(f"\n--- Phase 2: Continuous sending should start now ---")
        print("Listening for continuous graph and numeric data...")

        continuous_start = time.time()
        continuous_time = 3.0  # Listen for 3 seconds
        message_count = 0

        while time.time() - continuous_start < continuous_time:
            try:
                client_socket.settimeout(0.1)
                data = client_socket.recv(4096)
                if data:
                    elapsed = int((time.time() - start_time) * 1000)
                    message_count += 1
                    try:
                        content = data.decode('utf-8', errors='strict')
                        print(f"  [{elapsed:5d}ms] #{message_count}: "
                              f"{len(data):2d} bytes: {content}")
                    except UnicodeDecodeError:
                        print(f"  [{elapsed:5d}ms] #{message_count}: "
                              f"{len(data):2d} bytes: [binary data: {data[:20].hex()}...]")
            except socket.timeout:
                continue
            except (OSError, ConnectionError):
                print("Connection error during continuous receive")
                break

        print(f"\nContinuous phase: Received {message_count} messages in {continuous_time} seconds")
        print(f"Total test time: {time.time() - start_time:.2f} seconds")

    except (OSError, ConnectionError) as e:
        print(f"Error: {e}")
    finally:
        if client_socket:
            try:
                client_socket.close()
            except (OSError, AttributeError):
                pass


if __name__ == "__main__":
    main()
