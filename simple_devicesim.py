#!/usr/bin/env python3
"""
Simple Device Simulator Script

This script reads a YAML configuration file and creates a UNIX socket to send
and receive data based on the rules defined in the configuration file.

Usage: python simple_devicesim.py <config_file> <socket_file>
"""

import heapq
import os
import re
import socket
import sys
import time
from typing import List, Dict, Any, Optional

import yaml


def load_config(config_file: str) -> Dict[str, Any]:
    """Load and parse YAML configuration"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Support new simplified format with Messages array
    if 'Messages' in config:
        messages = config['Messages']
    # Backward compatibility: convert old Replies format
    elif 'Replies' in config:
        messages = []
        for reply in config['Replies']:
            if 'Messages' in reply:
                messages.extend(reply['Messages'])
    else:
        messages = []

    # Ensure each message has required fields with defaults
    for message in messages:
        if 'waitCount' not in message:
            message['waitCount'] = 0  # Default: send immediately
        if 'delay' not in message:
            message['delay'] = 0  # Default: no delay
        if 'repeat' not in message:
            message['repeat'] = 1  # Default: send once

    return {
        'Messages': messages
    }


def find_matching_files(pattern: str, base_dir: str = '.') -> List[str]:
    """Find files matching the regex pattern"""
    try:
        files = []
        for filename in os.listdir(base_dir):
            if re.match(pattern, filename):
                full_path = os.path.join(base_dir, filename)
                if os.path.isfile(full_path):
                    files.append(full_path)
        return sorted(files)
    except OSError as e:
        print(f"Error finding files for pattern '{pattern}': {e}")
        return []


def send_file(file_path: str, connection) -> bool:
    """Send file contents to socket"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        connection.send(data)
        print(f"Sent: {os.path.basename(file_path)} ({len(data)} bytes)")
        return True
    except (OSError, ConnectionError) as e:
        print(f"Error sending file {file_path}: {e}")
        return False


def receive_with_timeout(connection, timeout: float) -> Optional[bytes]:
    """Receive data with timeout"""
    connection.settimeout(timeout)
    try:
        data = connection.recv(4096)
        if data:
            print(f"Received: {data.hex()}")
        return data
    except socket.timeout:
        return None
    except (OSError, ConnectionError) as e:
        print(f"Error receiving: {e}")
        return None


def create_message_schedule(config: Dict[str, Any],
                            base_dir: str) -> List[Dict[str, Any]]:
    """Create message schedule from configuration - DEPRECATED"""
    print("WARNING: create_message_schedule is deprecated")
    return []


def create_message_schedule_for_reply(reply_config: Dict[str, Any],
                                      base_dir: str) -> List[Dict[str, Any]]:
    """Create message schedule for a specific reply - DEPRECATED"""
    print("WARNING: create_message_schedule_for_reply is deprecated")
    return []


def run_message_loop(connection, config: Dict[str, Any]) -> None:
    """Run the main message loop with waitCount-based logic"""
    messages = config.get('Messages', [])

    if not messages:
        print("No messages configured")
        return

    print(f"Configured {len(messages)} messages")

    # Group messages by waitCount for efficient processing
    base_dir = os.getcwd()
    wait_groups = {}
    immediate_messages = []

    for msg_config in messages:
        wait_count = msg_config.get('waitCount', 0)
        pattern = msg_config['file name']
        delay = msg_config.get('delay', 0)
        repeat = msg_config.get('repeat', 1)

        # Find matching files
        matching_files = find_matching_files(pattern, base_dir)
        print(f"Pattern '{pattern}' matches {len(matching_files)} files (waitCount={wait_count})")

        # Create message entries for each matching file
        for file_path in matching_files:
            message_entry = {
                'file_path': file_path,
                'delay': delay,
                'repeat': repeat,
                'sent_count': 0,
                'waitCount': wait_count
            }

            if wait_count == 0:
                immediate_messages.append(message_entry)
            else:
                if wait_count not in wait_groups:
                    wait_groups[wait_count] = []
                wait_groups[wait_count].append(message_entry)

    # Send immediate messages (waitCount = 0)
    if immediate_messages:
        print(f"\nSending {len(immediate_messages)} immediate messages")
        execute_message_group(connection, immediate_messages)

    # Process triggered messages
    if wait_groups:
        max_wait_count = max(wait_groups.keys())
        print(f"Will wait for up to {max_wait_count} client messages")

        received_count = 0

        while received_count < max_wait_count:
            # Wait for incoming message
            print(f"\nWaiting for client message {received_count + 1}...")
            received_data = receive_with_timeout(connection, 30.0)

            if not received_data:
                print("No message received, timeout reached")
                break

            received_count += 1
            print(f"Received client message #{received_count}")

            # Check if any message groups should be triggered
            if received_count in wait_groups:
                messages_to_send = wait_groups[received_count]
                print(f"Triggering {len(messages_to_send)} message(s) for waitCount {received_count}")
                execute_message_group(connection, messages_to_send)

    print("\nMessage loop completed")


