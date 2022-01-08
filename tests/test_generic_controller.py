# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import unittest
import json

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
