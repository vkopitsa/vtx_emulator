# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation for using the emulator with INAV and BetaFlight in SITL mode
- Initial implementation of VTX emulator
- Support for SmartAudio protocol versions 1, 2, and 2.1
- Support for all standard SmartAudio commands (GET_SETTINGS, SET_POWER, SET_CHANNEL, SET_FREQUENCY, SET_MODE)
- Proper CRC-8 validation
- Connection retry mechanism with exponential backoff
- Comprehensive logging
- Unit tests
- Example scripts
- Documentation
- Docker support
- GitHub Actions workflow for CI
- Makefile for common tasks
- Command-line interface for customizing emulator settings