def execute_message_group(connection, messages: List[Dict[str, Any]]) -> None:
    """Execute a group of messages with proper timing and repetition"""
    if not messages:
        return

    # Separate messages by behavior type
    request_response_messages = [msg for msg in messages if msg['repeat'] < 0]
    immediate_messages = [msg for msg in messages if msg['repeat'] > 0]
    single_messages = [msg for msg in messages if msg['repeat'] == 0 and msg['delay'] == 0]
    continuous_messages = [msg for msg in messages if msg['repeat'] == 0 and msg['delay'] > 0]

    # Handle single messages (repeat=0, delay=0)
    for msg in single_messages:
        print(f"Sending {os.path.basename(msg['file_path'])}: single message")
        if send_file(msg['file_path'], connection):
            msg['sent_count'] += 1
        else:
            print(f"Failed to send {os.path.basename(msg['file_path'])}, stopping")
            return

    # Send immediate/finite messages
    for msg in immediate_messages:
        delay_seconds = msg['delay'] / 1000.0 if msg['delay'] > 0 else 0
        repeat_count = msg['repeat']

        print(f"Sending {os.path.basename(msg['file_path'])}: "
              f"delay={msg['delay']}ms, repeat={repeat_count}")

        for i in range(repeat_count):
            if i > 0 and delay_seconds > 0:
                time.sleep(delay_seconds)

            if send_file(msg['file_path'], connection):
                msg['sent_count'] += 1
            else:
                print(f"Failed to send {os.path.basename(msg['file_path'])}, stopping")
                return

    # Handle request-response messages (repeat < 0)
    for msg in request_response_messages:
        execute_request_response_message(connection, msg)

    # Handle continuous messages (repeat=0) with scheduling
    if continuous_messages:
        execute_continuous_schedule(connection, continuous_messages)


def execute_reply_schedule(connection,
                           reply_schedule: List[Dict[str, Any]]) -> None:
    """Execute a reply schedule (send messages with timing) - DEPRECATED"""
    print("WARNING: execute_reply_schedule is deprecated, use execute_message_group instead")
    execute_message_group(connection, reply_schedule)


