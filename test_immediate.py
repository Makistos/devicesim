#!/usr/bin/env python3
"""
Test client for the immediate start configuration (WaitToStart: No, ReceiveCount: 1)
"""

import socket
import sys
import time


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_immediate.py <socket_file>")
        sys.exit(1)

    socket_file = sys.argv[1]
    client_socket = None

    try:
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(socket_file)
        print(f"Connected to {socket_file}")

        # Since WaitToStart is No, the server should start immediately
        # Let's first check if we get immediate data
        print("Checking for immediate data (server should start without trigger)...")

        start_time = time.time()
        immediate_data_count = 0

        # Check for immediate data for 2 seconds
        while time.time() - start_time < 2.0:
            try:
                client_socket.settimeout(0.1)
                data = client_socket.recv(4096)
                if data:
                    elapsed = int((time.time() - start_time) * 1000)
                    immediate_data_count += 1
                    try:
                        content = data.decode('utf-8', errors='strict')
                        print(f"  [{elapsed:5d}ms] #{immediate_data_count}: "
                              f"{len(data):2d} bytes: {content.strip()}")
                    except UnicodeDecodeError:
                        print(f"  [{elapsed:5d}ms] #{immediate_data_count}: "
                              f"{len(data):2d} bytes: [binary data: {data[:20].hex()}...]")
            except socket.timeout:
                continue
            except (OSError, ConnectionError):
                print("Connection error during immediate data check")
                break

        if immediate_data_count > 0:
            print(f"\n✅ Server started immediately and sent {immediate_data_count} messages!")
        else:
            print(f"\n❌ No immediate data received. Server might be waiting for a message.")

        # Now send one message (should trigger reply 1, then start continuous reply 2)
        print(f"\nSending one message to trigger the reply sequence...")
        client_socket.send(b"test_message")
        print("Sent: test_message")

        # Collect responses
        message_count = 0
        collect_start = time.time()
        collect_time = 3.0  # Listen for 3 seconds

        print(f"Listening for responses for {collect_time} seconds...")

        while time.time() - collect_start < collect_time:
            try:
                client_socket.settimeout(0.1)
                data = client_socket.recv(4096)
                if data:
                    elapsed = int((time.time() - start_time) * 1000)
                    message_count += 1
                    try:
                        content = data.decode('utf-8', errors='strict')
                        print(f"  [{elapsed:5d}ms] #{immediate_data_count + message_count}: "
                              f"{len(data):2d} bytes: {content.strip()}")
                    except UnicodeDecodeError:
                        print(f"  [{elapsed:5d}ms] #{immediate_data_count + message_count}: "
                              f"{len(data):2d} bytes: [binary data: {data[:20].hex()}...]")
            except socket.timeout:
                continue
            except (OSError, ConnectionError):
                print("Connection error during response collection")
                break

        total_messages = immediate_data_count + message_count
        print(f"\nTest completed!")
        print(f"Total messages received: {total_messages}")
        print(f"- Immediate data: {immediate_data_count}")
        print(f"- After sending message: {message_count}")
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
