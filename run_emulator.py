#!/usr/bin/env python3
"""
Script to run the VTX Emulator with command-line arguments.

Usage:
    python run_emulator.py [options]

Options:
    --ip IP             Server IP address (default: 0.0.0.0)
    --port PORT         Server port (default: 5762)
    --version VERSION   SmartAudio version (1, 2, or 3 for V2.1) (default: 2)
    --channel CHANNEL   Initial channel (default: 1)
    --power POWER       Initial power level (default: 0)
    --frequency FREQ    Initial frequency in MHz (default: 5865)
    --retries RETRIES   Maximum connection retries (default: 5000)
    --delay DELAY       Initial retry delay in seconds (default: 1)
    --help              Show this help message and exit
"""

import argparse
from main_port import VTXEmulator, VTXState


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the VTX Emulator with custom settings"
    )
    
    parser.add_argument(
        "--ip", 
        default="0.0.0.0",
        help="Server IP address (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=5762,
        help="Server port (default: 5762)"
    )
    
    parser.add_argument(
        "--version", 
        type=int, 
        choices=[1, 2, 3], 
        default=2,
        help="SmartAudio version (1, 2, or 3 for V2.1) (default: 2)"
    )
    
    parser.add_argument(
        "--channel", 
        type=int, 
        default=1,
        help="Initial channel (default: 1)"
    )
    
    parser.add_argument(
        "--power", 
        type=int, 
        default=0,
        help="Initial power level (default: 0)"
    )
    
    parser.add_argument(
        "--frequency", 
        type=int, 
        default=5865,
        help="Initial frequency in MHz (default: 5865)"
    )
    
    parser.add_argument(
        "--retries", 
        type=int, 
        default=5000,
        help="Maximum connection retries (default: 5000)"
    )
    
    parser.add_argument(
        "--delay", 
        type=float, 
        default=1.0,
        help="Initial retry delay in seconds (default: 1.0)"
    )
    
    return parser.parse_args()


def run_emulator_with_args():
    """Run the VTX emulator with command-line arguments."""
    args = parse_args()
    
    # Create a custom VTX state
    vtx_state = VTXState()
    vtx_state.version = args.version
    vtx_state.channel = args.channel
    vtx_state.power = args.power
    vtx_state.frequency = args.frequency
    
    # Create an emulator instance
    emulator = VTXEmulator()
    
    # Replace the default state with our custom state
    emulator.vtx_state = vtx_state
    
    # Customize configuration
    emulator.config.TCP_IP = args.ip
    emulator.config.TCP_PORT = args.port
    emulator.config.MAX_RETRIES = args.retries
    emulator.config.RETRY_DELAY = args.delay
    
    # Print configuration
    print("Starting VTX Emulator with the following configuration:")
    print(f"- IP Address: {emulator.config.TCP_IP}")
    print(f"- Port: {emulator.config.TCP_PORT}")
    print(f"- SmartAudio Version: {vtx_state.version}")
    print(f"- Channel: {vtx_state.channel}")
    print(f"- Power Level: {vtx_state.power}")
    print(f"- Frequency: {vtx_state.frequency} MHz")
    print(f"- Max Retries: {emulator.config.MAX_RETRIES}")
    print(f"- Initial Retry Delay: {emulator.config.RETRY_DELAY} seconds")
    print("\nPress Ctrl+C to stop the emulator")
    
    try:
        # Run the emulator
        emulator.run()
    except KeyboardInterrupt:
        print("\nEmulator stopped by user")


if __name__ == "__main__":
    run_emulator_with_args()
