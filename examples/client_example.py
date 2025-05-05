#!/usr/bin/env python3
"""
Example client script demonstrating how to connect to the VTX Emulator
and send SmartAudio commands.

This script shows how to:
1. Connect to the VTX Emulator server
2. Send SmartAudio commands
3. Parse the responses
"""

import socket
import time
import sys
import os

try:
    # Try to import directly
    from main_port import Configuration
except ImportError:
    # If that fails, add the parent directory to the path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    from main_port import Configuration


def create_get_settings_packet():
    """Create a SmartAudio GET_SETTINGS packet."""
    # [SYNC, HEADER, CMD, LEN, CRC]
    return bytearray([
        Configuration.SA_SYNC_BYTE,
        Configuration.SA_HEADER_BYTE,
        Configuration.SA_CMD_GET_SETTINGS,
        0x00,
        0x0B  # CRC
    ])


def create_set_power_packet(power_level):
    """Create a SmartAudio SET_POWER packet."""
    # [SYNC, HEADER, CMD, LEN, DATA, CRC]
    # CMD = 0x02 << 1 = 0x04 (SET_POWER)
    return bytearray([
        Configuration.SA_SYNC_BYTE,
        Configuration.SA_HEADER_BYTE,
        0x04,  # Shifted command
        0x01,  # Length
        power_level & 0x7F,  # Power level (mask off high bit)
        0xC3  # CRC (pre-calculated for power_level=2)
    ])


def parse_response(response):
    """Parse a SmartAudio response packet."""
    if len(response) < 5:
        return "Invalid response (too short)"
    
    cmd = response[2]
    length = response[3]
    data = response[4:4+length]
    
    if cmd == 0x01:  # GET_SETTINGS response (V1)
        return parse_settings_v1(data)
    elif cmd == 0x09:  # GET_SETTINGS response (V2)
        return parse_settings_v2(data)
    elif cmd == 0x11:  # GET_SETTINGS response (V2.1)
        return parse_settings_v21(data)
    elif cmd == Configuration.SA_CMD_SET_POWER:
        return f"Power set to {data[0]}"
    elif cmd == Configuration.SA_CMD_SET_CHANNEL:
        return f"Channel set to {data[0]}"
    elif cmd == Configuration.SA_CMD_SET_FREQUENCY:
        freq = (data[0] << 8) | data[1]
        return f"Frequency set to {freq} MHz"
    elif cmd == Configuration.SA_CMD_SET_MODE:
        return f"Mode set to {data[0]:08b}"
    else:
        return f"Unknown command: {cmd:02X}"


def parse_settings_v1(data):
    """Parse a V1 GET_SETTINGS response."""
    if len(data) < 5:
        return "Invalid V1 settings data"
    
    channel = data[0]
    power = data[1]
    mode = data[2]
    freq = (data[3] << 8) | data[4]
    
    return (
        f"SmartAudio V1 Settings:\n"
        f"  Channel: {channel}\n"
        f"  Power: {power}\n"
        f"  Mode: {mode:08b}\n"
        f"  Frequency: {freq} MHz"
    )


def parse_settings_v2(data):
    """Parse a V2 GET_SETTINGS response."""
    if len(data) < 5:
        return "Invalid V2 settings data"
    
    channel = data[0]
    power = data[1]
    mode = data[2]
    freq = (data[3] << 8) | data[4]
    
    return (
        f"SmartAudio V2 Settings:\n"
        f"  Channel: {channel}\n"
        f"  Power: {power}\n"
        f"  Mode: {mode:08b}\n"
        f"  Frequency: {freq} MHz"
    )


def parse_settings_v21(data):
    """Parse a V2.1 GET_SETTINGS response."""
    if len(data) < 7:
        return "Invalid V2.1 settings data"
    
    channel = data[0]
    power = data[1]
    mode = data[2]
    freq = (data[3] << 8) | data[4]
    power_dbm = data[5]
    num_levels = data[6]
    
    power_levels = []
    for i in range(num_levels):
        if 7 + i < len(data):
            power_levels.append(data[7 + i])
    
    return (
        f"SmartAudio V2.1 Settings:\n"
        f"  Channel: {channel}\n"
        f"  Power: {power}\n"
        f"  Mode: {mode:08b}\n"
        f"  Frequency: {freq} MHz\n"
        f"  Power (dBm): {power_dbm}\n"
        f"  Power Levels: {power_levels}"
    )


def run_client():
    """Connect to the VTX Emulator and send commands."""
    # Connect to the VTX Emulator
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        server_addr = f"{Configuration.TCP_IP}:{Configuration.TCP_PORT}"
        print(f"Connecting to {server_addr}...")
        sock.connect((Configuration.TCP_IP, Configuration.TCP_PORT))
        print("Connected!")
        
        # Send GET_SETTINGS command
        print("\nSending GET_SETTINGS command...")
        packet = create_get_settings_packet()
        sock.sendall(packet)
        
        # Receive response
        response = sock.recv(1024)
        print(f"Received: {response.hex()}")
        print(parse_response(response))
        
        # Wait a bit
        time.sleep(1)
        
        # Send SET_POWER command
        print("\nSending SET_POWER command (power level 2)...")
        packet = create_set_power_packet(2)
        sock.sendall(packet)
        
        # Receive response
        response = sock.recv(1024)
        print(f"Received: {response.hex()}")
        print(parse_response(response))
        
        # Wait a bit
        time.sleep(1)
        
        # Send GET_SETTINGS command again to verify the change
        print("\nSending GET_SETTINGS command again...")
        packet = create_get_settings_packet()
        sock.sendall(packet)
        
        # Receive response
        response = sock.recv(1024)
        print(f"Received: {response.hex()}")
        print(parse_response(response))
        
    except ConnectionRefusedError:
        print("Connection refused. Make sure the VTX Emulator is running.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sock.close()
        print("\nConnection closed")


if __name__ == "__main__":
    run_client()
