#!/usr/bin/env python3
"""
Test script to verify waitCount functionality
"""

import socket
import time
import os
import threading

def test_client():
    """Client that sends messages and receives responses"""
    time.sleep(1)  # Give server time to start

    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        client_socket.connect('/tmp/test_socket.sock')
        print("Client connected")

        # Send 3 trigger messages and receive responses
        for i in range(3):
            message = f"trigger_{i+1}".encode()
            print(f"Sending trigger message {i+1}: {message}")
            client_socket.send(message)
            time.sleep(0.5)  # Small delay between messages

            # Try to receive any response
            try:
                client_socket.settimeout(1.0)
                response = client_socket.recv(1024)
                if response:
                    print(f"Received response after message {i+1}: {len(response)} bytes")
                else:
                    print(f"No response after message {i+1}")
            except socket.timeout:
                print(f"No response received after message {i+1} (timeout)")

        print("Client finished sending messages")
        time.sleep(2)  # Give server time to process

    except Exception as e:
        print(f"Client error: {e}")
    finally:
        client_socket.close()
        print("Client disconnected")

def run_test():
    """Run the complete test"""
    print("=== Testing waitCount functionality ===")

    # First, generate some test data files
    print("Generating test files...")
    os.system("echo '0x55' > /tmp/simple_def.txt")
    os.system("echo '100' >> /tmp/simple_def.txt")
    os.system("python3 generate_test_data.py /tmp/simple_def.txt start 3")

    # Start the simulator in background
    server_process = None
    try:
        import subprocess
        server_process = subprocess.Popen([
            'python3', 'simple_devicesim.py',
            'config_triggered.yaml',
            '/tmp/test_socket.sock'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("Server started, waiting for it to initialize...")
        time.sleep(2)

        # Run the client
        test_client()

    except Exception as e:
        print(f"Test error: {e}")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()

        # Cleanup
        if os.path.exists('/tmp/test_socket.sock'):
            os.unlink('/tmp/test_socket.sock')
        if os.path.exists('/tmp/simple_def.txt'):
            os.unlink('/tmp/simple_def.txt')

        print("Test completed")

if __name__ == "__main__":
    run_test()
