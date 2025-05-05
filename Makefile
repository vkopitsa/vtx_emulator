# VTX Emulator Makefile

.PHONY: run test test-extended install clean docker docker-run docker-compose help

# Default target
help:
	@echo "VTX Emulator Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  run            - Run the VTX emulator with default settings"
	@echo "  run-args       - Run the VTX emulator with command-line arguments"
	@echo "  test           - Run basic unit tests"
	@echo "  test-extended  - Run extended unit tests"
	@echo "  test-all       - Run all unit tests"
	@echo "  install        - Install the package"
	@echo "  clean          - Remove build artifacts and __pycache__ directories"
	@echo "  docker         - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-compose - Run with Docker Compose"
	@echo "  help           - Show this help message"

# Run the emulator
run:
	@echo "Running VTX emulator..."
	@./main_port.py

# Run the emulator with command-line arguments
run-args:
	@echo "Running VTX emulator with command-line arguments..."
	@./run_emulator.py $(ARGS)

# Run basic unit tests
test:
	@echo "Running basic unit tests..."
	@python -m unittest test_main_port.py

# Run extended unit tests
test-extended:
	@echo "Running extended unit tests..."
	@python -m unittest test_main_port_extended.py

# Run all unit tests
test-all:
	@echo "Running all unit tests..."
	@python -m unittest discover

# Install the package
install:
	@echo "Installing VTX emulator..."
	@pip install -e .

# Clean build artifacts and __pycache__ directories
clean:
	@echo "Cleaning build artifacts and __pycache__ directories..."
	@rm -rf build/ dist/ *.egg-info/ __pycache__/ */__pycache__/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete

# Build Docker image
docker:
	@echo "Building Docker image..."
	@docker build -t vtx-emulator .

# Run Docker container
docker-run:
	@echo "Running Docker container..."
	@docker run -p 5762:5762 vtx-emulator

# Run with Docker Compose
docker-compose:
	@echo "Running with Docker Compose..."
	@docker-compose up
