# VTX Emulator

A Python-based emulator for Video Transmitter (VTX) devices that implements the SmartAudio protocol, commonly used in FPV (First Person View) drones.

## Overview

This project provides a software emulation of a VTX device that can respond to SmartAudio protocol commands. It creates a TCP server that listens for incoming SmartAudio commands and responds with appropriate data, mimicking the behavior of a real VTX device.

The SmartAudio protocol is a popular standard used in FPV drones to control video transmitters, allowing flight controllers to change VTX settings such as channel, power level, and frequency.

## Features

- Emulates SmartAudio protocol versions 1, 2, and 2.1
- Supports all standard SmartAudio commands:
  - Get Settings
  - Set Power
  - Set Channel
  - Set Frequency
  - Set Mode
- Implements proper CRC-8 validation
- Handles connection retries with exponential backoff
- Comprehensive logging
- Well-tested with unit tests

## Requirements

- Python 3.6 or higher
- Standard Python libraries (socket, time, logging)

## Installation

### Standard Installation

Clone the repository:

```bash
git clone https://github.com/vkopitsa/vtx_emulator.git
cd vtx_emulator
```

No additional dependencies are required as the project uses only standard Python libraries.

### Docker Installation

The project includes Docker support for easy deployment:

```bash
# Build and run using Docker
docker build -t vtx-emulator .
docker run -p 5762:5762 vtx-emulator

# Or use Docker Compose
docker-compose up
```

You can also use the Makefile for Docker operations:

```bash
# Build Docker image
make docker

# Run Docker container
make docker-run

# Run with Docker Compose
make docker-compose
```

## Usage

### Using with INAV and BetaFlight SITL

The VTX Emulator can be integrated with both INAV and BetaFlight when running in SITL (Software In The Loop) mode, allowing you to test VTX control functionality without physical hardware.

#### INAV SITL Integration

INAV SITL can connect to the VTX Emulator to test SmartAudio communication:

1. Start the VTX Emulator first:
   ```bash
   python run_emulator.py --ip 127.0.0.1 --port 5762
   ```

2. Configure INAV SITL to use the SmartAudio protocol on the appropriate port:
   - In the INAV SITL configuration, set the VTX protocol to SmartAudio
   - Configure the serial port that will communicate with the VTX Emulator
   - Ensure the port matches the one used by the VTX Emulator (default: 5762)

3. Run INAV SITL with the appropriate configuration:
   ```bash
   # Example command (actual command may vary based on your INAV SITL setup)
   ./inav_sitl --serial-device tcp://127.0.0.1:5762 --vtx-protocol smartaudio
   ```

4. Use the INAV Configurator or CLI to change VTX settings, which will be sent to the emulator.

#### BetaFlight SITL Integration

BetaFlight SITL can also be configured to work with the VTX Emulator:

1. Start the VTX Emulator:
   ```bash
   python run_emulator.py --ip 127.0.0.1 --port 5762
   ```

2. Configure BetaFlight SITL:
   - Set the VTX protocol to SmartAudio in the BetaFlight configuration
   - Configure the appropriate UART port for SmartAudio communication
   - Set the port to connect to the VTX Emulator's TCP server

3. Run BetaFlight SITL:
   ```bash
   # Example command (actual command may vary based on your BetaFlight SITL setup)
   ./betaflight_sitl --serial tcp://127.0.0.1:5762 --vtx smartaudio
   ```

4. Use the BetaFlight Configurator to change VTX settings and observe the communication with the emulator.

#### Key Differences Between INAV and BetaFlight Integration

- **Configuration Parameters**: INAV and BetaFlight use slightly different configuration parameters for VTX control.
- **CLI Commands**: The CLI commands for configuring VTX settings differ between INAV and BetaFlight.
- **SmartAudio Implementation**: BetaFlight may use a more recent implementation of the SmartAudio protocol with additional features.
- **Default Ports**: The default serial port assignments may differ between the two firmwares.

For both flight controllers, you can verify the communication by checking the VTX Emulator logs, which will show the received commands and sent responses.

### Running the Emulator

There are several ways to run the VTX emulator:

#### 1. Basic Usage

To start the VTX emulator with default settings:

```bash
python main_port.py
```

Or, if you've made the script executable:

```bash
./main_port.py
```

By default, the emulator will:
- Listen on all interfaces (0.0.0.0)
- Use port 5762
- Attempt to reconnect if the connection is lost

#### 2. With Command-line Arguments

