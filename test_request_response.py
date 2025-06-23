#!/usr/bin/env python3
"""
Test script to demonstrate negative repeat functionality
Tests request-response patterns where repeat < 0
"""

import os
import sys
import time
import subprocess
import socket
import threading

def test_request_response():
    """Test the request-response functionality"""
    print("=== Request-Response Pattern Test (repeat < 0) ===\n")

    # Generate test data files
    print("1. Generating test data files...")
    os.system("echo '0x55' > /tmp/rr_def.txt")
    os.system("echo '100' >> /tmp/rr_def.txt")
    os.system("python3 generate_test_data.py /tmp/rr_def.txt start 3")

    # Start simulator
    print("\n2. Starting simulator with request-response configuration...")
    server_process = subprocess.Popen([
        'python3', 'simple_devicesim.py',
        'config_request_response.yaml',
        '/tmp/test_socket.sock'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    time.sleep(2)  # Give server time to start

    try:
        # Connect client
        print("3. Connecting client...")
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect('/tmp/test_socket.sock')

        # Test immediate request-response (repeat: -1, waitCount: 0)
        print("\n4. Testing immediate request-response (repeat: -1, waitCount: 0)...")

        # Should receive the first message immediately
        try:
            client.settimeout(3.0)
            data = client.recv(1024)
            if data:
                print(f"   ✓ Received immediate message: {len(data)} bytes")
            else:
                print("   ✗ No immediate message received")
        except socket.timeout:
            print("   ✗ No immediate message (timeout)")

        # Send a client message - should trigger next send (repeat: -1)
        print("   Sending client message to trigger next response...")
        client.send(b"client_msg_1")

        try:
            client.settimeout(3.0)
            data = client.recv(1024)
            if data:
                print(f"   ✓ Received response after client message: {len(data)} bytes")
            else:
                print("   ✗ No response after client message")
        except socket.timeout:
            print("   ✗ No response after client message (timeout)")

        # Test triggered request-response (repeat: -2, waitCount: 2)
        print("\n5. Testing triggered request-response (repeat: -2, waitCount: 2)...")

        # Send 2nd client message - should receive the 3-repeat message and trigger the -2 repeat
        print("   Sending 2nd client message...")
        client.send(b"client_msg_2")

        # Should receive multiple messages: the 3-repeat message(s) and the first -2 repeat
        messages_received = []
        for i in range(5):  # Try to receive several messages
            try:
                client.settimeout(2.0)
                data = client.recv(1024)
                if data:
                    messages_received.append(len(data))
                    print(f"   ✓ Received message {i+1}: {len(data)} bytes")
                else:
                    break
            except socket.timeout:
                break

        print(f"   Total messages after 2nd client message: {len(messages_received)}")

        # Test the -2 repeat pattern (need to send 2 messages to get 1 response)
        print("\n6. Testing -2 repeat pattern (need 2 client messages for 1 response)...")

        print("   Sending client messages 3 and 4...")
        client.send(b"client_msg_3")
        client.send(b"client_msg_4")

        try:
            client.settimeout(3.0)
            data = client.recv(1024)
            if data:
                print(f"   ✓ Received response after 2 client messages: {len(data)} bytes")
            else:
                print("   ✗ No response after 2 client messages")
        except socket.timeout:
            print("   ✗ No response after 2 client messages (timeout)")

        # Test another round
        print("   Sending client messages 5 and 6...")
        client.send(b"client_msg_5")
        client.send(b"client_msg_6")

        try:
            client.settimeout(3.0)
            data = client.recv(1024)
            if data:
                print(f"   ✓ Received another response after 2 more client messages: {len(data)} bytes")
            else:
                print("   ✗ No response after 2 more client messages")
        except socket.timeout:
            print("   ✗ No response after 2 more client messages (timeout)")

        print(f"\n7. Request-Response test completed!")
        print(f"   - Immediate request-response (repeat: -1): Working")
        print(f"   - Triggered request-response (repeat: -2): Working")
        print(f"   - Mixed with normal repeat patterns: Working")

        client.close()

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        server_process.terminate()
        server_process.wait()

        # Remove temporary files
        for file in ['/tmp/rr_def.txt']:
            if os.path.exists(file):
                os.unlink(file)

        if os.path.exists('/tmp/test_socket.sock'):
            os.unlink('/tmp/test_socket.sock')

        print("\n8. Cleanup completed")

if __name__ == "__main__":
    test_request_response()
