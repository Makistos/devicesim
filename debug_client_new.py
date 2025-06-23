#!/usr/bin/env python3
"""
Simple debug client to test the device simulator step by step
Works with the new waitCount-based configuration format
"""

import socket
import time
import sys

def main():
    socket_file = "/tmp/test_socket.sock"
    client_socket = None

    try:
        # Connect to socket
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(socket_file)
        print(f"Connected to {socket_file}")
        print("Note: This client works with waitCount-based configurations")

        # Check for immediate messages (waitCount = 0)
        print("\nChecking for immediate messages (waitCount = 0)...")
        try:
            client_socket.settimeout(2.0)
            data = client_socket.recv(1024)
            if data:
                print(f"Received immediate message: {len(data)} bytes")
            else:
                print("No immediate messages")
        except socket.timeout:
            print("No immediate messages (timeout)")

        # Send trigger messages to activate waitCount-based responses
        print(f"\nSending trigger messages...")
        for i in range(1, 6):
            message = f"trigger_{i}".encode()
            print(f"\nSending trigger message {i}: {message.decode()}")
            client_socket.send(message)

            # Wait for response (should come if waitCount matches)
            try:
                client_socket.settimeout(3.0)
                data = client_socket.recv(1024)
                if data:
                    print(f"  -> Received response: {len(data)} bytes")
                else:
                    print(f"  -> No response for message {i}")
            except socket.timeout:
                print(f"  -> No response for message {i} (timeout)")

            time.sleep(0.5)  # Small delay between messages

        # Give time for any continuous messages (repeat: 0) to start
        print(f"\nWaiting for continuous messages (repeat: 0)...")
        for i in range(5):  # Check for 5 more messages
            try:
                client_socket.settimeout(2.0)
                data = client_socket.recv(1024)
                if data:
                    print(f"Received continuous message {i+1}: {len(data)} bytes")
                else:
                    break
            except socket.timeout:
                print("No more continuous messages")
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client_socket:
            client_socket.close()
            print("Disconnected")

if __name__ == "__main__":
    main()
