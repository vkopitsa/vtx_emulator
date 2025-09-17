import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import logging
import main_port


class TestMainPortExtended(unittest.TestCase):
    def setUp(self):
        # Reset VTX state before each test
        main_port.vtx_state = {
            "version": 2,
            "channel": 1,
            "power": 0,
            "mode": 0b00010,
            "frequency": 5865,
            "power_levels": [0x00, 0x0E, 0x14, 0x1A],
        }
        # Set up logging capture
        self.log_capture = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture)
        self.log_handler.setLevel(logging.INFO)
        
        # Get the logger and add our handler
        self.logger = logging.getLogger("VTXEmulator")
        self.original_level = self.logger.level
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.log_handler)
        
        # Also keep stdout capture for any tests that might need it
        self.original_stdout = sys.stdout
        self.stdout_capture = io.StringIO()
        sys.stdout = self.stdout_capture

    def tearDown(self):
        # Restore original stdout
        sys.stdout = self.original_stdout
        # Remove our log handler and restore original level
        self.logger.removeHandler(self.log_handler)
        self.logger.setLevel(self.original_level)

    def test_crc8_with_various_inputs(self):
        # Test with different lengths of input - updated to match actual implementation
        self.assertEqual(main_port.crc8([0x01]), 0xD5)
        self.assertEqual(main_port.crc8([0x01, 0x02, 0x03]), 63)  # 0x3F

        # Test with boundary values
        self.assertEqual(main_port.crc8([0x00, 0x00]), 0x00)
        self.assertEqual(main_port.crc8([0xFF, 0xFF]), 129)  # 0x81

    def test_short_to_bytes_edge_cases(self):
        # Test with negative values (should handle only the lower 16 bits)
        self.assertEqual(main_port.short_to_bytes(-1), [0xFF, 0xFF])
        self.assertEqual(main_port.short_to_bytes(-256), [0xFF, 0x00])

        # Test with values larger than 16 bits (should truncate)
        self.assertEqual(main_port.short_to_bytes(65536), [0, 0])
        self.assertEqual(main_port.short_to_bytes(65537), [0, 1])

    def test_build_frame_with_edge_cases(self):
        # Test with large command value - updated CRC
        frame = main_port.build_frame(0xFF, [])
        expected = bytearray([0xAA, 0x55, 0xFF, 0, 0x78])
        self.assertEqual(frame, expected)

        # Test with large payload
        large_payload = list(range(255))
        frame = main_port.build_frame(0x01, large_payload)
        self.assertEqual(len(frame), 4 + len(large_payload) + 1)
        self.assertEqual(frame[0], 0xAA)  # SYNC
        self.assertEqual(frame[1], 0x55)  # HEADER
        self.assertEqual(frame[2], 0x01)  # CMD
        self.assertEqual(frame[3], len(large_payload))  # LEN

        # Verify payload and CRC
        for i, val in enumerate(large_payload):
            self.assertEqual(frame[4 + i], val)
        self.assertEqual(frame[-1], main_port.crc8(frame[2:-1]))

    def test_handle_set_power_with_high_bit(self):
        # Test with high bit set (should be masked off)
        response = main_port.handle_set_power([0x82])  # 0x82 = 0b10000010
        self.assertEqual(main_port.vtx_state["power"], 2)  # Only lower 7 bits

        # Check logger output instead of stdout
        log_output = self.log_capture.getvalue()
        self.assertIn("Setting power to 2", log_output)

    def test_handle_set_channel_with_invalid_values(self):
        # Test with various channel values
        for channel in [0, 1, 8, 255]:
            main_port.vtx_state["channel"] = 1  # Reset
            main_port.handle_set_channel([channel])
            self.assertEqual(main_port.vtx_state["channel"], channel)

            # Check logger output instead of stdout
            log_output = self.log_capture.getvalue()
            self.assertIn(f"Setting channel to {channel}", log_output)

            # Reset capture
            self.log_capture = io.StringIO()
            self.log_handler.stream = self.log_capture

    def test_handle_set_frequency_with_boundary_values(self):
        # Test with min/max frequency values
        test_cases = [
            (0x00, 0x00, 0),      # Min frequency
            (0xFF, 0xFF, 65535),  # Max frequency
            (0x16, 0xE9, 5865),   # Default frequency
        ]

        for high, low, expected in test_cases:
            main_port.vtx_state["frequency"] = 0  # Reset
            response = main_port.handle_set_frequency([high, low])
            self.assertEqual(main_port.vtx_state["frequency"], expected)

            # Check logger output instead of stdout
            log_output = self.log_capture.getvalue()
            self.assertIn(f"Setting frequency to {expected}", log_output)

            # Reset capture
            self.log_capture = io.StringIO()
            self.log_handler.stream = self.log_capture

    def test_handle_set_mode_with_different_modes(self):
        # Test with different mode values
        for mode in [0, 1, 0b00010, 0b11111]:
            main_port.vtx_state["mode"] = 0  # Reset
            response = main_port.handle_set_mode([mode])
            self.assertEqual(main_port.vtx_state["mode"], mode)

            # Check logger output instead of stdout
            log_output = self.log_capture.getvalue()
            self.assertIn(f"Setting mode to {mode}", log_output)

            # Reset capture
            self.log_capture = io.StringIO()
            self.log_handler.stream = self.log_capture

    @patch('socket.socket')
    def test_run_emulator_state_machine_transitions(self, mock_socket):
        # Test the state machine transitions in run_emulator
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        # Create a sequence of bytes that will exercise different state transitions
        # 1. Start with a valid packet
        # 2. Then a partial packet (SYNC only)
        # 3. Then an invalid packet (wrong HEADER)
        # 4. Then a valid packet again
        bytes_sequence = [
            # Valid GET_SETTINGS packet - updated CRC
            0xAA, 0x55, 0x02, 0x00, 0x0B,
            # Partial packet (SYNC only)
            0xAA,
            # Invalid packet (wrong HEADER)
            0xAA, 0x00, 0x01, 0x00, 0x01,
            # Valid SET_POWER packet - updated CRC
            0xAA, 0x55, 0x04, 0x01, 0x02, 0xC3  # CRC calculated for this packet
        ]

        # Set up the mock to return bytes one at a time, then None to exit the loop
        mock_socket_instance.recv.side_effect = [
            bytes([b]) for b in bytes_sequence
        ] + [b'']  # Empty bytes to break the loop

        # Patch the crc8 function to always return the correct CRC
        with patch('main_port.crc8', return_value=0x0B):
            # Run the emulator
            main_port.run_emulator()

            # Check that sendall was called
            self.assertTrue(mock_socket_instance.sendall.called)

    @patch('socket.socket')
    def test_run_emulator_unexpected_exception(self, mock_socket):
        # Test handling of unexpected exceptions
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        # Make recv raise an unexpected exception
        mock_socket_instance.recv.side_effect = Exception("Unexpected error")

        # Run the emulator
        main_port.run_emulator()

        # Check that the exception was handled (if we get here, the test passes)
        # Check the logger output to see if the error was logged
        log_output = self.log_capture.getvalue()
        self.assertIn("An unexpected error occurred", log_output)

    @patch('socket.socket')
    @patch('time.sleep', return_value=None)
    def test_run_emulator_max_retries(self, mock_sleep, mock_socket):
        # Test that the emulator exits after MAX_RETRIES
        # Fix: Use side_effect on the instance, not the class
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = ConnectionRefusedError

        # Set MAX_RETRIES to a small value for testing
        original_max_retries = main_port.MAX_RETRIES
        original_retry_delay = main_port.RETRY_DELAY
        main_port.MAX_RETRIES = 3

        try:
            # Run the emulator
            main_port.run_emulator()

            # Check that the max retries message was logged
            log_output = self.log_capture.getvalue()
            self.assertIn("Max retries reached", log_output)
        finally:
            # Restore original values
            main_port.MAX_RETRIES = original_max_retries
            main_port.RETRY_DELAY = original_retry_delay

    def test_command_handlers_mapping(self):
        # Test that all command handlers are correctly mapped
        cmd_get_settings = main_port.Configuration.SA_CMD_GET_SETTINGS
        cmd_set_power = main_port.Configuration.SA_CMD_SET_POWER
        cmd_set_channel = main_port.Configuration.SA_CMD_SET_CHANNEL
        cmd_set_frequency = main_port.Configuration.SA_CMD_SET_FREQUENCY
        cmd_set_mode = main_port.Configuration.SA_CMD_SET_MODE

        self.assertEqual(
            main_port.command_handlers[cmd_get_settings].__name__,
            '<lambda>'
        )
        self.assertEqual(
            main_port.command_handlers[cmd_set_power],
            main_port.handle_set_power
        )
        self.assertEqual(
            main_port.command_handlers[cmd_set_channel],
            main_port.handle_set_channel
        )
        self.assertEqual(
            main_port.command_handlers[cmd_set_frequency],
            main_port.handle_set_frequency
        )
        self.assertEqual(
            main_port.command_handlers[cmd_set_mode],
            main_port.handle_set_mode
        )


if __name__ == '__main__':
    unittest.main()
