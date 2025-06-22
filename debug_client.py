#!/usr/bin/env python3
"""
Simple debug client to test the device simulator step by step
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

        # Send initial trigger (for WaitToStart)
        client_socket.send(b"initial_trigger")
        print("Sent initial trigger message")
        time.sleep(1)

        # Try to receive any immediate response
        try:
            client_socket.settimeout(2.0)
            data = client_socket.recv(1024)
            if data:
                print(f"Received immediate response: {data}")
            else:
                print("No immediate response")
        except socket.timeout:
            print("No immediate response (timeout)")

        # Now send the 5 messages that should trigger replies
        for i in range(1, 6):
            message = f"message_{i}".encode()
            client_socket.send(message)
            print(f"Sent message {i}: {message}")

            # Wait a bit and try to receive response
            try:
                client_socket.settimeout(3.0)
                data = client_socket.recv(1024)
                if data:
                    print(f"  -> Received response: {data}")
                else:
                    print(f"  -> No response for message {i}")
            except socket.timeout:
                print(f"  -> Timeout waiting for response to message {i}")

        print("Keeping connection open for a few more seconds...")
        time.sleep(5)

        # Try to receive any more data
        try:
            client_socket.settimeout(1.0)
            while True:
                data = client_socket.recv(1024)
                if data:
                    print(f"Additional data: {data}")
                else:
                    break
        except socket.timeout:
            print("No more data available")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client_socket:
            try:
                client_socket.close()
            except:
                pass

if __name__ == "__main__":
    main()
