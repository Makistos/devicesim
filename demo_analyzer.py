#!/usr/bin/env python3
"""
Demo script showing analyze_message_flow.py with different configurations
"""

import os
import sys

def run_demo():
    print("=== Message Flow Analyzer Demonstration ===\n")
    
    configs = [
        ("config_simple.yaml", 3, "Immediate mode with continuous sending"),
        ("config_triggered.yaml", 6, "Triggered mode with various waitCount values"),
        ("config_request_response.yaml", 6, "Request-response patterns with negative repeat")
    ]
    
    for i, (config, messages, description) in enumerate(configs, 1):
        print(f"🔍 Demo {i}/3: {description}")
        print(f"   Configuration: {config}")
        print(f"   Client messages: {messages}")
        print(f"   Command: python3 analyze_message_flow.py {config} {messages}")
        
        # Run the analyzer
        if os.path.exists(config):
            print(f"\n{'='*60}")
            os.system(f"python3 analyze_message_flow.py {config} {messages}")
            print(f"{'='*60}\n")
        else:
            print(f"   ⚠️  Configuration file not found: {config}")
        
        if i < len(configs):
            input("Press Enter to continue to next demo...")
            print()
    
    print("✅ All demonstrations completed!")
    print("\nThe analyzer works with any valid YAML configuration and provides:")
    print("• Configuration analysis and parameter breakdown")
    print("• Real-time message flow tracking with timestamps") 
    print("• Pattern recognition and behavior classification")
    print("• Complete timeline and summary reports")

if __name__ == "__main__":
    run_demo()
