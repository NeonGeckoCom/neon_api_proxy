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

import json
import os
import sys
import unittest

from requests import Response

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_api_proxy.owm_api import OpenWeatherAPI

VALID_LAT = "47.4797"
VALID_LNG = "-122.2079"

INVALID_LAT = "a"
INVALID_LNG = "b"

# KIRKLAND_LAT = "47.6769"
# KIRKLAND_LNG = "-122.2060"

VALID_QUERY = {"lat": "47.6769",
               "lng": "-122.2060",
               "units": "imperial"}

VALID_QUERY_ONECALL = {"lat": "47.6769",
                       "lng": "-122.2060",
                       "units": "imperial",
                       "api": "onecall"}

VALID_QUERY_CURRENT = {"lat": "47.6769",
                       "lng": "-122.2060",
                       "units": "imperial",
                       "api": "weather"}

VALID_QUERY_NO_UNITS = {"lat": "47.6769",
                        "lng": "-122.2060"}

INVALID_QUERY = {}


class TestOpenWeatherAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = OpenWeatherAPI()

    def test_valid_api_query(self):
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "metric")
        # self.assertIsInstance(resp, Response)
        self.assertTrue(resp.ok)
        self.assertIsInstance(resp.json(), dict)

    def test_valid_api_cached_query(self):
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "metric")
        # self.assertIsInstance(resp, Response)
        self.assertFalse(resp.from_cache)
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "metric")
        # self.assertIsInstance(resp, Response)
        self.assertTrue(resp.from_cache)

    def test_valid_api_expired_cache_query(self):
        self.api.cache_timeout = 0
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "imperial")
        self.assertIsInstance(resp, Response)
        self.assertFalse(resp.from_cache)
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "imperial")
        self.assertIsInstance(resp, Response)
        self.assertFalse(resp.from_cache)
        self.api.cache_timeout = 180

    def test_invalid_api_query(self):
        with self.assertRaises(ValueError):
            self.api._get_api_response(INVALID_LAT, INVALID_LNG, "metric")

    def test_handle_query_valid(self):
        resp = self.api.handle_query(**VALID_QUERY)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 200)
        self.assertEqual(resp["encoding"], "utf-8")
        self.assertIsInstance(json.loads(resp["content"]), dict)

    def test_handle_query_valid_onecall(self):
        resp = self.api.handle_query(**VALID_QUERY_ONECALL)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 200)
        self.assertEqual(resp["encoding"], "utf-8")
        self.assertIsInstance(json.loads(resp["content"]), dict)

        spanish = self.api.handle_query(**VALID_QUERY_ONECALL, lang="es")
        self.assertIsInstance(spanish, dict)
        self.assertEqual(spanish["status_code"], 200)
        self.assertEqual(spanish["encoding"], "utf-8")
        self.assertIsInstance(json.loads(spanish["content"]), dict)
        self.assertNotEqual(spanish, resp)

    def test_handle_query_valid_current(self):
        resp = self.api.handle_query(**VALID_QUERY_CURRENT)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 200)
        self.assertEqual(resp["encoding"], "utf-8")
        self.assertIsInstance(json.loads(resp["content"]), dict)

    def test_handle_query_valid_no_units(self):
        resp = self.api.handle_query(**VALID_QUERY_NO_UNITS)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 200)
        self.assertEqual(resp["encoding"], "utf-8")
        self.assertIsInstance(json.loads(resp["content"]), dict)

    def test_handle_query_invalid(self):
        resp = self.api.handle_query(**INVALID_QUERY)
        self.assertIsInstance(resp, dict)
        self.assertNotEqual(resp["status_code"], 200)


if __name__ == '__main__':
    unittest.main()
