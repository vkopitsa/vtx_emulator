# SmartAudio Protocol Documentation

This document provides an overview of the SmartAudio protocol as implemented in the VTX Emulator.

## Overview

SmartAudio is a serial protocol developed by TBS (Team BlackSheep) for controlling Video Transmitters (VTX) in FPV (First Person View) drones. It allows flight controllers to change VTX settings such as channel, power level, and frequency.

## Protocol Versions

The VTX Emulator supports three versions of the SmartAudio protocol:

- **Version 1**: Basic functionality
- **Version 2**: Improved functionality
- **Version 2.1**: Extended functionality with power level information

## Packet Format

### Command Packet (Flight Controller to VTX)

```
[SYNC_BYTE][HEADER_BYTE][COMMAND][LENGTH][DATA...][CRC]
```

- `SYNC_BYTE`: 0xAA
- `HEADER_BYTE`: 0x55
- `COMMAND`: Command ID (may be shifted left by 1 bit in some implementations)
- `LENGTH`: Length of the data section
- `DATA`: Command-specific data
- `CRC`: CRC-8 checksum (polynomial 0xD5)

### Response Packet (VTX to Flight Controller)

```
[SYNC_BYTE][HEADER_BYTE][COMMAND][LENGTH][DATA...][CRC]
```

- `SYNC_BYTE`: 0xAA
- `HEADER_BYTE`: 0x55
- `COMMAND`: Command ID (varies by version for GET_SETTINGS)
- `LENGTH`: Length of the data section
- `DATA`: Response-specific data
- `CRC`: CRC-8 checksum (polynomial 0xD5)

## Commands

### GET_SETTINGS (0x01)

Requests the current VTX settings.

**Command Packet:**
```
[0xAA][0x55][0x01][0x00][0x0B]
```

**Response Packet (V1):**
```
[0xAA][0x55][0x01][0x05][CHANNEL][POWER][MODE][FREQ_H][FREQ_L][CRC]
```

**Response Packet (V2):**
```
[0xAA][0x55][0x09][0x05][CHANNEL][POWER][MODE][FREQ_H][FREQ_L][CRC]
```

**Response Packet (V2.1):**
```
[0xAA][0x55][0x11][0x0B][CHANNEL][POWER][MODE][FREQ_H][FREQ_L][POWER_DBM][NUM_LEVELS][LEVELS...][CRC]
```

### SET_POWER (0x02)

Sets the VTX power level.

**Command Packet:**
```
[0xAA][0x55][0x04][0x01][POWER][CRC]
```
Note: The command is shifted left by 1 bit (0x02 << 1 = 0x04)

**Response Packet:**
```
[0xAA][0x55][0x02][0x02][POWER][RESERVED][CRC]
```

### SET_CHANNEL (0x03)

Sets the VTX channel.

**Command Packet:**
```
[0xAA][0x55][0x06][0x01][CHANNEL][CRC]
```
Note: The command is shifted left by 1 bit (0x03 << 1 = 0x06)

**Response Packet:**
```
[0xAA][0x55][0x03][0x02][CHANNEL][RESERVED][CRC]
```

### SET_FREQUENCY (0x04)

Sets the VTX frequency directly.

**Command Packet:**
```
[0xAA][0x55][0x08][0x02][FREQ_H][FREQ_L][CRC]
```
Note: The command is shifted left by 1 bit (0x04 << 1 = 0x08)

**Response Packet:**
```
[0xAA][0x55][0x04][0x03][FREQ_H][FREQ_L][RESERVED][CRC]
```

### SET_MODE (0x05)

Sets the VTX mode (e.g., pit mode).

**Command Packet:**
```
[0xAA][0x55][0x0A][0x01][MODE][CRC]
```
Note: The command is shifted left by 1 bit (0x05 << 1 = 0x0A)

**Response Packet:**
```
[0xAA][0x55][0x05][0x02][MODE][RESERVED][CRC]
```

## Mode Bits

The MODE byte contains several flags:

- Bit 0: Frequency mode (0 = channel, 1 = frequency)
- Bit 1: Pit mode (0 = normal, 1 = pit mode)
- Bit 2: In Range (0 = out of range, 1 = in range)
- Bit 3: Unlocked (0 = locked, 1 = unlocked)
- Bit 4: VTX Type (0 = A, 1 = B)

## CRC-8 Calculation

The CRC-8 checksum is calculated using polynomial 0xD5. The calculation starts from the COMMAND byte and includes the LENGTH byte and all DATA bytes.

```python
def crc8(data):
    """Compute CRC-8 checksum using polynomial 0xD5."""
    crc = 0
    for byte in data:
        crc = CRC8_TABLE[crc ^ byte]
    return crc
```

## Implementation Notes

- Some implementations of SmartAudio shift the command byte left by 1 bit in the command packet.
- The VTX Emulator handles both shifted and unshifted commands for compatibility.
- The response packet always uses the unshifted command ID.
- The GET_SETTINGS response command ID varies by version:
  - V1: 0x01
  - V2: 0x09
  - V2.1: 0x11
