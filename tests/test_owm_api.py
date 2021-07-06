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
import json
import os
import sys
import unittest

from requests_cache.response import Response

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

VALID_QUERY_NO_UNITS = {"lat": "47.6769",
                        "lng": "-122.2060"}

INVALID_QUERY = {}


class TestOpenWeatherAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = OpenWeatherAPI()

    def test_valid_api_query(self):
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "metric")
        self.assertIsInstance(resp, Response)
        self.assertTrue(resp.ok)
        self.assertIsInstance(resp.json(), dict)

    def test_valid_api_cached_query(self):
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "metric")
        self.assertIsInstance(resp, Response)
        self.assertFalse(resp.from_cache)
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "metric")
        self.assertIsInstance(resp, Response)
        self.assertTrue(resp.from_cache)

    def test_valid_api_expired_cache_query(self):
        self.api.cache_timeout = 0
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "imperial")
        self.assertIsInstance(resp, Response)
        self.assertFalse(resp.from_cache)
        resp = self.api._get_api_response(VALID_LAT, VALID_LNG, "imperial")
        self.assertIsInstance(resp, Response)
        self.assertTrue(resp.from_cache)
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
