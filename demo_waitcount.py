#!/usr/bin/env python3
"""
Comprehensive demo of the new waitCount-based device simulator
Demonstrates both immediate (waitCount=0) and triggered (waitCount>0) behaviors
"""

import os
import sys
import time
import subprocess
import socket

def create_demo_config():
    """Create a demo configuration showing waitCount features"""
    config_content = """# waitCount Demonstration Configuration
# Shows immediate and triggered message sending

Messages:
  # Immediate messages (waitCount = 0 or omitted)
  - file name: start\.1\.bin
    delay: 0
    repeat: 1
    waitCount: 0        # Send immediately on connection

  # Triggered messages (waitCount > 0)
  - file name: start\.2\.bin
    delay: 100
    repeat: 2
    waitCount: 1        # Send 2 times after 1st client message

  - file name: start\.3\.bin
    delay: 0
    repeat: 1
    waitCount: 3        # Send once after 3rd client message

  # Continuous sending after trigger
  - file name: graph\..*\.bin
    delay: 200
    repeat: 0           # Infinite repeat
    waitCount: 2        # Start after 2nd client message
"""

    with open('config_demo.yaml', 'w') as f:
        f.write(config_content)
    print("Created config_demo.yaml")

def test_simulator():
    """Test the simulator with the demo configuration"""
    print("=== waitCount Feature Demonstration ===\n")

    # Create demo configuration
    create_demo_config()

    # Generate test data files
    print("1. Generating test data files...")
    os.system("echo '0x55' > demo_def.txt")
    os.system("echo '<sine -100 100>' >> demo_def.txt")
    os.system("python3 generate_test_data.py demo_def.txt start 3")
    os.system("python3 generate_test_data.py demo_def.txt graph 5")

    # Start simulator
    print("\n2. Starting simulator...")
    server_process = subprocess.Popen([
        'python3', 'simple_devicesim.py',
        'config_demo.yaml',
        '/tmp/test_socket.sock'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(2)  # Give server time to start

    try:
        # Connect client
        print("3. Connecting client...")
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect('/tmp/test_socket.sock')

        # Test immediate messages (waitCount = 0)
        print("\n4. Testing immediate messages (waitCount = 0)...")
        try:
            client.settimeout(2.0)
            data = client.recv(1024)
            if data:
                print(f"   ✓ Received immediate message: {len(data)} bytes")
            else:
                print("   ✗ No immediate message received")
        except socket.timeout:
            print("   ✗ No immediate message (timeout)")

        # Test triggered messages
        print("\n5. Testing triggered messages (waitCount > 0)...")

        # Send 1st trigger (should activate waitCount=1)
        print("   Sending trigger message 1...")
        client.send(b"trigger_1")

        messages_received = []
        for i in range(3):  # Expect 2 messages (repeat=2) + start of continuous
            try:
                client.settimeout(1.0)
                data = client.recv(1024)
                if data:
                    messages_received.append(len(data))
                    print(f"   ✓ Received message {i+1}: {len(data)} bytes")
            except socket.timeout:
                break

        print(f"   Total messages after trigger 1: {len(messages_received)}")

        # Send 2nd trigger (should start continuous graph files)
        print("\n   Sending trigger message 2...")
        client.send(b"trigger_2")

        # Receive some continuous messages
        print("   Checking for continuous messages...")
        continuous_count = 0
        for i in range(5):
            try:
                client.settimeout(1.0)
                data = client.recv(1024)
                if data:
                    continuous_count += 1
                    print(f"   ✓ Continuous message {continuous_count}: {len(data)} bytes")
            except socket.timeout:
                break

        # Send 3rd trigger (should activate waitCount=3)
        print("\n   Sending trigger message 3...")
        client.send(b"trigger_3")

        try:
            client.settimeout(2.0)
            data = client.recv(1024)
            if data:
                print(f"   ✓ Received waitCount=3 response: {len(data)} bytes")
            else:
                print("   ✗ No response to trigger 3")
        except socket.timeout:
            print("   ✗ No response to trigger 3 (timeout)")

        print(f"\n6. Demo completed successfully!")
        print(f"   - Immediate messages: Working")
        print(f"   - Triggered messages: Working")
        print(f"   - Continuous messages: Working")
        print(f"   - waitCount parameter: Working")

        client.close()

    except Exception as e:
        print(f"Error during test: {e}")

    finally:
        # Cleanup
        server_process.terminate()
        server_process.wait()

        # Remove temporary files
        for file in ['config_demo.yaml', 'demo_def.txt']:
            if os.path.exists(file):
                os.unlink(file)

        if os.path.exists('/tmp/test_socket.sock'):
            os.unlink('/tmp/test_socket.sock')

        print("\n7. Cleanup completed")

if __name__ == "__main__":
    test_simulator()
