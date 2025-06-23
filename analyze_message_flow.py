#!/usr/bin/env python3
"""
Generic message flow analyzer for device simulator YAML configurations
Shows exactly what messages are sent between simulator and client for any config

Usage: python3 analyze_message_flow.py <config.yaml> [num_client_messages]
"""

import os
import sys
import time
import subprocess
import socket
import yaml
from datetime import datetime

class MessageFlowAnalyzer:
    def __init__(self, config_file, max_client_messages=10):
        self.config_file = config_file
        self.max_client_messages = max_client_messages
        self.message_log = []
        self.client = None
        self.server_process = None
        self.config = None
        
    def load_and_analyze_config(self):
        """Load and analyze the YAML configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            print(f"=== Message Flow Analysis: {self.config_file} ===\n")
            
            messages = self.config.get('Messages', [])
            if not messages:
                print("❌ No Messages found in configuration")
                return False
                
            print(f"📋 Configuration contains {len(messages)} message(s):")
            for i, msg in enumerate(messages, 1):
                file_pattern = msg.get('file name', 'unknown')
                repeat = msg.get('repeat', 1)
                delay = msg.get('delay', 0)
                wait_count = msg.get('waitCount', 0)
                
                # Determine behavior type
                if repeat > 0:
                    behavior = f"Send {repeat} times then stop"
                elif repeat == 0:
                    behavior = "Send continuously (infinite)"
                else:
                    behavior = f"Request-response (wait for {abs(repeat)} client msg(s))"
                
                trigger = "Immediately" if wait_count == 0 else f"After {wait_count} client message(s)"
                
                print(f"   {i}. {file_pattern}")
                print(f"      ├─ Trigger: {trigger}")
                print(f"      ├─ Behavior: {behavior}")
                print(f"      └─ Delay: {delay}ms")
                
            return True
            
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False

    def log_message(self, direction, content, description=""):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.message_log.append({
            'time': timestamp,
            'direction': direction,  # 'CLIENT->SERVER' or 'SERVER->CLIENT'
            'content': content,
            'description': description
        })

        arrow = "📤" if direction == "CLIENT->SERVER" else "📥"
        print(f"[{timestamp}] {arrow} {direction}: {content} {description}")

    def setup_test_environment(self):
        """Set up test data files based on config"""
        print("\n1. Setting up test environment...")
        
        # Create a simple test definition
        os.system("echo '0xAA' > /tmp/flow_def.txt")
        os.system("echo '0xBB' >> /tmp/flow_def.txt")
        
        # Find all file patterns in config and generate matching files
        messages = self.config.get('Messages', [])
        file_patterns = set()
        
        for msg in messages:
            pattern = msg.get('file name', '')
            # Extract base name from regex pattern (simplified)
            if '\\.' in pattern:
                base = pattern.split('\\.')[0]
                file_patterns.add(base)
        
        # Generate test files for each pattern
        for pattern in file_patterns:
            print(f"   Generating files for pattern: {pattern}")
            os.system(f"python3 generate_test_data.py /tmp/flow_def.txt {pattern} 5")
        
        print(f"   Test files created with content: [0xAA, 0xBB] (2 bytes each)")

    def start_simulator(self):
        """Start the simulator in background"""
        print(f"\n2. Starting simulator with {self.config_file}...")
        self.server_process = subprocess.Popen([
            'python3', 'simple_devicesim.py',
            self.config_file,
            '/tmp/test_socket.sock'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        time.sleep(2)  # Give server time to start
        print("   Simulator started and listening...")

    def connect_client(self):
        """Connect client to simulator"""
        print("\n3. Connecting client...")
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.client.connect('/tmp/test_socket.sock')
        print("   Client connected")

    def analyze_message_flow(self):
        """Analyze the message flow based on configuration"""
        print(f"\n4. Message Flow Analysis:")
        print("=" * 80)
        
        messages = self.config.get('Messages', [])
        
        # Check for immediate messages (waitCount = 0)
        immediate_messages = [msg for msg in messages if msg.get('waitCount', 0) == 0]
        if immediate_messages:
            print(f"\n📍 IMMEDIATE MESSAGES (waitCount = 0)")
            print(f"   Expected: {len(immediate_messages)} message(s) should be sent immediately")
            
            immediate_received = 0
            for i in range(len(immediate_messages) * 3):  # Try to receive multiple
                try:
                    self.client.settimeout(2.0)
                    data = self.client.recv(1024)
                    if data:
                        immediate_received += 1
                        self.log_message("SERVER->CLIENT", f"{len(data)} bytes", f"(immediate #{immediate_received})")
                    else:
                        break
                except socket.timeout:
                    break
            
            print(f"   📊 Immediate messages received: {immediate_received}")
        
        # Send client messages and observe responses
        client_message_count = 0
        
        for round_num in range(1, self.max_client_messages + 1):
            print(f"\n📍 CLIENT MESSAGE ROUND {round_num}")
            
            # Send client message
            client_msg = f"client_msg_{round_num}".encode()
            self.client.send(client_msg)
            client_message_count += 1
            self.log_message("CLIENT->SERVER", f"{len(client_msg)} bytes", 
                           f"(#{client_message_count}: '{client_msg.decode()}')")
            
            # Check which messages should be triggered by this client message count
            triggered_messages = [msg for msg in messages if msg.get('waitCount', 0) == client_message_count]
            
            if triggered_messages:
                print(f"   Expected triggers for client message #{client_message_count}:")
                for msg in triggered_messages:
                    repeat = msg.get('repeat', 1)
                    pattern = msg.get('file name', 'unknown')
                    if repeat > 0:
                        print(f"   • {pattern}: Send {repeat} times")
                    elif repeat == 0:
                        print(f"   • {pattern}: Start continuous sending")
                    else:
                        print(f"   • {pattern}: Start request-response (need {abs(repeat)} client msgs)")
            
            # Try to receive responses
            responses_received = 0
            for i in range(10):  # Try to receive up to 10 responses
                try:
                    self.client.settimeout(1.5)
                    data = self.client.recv(1024)
                    if data:
                        responses_received += 1
                        self.log_message("SERVER->CLIENT", f"{len(data)} bytes", 
                                       f"(response #{responses_received} to client msg #{client_message_count})")
                    else:
                        break
                except socket.timeout:
                    break
            
            print(f"   📊 Responses received: {responses_received}")
            
            # Stop early if no responses for several rounds
            if responses_received == 0 and round_num > 3:
                print(f"   ℹ️  No responses for several rounds, analysis may be complete")
                break
            
            time.sleep(0.5)  # Small delay between rounds
        
        print("=" * 80)

    def show_summary(self):
        """Show summary of message flow"""
        print(f"\n5. Message Flow Summary:")
        print("=" * 80)
        
        client_messages = [msg for msg in self.message_log if msg['direction'] == 'CLIENT->SERVER']
        server_messages = [msg for msg in self.message_log if msg['direction'] == 'SERVER->CLIENT']
        
        print(f"📤 Total client messages sent: {len(client_messages)}")
        print(f"📥 Total server messages received: {len(server_messages)}")
        
        if self.message_log:
            print(f"\n📋 Complete Message Timeline:")
            for i, msg in enumerate(self.message_log, 1):
                direction = "C→S" if msg['direction'] == 'CLIENT->SERVER' else "S→C"
                print(f"   {i:2d}. [{msg['time']}] {direction} {msg['content']} {msg['description']}")
        
        # Analyze patterns
        print(f"\n🔍 Pattern Analysis:")
        messages = self.config.get('Messages', [])
        
        for i, msg in enumerate(messages, 1):
            pattern = msg.get('file name', 'unknown')
            repeat = msg.get('repeat', 1)
            wait_count = msg.get('waitCount', 0)
            
            print(f"   {i}. {pattern}:")
            
            if repeat > 0:
                print(f"      └─ Finite repeat: Sends {repeat} times after {wait_count} client message(s)")
            elif repeat == 0:
                print(f"      └─ Continuous: Sends infinitely after {wait_count} client message(s)")
            else:
                print(f"      └─ Request-response: Needs {abs(repeat)} client message(s) between sends")
        
        print("=" * 80)

    def cleanup(self):
        """Clean up resources"""
        print(f"\n6. Cleanup...")
        
        if self.client:
            self.client.close()
            
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        # Remove temporary files
        for file in ['/tmp/flow_def.txt']:
            if os.path.exists(file):
                os.unlink(file)
        
        if os.path.exists('/tmp/test_socket.sock'):
            os.unlink('/tmp/test_socket.sock')
            
        print("   Cleanup completed")

    def run_analysis(self):
        """Run the complete analysis"""
        try:
            if not self.load_and_analyze_config():
                return
                
            self.setup_test_environment()
            self.start_simulator()
            self.connect_client()
            self.analyze_message_flow()
            self.show_summary()
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Analysis interrupted by user")
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.cleanup()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_message_flow.py <config.yaml> [max_client_messages]")
        print("\nExamples:")
        print("  python3 analyze_message_flow.py config_simple.yaml")
        print("  python3 analyze_message_flow.py config_request_response.yaml 8")
        print("  python3 analyze_message_flow.py config_triggered.yaml 12")
        sys.exit(1)
    
    config_file = sys.argv[1]
    max_messages = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        sys.exit(1)
    
    analyzer = MessageFlowAnalyzer(config_file, max_messages)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
