import unittest
from unittest.mock import patch, MagicMock
import peer


class TestPeerFunctions(unittest.TestCase):

    @patch('peer.threading.Thread')
    @patch('peer.socket.socket')
    def test_login_credentials(self, mock_socket, mock_thread):
        # Define the credentials for testing
        test_username = 'user'
        test_password = 'pass'
        test_server_port = 8000
        test_udp_port = 9000

        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.return_value = b'login-success'  # Simulate a successful login response

        result = peer.login(test_username, test_password, test_server_port, test_udp_port)

        # Ensure no real network operations are performed
        mock_socket_instance.bind.assert_not_called()
        mock_socket_instance.listen.assert_not_called()


if __name__ == '__main__':
    unittest.main()
