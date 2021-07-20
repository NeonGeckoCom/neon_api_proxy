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
import json

from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_api_proxy.controller import NeonAPIProxyController

INVALID_SERVICE_QUERY = {
    "service": "invalid_service",
    "query": "how far away is Rome?",
    "api": "simple",
    "units": "metric",
    "ip": "64.34.186.120"
}

VALID_ALPHA_VANTAGE_QUERY = {
    "service": "alpha_vantage",
    "api": "quote",
    "symbol": "GOOGL"
}

VALID_OWM_QUERY = {
    "service": "open_weather_map",
    "lat": "47.6769",
    "lng": "-122.2060",
    "units": "imperial"
}

VALID_WOLFRAM_QUERY = {
    "service": "wolfram_alpha",
    "query": "how far away is Rome?",
    "api": "simple",
    "units": "metric",
    "ip": "64.34.186.120"
}


class TestGenericController(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.file_path = os.path.expanduser(os.environ.get('NEON_API_PROXY_CONFIG_PATH',
                                                          "~/.local/share/neon/credentials.json"))

        with open(os.path.expanduser(cls.file_path)) as input_file:
            cls._config_data = json.load(input_file)
        cls.controller = NeonAPIProxyController(config=cls._config_data)

    def test_invalid_service(self):
        resp = self.controller.resolve_query(INVALID_SERVICE_QUERY)
        self.assertIsNotNone(resp)
        self.assertEqual(resp['status_code'], 401)

    def test_alpha_vantage_forwarding(self):
        resp = self.controller.resolve_query(VALID_ALPHA_VANTAGE_QUERY)
        self.assertIsNotNone(resp)
        self.assertEqual(resp['status_code'], 200)

    def test_owm_forwarding(self):
        resp = self.controller.resolve_query(VALID_OWM_QUERY)
        self.assertIsNotNone(resp)
        self.assertEqual(resp['status_code'], 200)

    def test_wolfram_forwarding(self):
        resp = self.controller.resolve_query(VALID_WOLFRAM_QUERY)
        self.assertIsNotNone(resp)
        self.assertEqual(resp['status_code'], 200)


if __name__ == '__main__':
    unittest.main()
