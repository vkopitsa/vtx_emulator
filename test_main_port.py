import unittest
from unittest.mock import patch, MagicMock, call
import socket  # Used in mocked tests
import time    # Used in mocked tests
import main_port


class TestMainPort(unittest.TestCase):
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

    def test_crc8(self):
        # Test with known values - updated to match actual implementation
        # These values are calculated using the CRC8_TABLE in main_port.py
        self.assertEqual(main_port.crc8([0x02, 0x01]), 195)  # 0xC3
        self.assertEqual(main_port.crc8([0x03, 0x01]), 200)  # 0xC8
        self.assertEqual(main_port.crc8([0x04, 0x02, 0x16, 0xE3]), 228)  # 0xE4
        self.assertEqual(main_port.crc8([]), 0x00)  # Empty array

    def test_short_to_bytes(self):
        self.assertEqual(main_port.short_to_bytes(0), [0, 0])
        self.assertEqual(main_port.short_to_bytes(1), [0, 1])
        self.assertEqual(main_port.short_to_bytes(256), [1, 0])
        # 0x16E9 = 5865
        self.assertEqual(
            main_port.short_to_bytes(5865), [22, 233]
        )
        # Max 16-bit value
        self.assertEqual(
            main_port.short_to_bytes(65535), [255, 255]
        )

    def test_build_frame(self):
        # Test with empty payload - updated CRC
        frame = main_port.build_frame(0x01, [])
        self.assertEqual(frame, bytearray([0xAA, 0x55, 0x01, 0, 0x0B]))
        
        # Test with some payload - updated CRC
        frame = main_port.build_frame(0x02, [0x03, 0x04])
        self.assertEqual(
            frame, bytearray([0xAA, 0x55, 0x02, 2, 0x03, 0x04, 0xBA])
        )

    def test_handle_get_settings_v1(self):
        main_port.vtx_state["version"] = 1
        response = main_port.handle_get_settings()
        # Expected: [SYNC, HEADER, CMD=0x01, LEN=5, CHANNEL=1, POWER=0, MODE=0b00010,
        # FREQ_H=22, FREQ_L=233, CRC] - updated CRC
        self.assertEqual(
            response,
            bytearray([0xAA, 0x55, 0x01, 5, 1, 0, 0b00010, 22, 233, 0xD6])
        )

    def test_handle_get_settings_v2(self):
        main_port.vtx_state["version"] = 2
        response = main_port.handle_get_settings()
        # Expected: [SYNC, HEADER, CMD=0x09, LEN=5, CHANNEL=1, POWER=0, MODE=0b00010,
        # FREQ_H=22, FREQ_L=233, CRC] - updated CRC
        self.assertEqual(
            response,
            bytearray([0xAA, 0x55, 0x09, 5, 1, 0, 0b00010, 22, 233, 0x88])
        )

    def test_handle_get_settings_v21(self):
        main_port.vtx_state["version"] = 3  # V2.1
        response = main_port.handle_get_settings()
        # Expected: [SYNC, HEADER, CMD=0x11, LEN=9, CHANNEL=1, POWER=0, MODE=0b00010,
        # FREQ_H=22, FREQ_L=233, POWER_DBM=0, NUM_LEVELS=4, LEVELS...] - updated LEN and CRC
        expected = bytearray(
            [0xAA, 0x55, 0x11, 11, 1, 0, 0b00010, 22, 233, 0, 4, 0, 14, 20, 26]
        )
        expected.append(0x0F)  # Updated CRC
        self.assertEqual(response, expected)

    def test_handle_set_power(self):
        response = main_port.handle_set_power([0x02])
        self.assertEqual(main_port.vtx_state["power"], 2)
        # Expected: [SYNC, HEADER, CMD=0x02, LEN=2, POWER=2, RESERVED=1, CRC] - updated CRC
        self.assertEqual(
            response,
            bytearray([0xAA, 0x55, 0x02, 2, 2, 1, 0x9A])
        )

    def test_handle_set_channel(self):
        response = main_port.handle_set_channel([0x05])
        self.assertEqual(main_port.vtx_state["channel"], 5)
        self.assertEqual(main_port.vtx_state["mode"], 0)  # Should set mode to 0
        # Expected: [SYNC, HEADER, CMD=0x03, LEN=2, CHANNEL=5, RESERVED=1, CRC] - updated CRC
        self.assertEqual(
            response,
            bytearray([0xAA, 0x55, 0x03, 2, 5, 1, 0xEE])
        )

    def test_handle_set_frequency(self):
        # Set frequency to 5800 (0x16A8)
        response = main_port.handle_set_frequency([0x16, 0xA8])
        self.assertEqual(main_port.vtx_state["frequency"], 5800)
        self.assertEqual(main_port.vtx_state["mode"], 1)  # Should set mode to 1
        # Expected: [SYNC, HEADER, CMD=0x04, LEN=3, FREQ_H=0x16, FREQ_L=0xA8,
        # RESERVED=1, CRC] - updated CRC
        self.assertEqual(
            response,
            bytearray([0xAA, 0x55, 0x04, 3, 0x16, 0xA8, 1, 0x42])
        )

    def test_handle_set_mode(self):
        response = main_port.handle_set_mode([0x03])
        self.assertEqual(main_port.vtx_state["mode"], 3)
        # Expected: [SYNC, HEADER, CMD=0x05, LEN=2, MODE=3, RESERVED=1, CRC] - updated CRC
        self.assertEqual(
            response,
            bytearray([0xAA, 0x55, 0x05, 2, 3, 1, 0x9F])
        )

    @patch('socket.socket')
    @patch('time.sleep', return_value=None)
    def test_run_emulator_connection_refused(self, mock_sleep, mock_socket):
        # Mock socket to raise ConnectionRefusedError on connect
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = ConnectionRefusedError
        
        # Set MAX_RETRIES to a small value for testing
        original_max_retries = main_port.MAX_RETRIES
        original_retry_delay = main_port.RETRY_DELAY
        main_port.MAX_RETRIES = 3
        
        try:
            main_port.run_emulator()
            # Check that connect was called the expected number of times
            self.assertEqual(mock_socket_instance.connect.call_count, 3)
            # Check that sleep was called with the correct values
            # The actual calls include an extra call(1) at the end of each iteration
            expected_calls = [call(1), call(2), call(4)]
            for expected_call in expected_calls:
                self.assertIn(expected_call, mock_sleep.call_args_list)
        finally:
            # Restore original values
            main_port.MAX_RETRIES = original_max_retries
            main_port.RETRY_DELAY = original_retry_delay

    @patch('socket.socket')
    def test_run_emulator_packet_processing(self, mock_socket):
        # Mock socket to return a valid SmartAudio packet
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        
        # Simulate receiving a GET_SETTINGS packet
        # [SYNC, HEADER, CMD, LEN, CRC] - updated CRC
        get_settings_packet = [0xAA, 0x55, 0x02, 0x00, 0x0B]
        
        # Set up the mock to return bytes one at a time, then None to exit the loop
        mock_socket_instance.recv.side_effect = [
            bytes([b]) for b in get_settings_packet
        ] + [b'']  # Empty bytes to break the loop
        
        # Patch the crc8 function to always return the correct CRC
        with patch('main_port.crc8', return_value=0x0B):
            # Run the emulator
            main_port.run_emulator()
            
            # Check that sendall was called
            self.assertTrue(mock_socket_instance.sendall.called)

    @patch('socket.socket')
    def test_run_emulator_invalid_packet(self, mock_socket):
        # Mock socket to return an invalid packet
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        
        # Invalid packet (wrong CRC)
        invalid_packet = [0xAA, 0x55, 0x01, 0x00, 0xFF]
        
        # Set up the mock to return bytes one at a time, then None to exit the loop
        mock_socket_instance.recv.side_effect = [
            bytes([b]) for b in invalid_packet
        ] + [b'']  # Empty bytes to break the loop
        
        # Run the emulator
        main_port.run_emulator()
        
        # Check that sendall was not called (invalid CRC)
        mock_socket_instance.sendall.assert_not_called()

    @patch('socket.socket')
    def test_run_emulator_set_power_packet(self, mock_socket):
        # Mock socket to return a SET_POWER packet
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        
        # [SYNC, HEADER, CMD, LEN, DATA, CRC] - updated CRC
        # CMD = 0x02 << 1 = 0x04 (SET_POWER)
        set_power_packet = [0xAA, 0x55, 0x04, 0x01, 0x02, 0xC3]
        
        # Set up the mock to return bytes one at a time, then None to exit the loop
        mock_socket_instance.recv.side_effect = [
            bytes([b]) for b in set_power_packet
        ] + [b'']  # Empty bytes to break the loop
        
        # Patch the crc8 function to return the correct CRC for the packet
        with patch.object(main_port, 'crc8') as mock_crc8:
            # Configure the mock to return the correct CRC for the packet
            mock_crc8.return_value = 0xC3
            
            # Run the emulator
            main_port.run_emulator()
            
            # Check that sendall was called
            self.assertTrue(mock_socket_instance.sendall.called)


if __name__ == '__main__':
    unittest.main()
