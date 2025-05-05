# Contributing to VTX Emulator

Thank you for considering contributing to VTX Emulator! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue with the following information:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any additional context (screenshots, logs, etc.)

### Suggesting Enhancements

If you have ideas for enhancements, please create an issue with:

- A clear, descriptive title
- A detailed description of the enhancement
- Any relevant examples or mockups
- Explanation of why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests to ensure they pass
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/vkopitsa/vtx_emulator.git
   cd vtx_emulator
   ```

2. Set up a virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Run the tests
   ```bash
   python -m unittest test_main_port.py
   python -m unittest test_main_port_extended.py
   ```

## Coding Guidelines

- Follow PEP 8 style guidelines
- Write docstrings for all functions, classes, and methods
- Include comments for complex code sections
- Write unit tests for new functionality

## Testing

- All new features should include appropriate tests
- All tests must pass before a pull request will be accepted
- Run the existing tests to ensure your changes don't break existing functionality

## Documentation

- Update the README.md if your changes affect usage or installation
- Document new features or changes in behavior

## Questions?

If you have any questions about contributing, please create an issue with your question.

Thank you for your contributions!