For more flexibility, you can use the `run_emulator.py` script with command-line arguments:

```bash
python run_emulator.py --ip 127.0.0.1 --port 5763 --version 3 --channel 2 --power 1 --frequency 5800
```

Available options:

```
--ip IP             Server IP address (default: 0.0.0.0)
--port PORT         Server port (default: 5762)
--version VERSION   SmartAudio version (1, 2, or 3 for V2.1) (default: 2)
--channel CHANNEL   Initial channel (default: 1)
--power POWER       Initial power level (default: 0)
--frequency FREQ    Initial frequency in MHz (default: 5865)
--retries RETRIES   Maximum connection retries (default: 5000)
--delay DELAY       Initial retry delay in seconds (default: 1)
--help              Show this help message and exit
```

#### 3. Using the Makefile

The project includes a Makefile for common tasks:

```bash
# Run the emulator with default settings
make run

# Run the emulator with command-line arguments
make run-args ARGS="--ip 127.0.0.1 --port 5763"

# Run basic unit tests
make test

# Run extended unit tests
make test-extended

# Run all unit tests
make test-all

# Install the package
make install

# Clean build artifacts
make clean

# Show help
make help
```

### Configuration

You can also modify the settings directly in the `Configuration` class in `main_port.py`:

- `TCP_IP`: Server IP address (default: '0.0.0.0')
- `TCP_PORT`: Server port (default: 5762)
- `RETRY_DELAY`: Initial delay in seconds before retrying (default: 1)
- `MAX_RETRIES`: Maximum number of retries (default: 5000)

### Examples

The `examples/` directory contains scripts demonstrating how to use the emulator:

- `custom_vtx_config.py`: Shows how to use the emulator with custom configuration
- `client_example.py`: Demonstrates how to connect to the emulator and send SmartAudio commands

### Testing

Run the unit tests to verify the emulator's functionality:

```bash
python -m unittest test_main_port.py
python -m unittest test_main_port_extended.py
```

## Protocol Details

### SmartAudio Packet Format

```
[SYNC_BYTE][HEADER_BYTE][COMMAND][LENGTH][DATA...][CRC]
```

- `SYNC_BYTE`: 0xAA
- `HEADER_BYTE`: 0x55
- `COMMAND`: Command ID
- `LENGTH`: Length of the data section
- `DATA`: Command-specific data
- `CRC`: CRC-8 checksum (polynomial 0xD5)

### Supported Commands

| Command | ID | Description |
|---------|------|-------------|
| GET_SETTINGS | 0x01 | Get current VTX settings |
| SET_POWER | 0x02 | Set VTX power level |
| SET_CHANNEL | 0x03 | Set VTX channel |
| SET_FREQUENCY | 0x04 | Set VTX frequency directly |
| SET_MODE | 0x05 | Set VTX mode (e.g., pit mode) |

## Project Structure

- `main_port.py`: Main emulator implementation
- `run_emulator.py`: Script to run the emulator with command-line arguments
- `test_main_port.py`: Basic unit tests
- `test_main_port_extended.py`: Extended unit tests
- `examples/`: Example scripts demonstrating how to use the emulator
  - `custom_vtx_config.py`: Example of using the emulator with custom configuration
  - `client_example.py`: Example client that connects to the emulator
- `docs/`: Documentation
  - `smartaudio_protocol.md`: Detailed documentation of the SmartAudio protocol
- `Makefile`: Makefile for common tasks
- `setup.py`: Setup script for installing the package
- `pyproject.toml`: Configuration for Python tools (Black, isort, pytest)
- `requirements.txt`: List of dependencies (empty as only standard libraries are used)
- `LICENSE`: MIT License file
- `CHANGELOG.md`: Changelog file to track changes
- `CODE_OF_CONDUCT.md`: Code of Conduct for contributors
- `SECURITY.md`: Security policy and vulnerability reporting
- `.gitignore`: Git ignore file
- `.editorconfig`: EditorConfig file for consistent coding styles
- `.dockerignore`: Docker ignore file
- `Dockerfile`: Docker configuration file
- `docker-compose.yml`: Docker Compose configuration file
- `.github/workflows/`: GitHub Actions workflows
  - `python-tests.yml`: Workflow for running tests on GitHub

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project, [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for our code of conduct, and [SECURITY.md](SECURITY.md) for our security policy and how to report security vulnerabilities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The FPV community for developing and documenting the SmartAudio protocol
- All contributors to this project
