# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import os
import sys
import unittest
import socket

from neon_utils.socket_utils import *
from neon_utils.logger import LOG

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_api_proxy.tcp_server import start_server, stop_server

VALID_WOLFRAM_QUERY = {
    "service": "wolfram_alpha",
    "query": "how far away is Rome?",
    "api": "simple",
    "units": "metric",
    "ip": "64.34.186.120"
}


class TestTCPSocket(unittest.TestCase):
    """Hereby we presume that there is an active socket service running"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = start_server('127.0.0.1', 8555, dict())
        cls.host = os.environ.get('host', '127.0.0.1')  # The server's hostname or IP address
        cls.port = os.environ.get('port', 8555)  # The server's port

    @classmethod
    def tearDownClass(cls) -> None:
        stop_server()

    def test_valid_wolfram_query(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            connected = False
            data = None
            while not connected:
                try:
                    s.connect((self.host, self.port))
                    connected = True
                except ConnectionRefusedError:
                    LOG.error("Connection refused!")
            while not data:
                try:
                    s.sendall(dict_to_b64(VALID_WOLFRAM_QUERY))
                except BrokenPipeError:
                    LOG.error("Socket broken pipe!")
                try:
                    data = get_packet_data(s, True)
                except ConnectionResetError:
                    LOG.error("Socket connection reset!")
            self.assertIsNotNone(data)
            converted_data = b64_to_dict(data)
            self.assertIsInstance(converted_data, dict)
            self.assertEqual(converted_data["status_code"], 200)
            self.assertTrue(b'wolfram' in converted_data['content'])


if __name__ == '__main__':
    unittest.main()
