#!/usr/bin/env python3
"""
Example script demonstrating how to use the VTX Emulator with custom 
configuration.

This script shows how to:
1. Import the VTX Emulator classes
2. Create a custom VTX configuration
3. Run the emulator with the custom configuration
"""

import sys
import os

try:
    # Try to import directly
    from main_port import VTXEmulator, VTXState
except ImportError:
    # If that fails, add the parent directory to the path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)
    from main_port import VTXEmulator, VTXState


def run_custom_emulator():
    """Run the VTX emulator with custom configuration."""
    # Create a custom VTX state
    vtx_state = VTXState()
    vtx_state.version = 3  # SmartAudio V2.1
    vtx_state.channel = 2  # Channel 2
    vtx_state.power = 1    # Power level 1
    vtx_state.frequency = 5800  # 5.8 GHz
    # Custom power levels (in dBm)
    vtx_state.power_levels = [0x00, 0x0E, 0x14, 0x1A, 0x20]

    # Create an emulator instance
    emulator = VTXEmulator()
    
    # Replace the default state with our custom state
    emulator.vtx_state = vtx_state
    
    # Customize configuration
    emulator.config.TCP_PORT = 5763  # Use a different port
    emulator.config.MAX_RETRIES = 10  # Fewer retries for testing
    
    # Run the emulator
    print("Starting VTX Emulator with custom configuration:")
    print(f"- Version: {vtx_state.version}")
    print(f"- Channel: {vtx_state.channel}")
    print(f"- Power: {vtx_state.power}")
    print(f"- Frequency: {vtx_state.frequency} MHz")
    print(f"- Power Levels: {vtx_state.power_levels}")
    print(f"- TCP Port: {emulator.config.TCP_PORT}")
    print(f"- Max Retries: {emulator.config.MAX_RETRIES}")
    print("\nPress Ctrl+C to stop the emulator")
    
    try:
        emulator.run()
    except KeyboardInterrupt:
        print("\nEmulator stopped by user")


if __name__ == "__main__":
    run_custom_emulator()
