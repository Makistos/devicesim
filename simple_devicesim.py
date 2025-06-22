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

    # Convert WaitToStart to boolean
    wait_to_start_value = config.get('WaitToStart', 'No')
    if isinstance(wait_to_start_value, bool):
        wait_to_start = wait_to_start_value
    else:
        wait_to_start = (
            str(wait_to_start_value).lower() in ['yes', 'true', '1']
        )
    receive_count = int(config.get('ReceiveCount', 0))

    # Support both old format (Messages) and new format (Replies)
    if 'Replies' in config:
        replies = config['Replies']
    elif 'Messages' in config:
        # Convert old format to new format for backward compatibility
        replies = [{
            'reply_number': 1,
            'Messages': config['Messages']
        }]
    else:
        replies = []

    return {
        'WaitToStart': wait_to_start,
        'ReceiveCount': receive_count,
        'Replies': replies
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


def create_message_schedule_for_reply(reply_config: Dict[str, Any],
                                      base_dir: str) -> List[Dict[str, Any]]:
    """Create message schedule for a specific reply"""
    message_schedule = []

    for msg_config in reply_config.get('Messages', []):
        pattern = msg_config['file name']
        delay = msg_config['delay']
        repeat = msg_config['repeat']

        matching_files = find_matching_files(pattern, base_dir)
        file_list = [os.path.basename(f) for f in matching_files]
        print(f"  Pattern '{pattern}' matches {len(matching_files)} files:")
        print(f"    {file_list}")

        for file_path in matching_files:
            message_schedule.append({
                'file_path': file_path,
                'delay': delay,
                'repeat': repeat,
                'sent_count': 0
            })

    return message_schedule


def create_message_schedule(config: Dict[str, Any],
                            base_dir: str) -> List[Dict[str, Any]]:
    """Create message schedule from configuration (backward compatibility)"""
    # This function is kept for backward compatibility
    # For new reply-based configs, we'll use create_message_schedule_for_reply
    if 'Replies' in config and config['Replies']:
        # Use the first reply for backward compatibility
        first_reply = config['Replies'][0]
        return create_message_schedule_for_reply(first_reply, base_dir)
    return []


def run_message_loop(connection, config: Dict[str, Any]) -> None:
    """Run the main message loop with reply-based logic"""
    replies = config.get('Replies', [])
    receive_count = config['ReceiveCount']

    if not replies:
        print("No replies configured")
        return

    print(f"Configured {len(replies)} different replies")
    print(f"ReceiveCount: {receive_count} (0 = unlimited)")

    # Show configuration for each reply
    base_dir = os.getcwd()
    for reply in replies:
        reply_num = reply.get('reply_number', 'unknown')
        print(f"Reply {reply_num} configuration:")
        create_message_schedule_for_reply(reply, base_dir)

    received_count = 0
    current_reply_index = 0

    # Phase 1: Handle ReceiveCount messages with corresponding replies
    if receive_count > 0:
        print(f"\nPhase 1: Handling first {receive_count} received messages")
        while received_count < receive_count:
            # Wait for incoming message
            print(f"\nWaiting for message {received_count + 1}...")
            received_data = receive_with_timeout(connection, 30.0)

            if not received_data:
                print("No message received, continuing...")
                continue

            received_count += 1
            print(f"Received message #{received_count}")

            # Use corresponding reply if available
            if current_reply_index < len(replies):
                reply_to_use = replies[current_reply_index]
                print(f"Using reply #{reply_to_use.get('reply_number', current_reply_index + 1)}")

                # Create and execute message schedule for this reply
                reply_schedule = create_message_schedule_for_reply(reply_to_use, base_dir)
                if reply_schedule:
                    execute_reply_schedule(connection, reply_schedule)
                else:
                    print("No messages to send for this reply")

                current_reply_index += 1
            else:
                print("No more replies configured for this message")

    # Phase 2: Continue with remaining replies and their message patterns
    if current_reply_index < len(replies):
        print(f"\nPhase 2: Processing remaining replies {current_reply_index + 1} to {len(replies)}")
        while current_reply_index < len(replies):
            reply_to_use = replies[current_reply_index]
            reply_num = reply_to_use.get('reply_number', current_reply_index + 1)
            print(f"\nProcessing reply #{reply_num}")

            # Create and execute message schedule for this reply
            reply_schedule = create_message_schedule_for_reply(reply_to_use, base_dir)
            if reply_schedule:
                execute_continuous_schedule(connection, reply_schedule)
            else:
                print("No messages to send for this reply")

            current_reply_index += 1

    print("\nAll replies processed")


def execute_reply_schedule(connection,
                           reply_schedule: List[Dict[str, Any]]) -> None:
    """Execute a reply schedule (send messages with timing)"""
    print(f"Executing reply with {len(reply_schedule)} message(s)")

    for msg in reply_schedule:
        delay_seconds = msg['delay'] / 1000.0  # Convert milliseconds to seconds
        repeat_count = msg['repeat']

        print(f"Sending {os.path.basename(msg['file_path'])}: "
              f"delay={msg['delay']}ms, repeat={repeat_count}")

        if delay_seconds > 0:
            print(f"Waiting {delay_seconds} seconds before sending...")
            time.sleep(delay_seconds)

        # Send the message
        if send_file(msg['file_path'], connection):
            msg['sent_count'] = 1

            # Handle repeats
            for i in range(1, repeat_count):
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
                if not send_file(msg['file_path'], connection):
                    print(f"Failed to send repeat {i+1}, stopping")
                    return
                msg['sent_count'] += 1
        else:
            print("Send failed, stopping reply execution")
            return


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
            # Wait for initial message if configured
            if config['WaitToStart']:
                print("WaitToStart is enabled - waiting for initial message...")
                initial_data = receive_with_timeout(connection, 30.0)
                if not initial_data:
                    print("No initial message received, exiting")
                    return
                print("Initial message received, starting device simulation")
            else:
                print("WaitToStart is disabled - starting immediately")

            # Run the message loop
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