def execute_continuous_schedule(connection, reply_schedule: List[Dict[str, Any]]) -> None:
    """Execute a continuous schedule (send messages continuously based on delay/repeat)"""
    start_time = time.time()
    send_queue: List = []

    # Group messages by delay to create rotation groups
    delay_groups = {}
    for i, msg in enumerate(reply_schedule):
        delay = msg['delay']
        if delay not in delay_groups:
            delay_groups[delay] = []
        delay_groups[delay].append((i, msg))

    # Schedule initial sends for each delay group
    for delay, group in delay_groups.items():
        send_time = start_time + (delay / 1000.0)
        # Start with the first message in each group
        msg_index, msg = group[0]
        # Add rotation info to track which message to send next
        rotation_state = {
            'current_index': 0,
            'group': group,
            'delay': delay
        }
        heapq.heappush(send_queue, (send_time, msg_index, msg, rotation_state))

    print(f"Scheduled {len(delay_groups)} delay groups for continuous sending")

    # Track messages with infinite repeat
    infinite_messages = [msg for msg in reply_schedule if msg['repeat'] == 0]
    if infinite_messages:
        print(f"Note: {len(infinite_messages)} message(s) have infinite repeat")

    # Process the schedule
    while send_queue:
        current_time = time.time()

        # Send any messages that are due
        while send_queue and send_queue[0][0] <= current_time:
            send_time, msg_index, msg, rotation_state = heapq.heappop(send_queue)

            if send_file(msg['file_path'], connection):
                msg['sent_count'] += 1

                # Schedule next send if needed
                if msg['repeat'] == 0 or msg['sent_count'] < msg['repeat']:
                    # Calculate next send time
                    next_send_time = send_time + (rotation_state['delay'] / 1000.0)

                    # Rotate to next message in the group
                    group = rotation_state['group']
                    rotation_state['current_index'] = (rotation_state['current_index'] + 1) % len(group)
                    next_msg_index, next_msg = group[rotation_state['current_index']]

                    heapq.heappush(send_queue, (next_send_time, next_msg_index, next_msg, rotation_state))
                else:
                    print(f"Completed sending {os.path.basename(msg['file_path'])} ({msg['sent_count']} times)")

            else:
                print("Send failed, stopping continuous schedule execution")
                return

        # For infinite messages, we'll run until interrupted or connection closes
        # Add a small check for connection status
        try:
            # Send a zero-byte message to test if connection is still alive
            connection.send(b'')
        except (ConnectionError, BrokenPipeError):
            print("Connection lost, stopping continuous schedule")
            break

        # Small sleep to prevent busy loop
        time.sleep(0.001)


def execute_request_response_message(connection, msg: Dict[str, Any]) -> None:
    """Execute a request-response message (repeat < 0)

    Sends the message repeatedly, waiting for abs(repeat) client messages
    between each send. This creates a request-response pattern.
    """
    request_count = abs(msg['repeat'])  # Number of client messages to wait for
    delay_seconds = msg['delay'] / 1000.0 if msg['delay'] > 0 else 0
    file_name = os.path.basename(msg['file_path'])

    print(f"Starting request-response for {file_name}: "
          f"wait for {request_count} client message(s) between sends, delay={msg['delay']}ms")

    # Send the first message immediately (after initial waitCount if any)
    if delay_seconds > 0:
        time.sleep(delay_seconds)

    if not send_file(msg['file_path'], connection):
        print(f"Failed to send initial {file_name}, stopping request-response")
        return

    msg['sent_count'] = 1

    # Continue request-response cycle indefinitely
    while True:
        print(f"Waiting for {request_count} client message(s) before next {file_name}...")

        # Wait for the required number of client messages
        received_messages = 0
        for i in range(request_count):
            received_data = receive_with_timeout(connection, 30.0)
            if not received_data:
                print(f"Timeout waiting for client message {i+1}/{request_count}, stopping request-response for {file_name}")
                return
            received_messages += 1
            print(f"  Received client message {received_messages}/{request_count}")

        # All required messages received, send the next response
        if delay_seconds > 0:
            time.sleep(delay_seconds)

        if not send_file(msg['file_path'], connection):
            print(f"Failed to send {file_name}, stopping request-response")
            return

        msg['sent_count'] += 1
        print(f"Sent {file_name} (total sent: {msg['sent_count']})")


def main():
    """Main function - entry point of the script"""
    if len(sys.argv) != 3:
        print("Usage: python simple_devicesim.py <config_file> <socket_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    socket_file = sys.argv[2]

    # Load configuration
    try:
        config = load_config(config_file)
        print(f"Configuration loaded: {config}")
    except (OSError, yaml.YAMLError) as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    # Remove existing socket file
    if os.path.exists(socket_file):
        os.unlink(socket_file)

    # Create socket
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        server_socket.bind(socket_file)
        server_socket.listen(1)
        print(f"Socket listening on {socket_file}")

        # Wait for connection
        print("Waiting for connection...")
        connection, _ = server_socket.accept()
        print("Client connected")

        try:
            # Run the message loop with new waitCount-based logic
            run_message_loop(connection, config)

        except (OSError, ConnectionError) as e:
            print(f"Error in main loop: {e}")
        finally:
            connection.close()

    except (OSError, ConnectionError) as e:
        print(f"Socket error: {e}")
    finally:
        server_socket.close()
        if os.path.exists(socket_file):
            os.unlink(socket_file)
        print("Cleanup completed")


if __name__ == "__main__":
    main()
