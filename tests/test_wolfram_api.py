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

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_api_proxy.wolfram_api import WolframAPI, QueryUrl


VALID_QUERY_IP = {"query": "how far away is Moscow?",
                  "units": "metric",
                  "ip": "50.47.129.133"}

VALID_QUERY_LAT_LON = {"query": "how far away is new york?",
                       "units": "nonmetric",
                       "lat": "47.4797",
                       "lng": "122.2079"}

VALID_QUERY_LAT_LON_IP = {"query": "how far away is Bellevue?",
                          "units": "nonmetric",
                          "lat": "47.4797",
                          "lng": "122.2079",
                          "ip": "50.47.129.133"}

VALID_QUERY_MINIMAL = {"query": "how far away is Miami?"}

INVALID_QUERY = {}

FULL_QUERY = "https://api.wolframalpha.com/v2/query?input=what+time+is+it&format=image,plaintext&output=XML&appid=DEMO"
SIMPLE_QUERY = "https://api.wolframalpha.com/v1/simple?i=Who+is+the+prime+minister+of+India%3F&appid=DEMO"
SPOKEN_QUERY = "https://api.wolframalpha.com/v1/spoken?i=Convert+42+mi+to+km&appid=DEMO"
SHORT_QUERY = "https://api.wolframalpha.com/v1/result?i=How+many+ounces+are+in+a+gallon%3F&appid=DEMO"
CONVERSE_QUERY = "http://api.wolframalpha.com/v1/conversation.jsp?appid=DEMO&i=How+much+does+the+earth+weigh%3f"
RECOGNIZE_QUERY = "https://www.wolframalpha.com/queryrecognizer/query.jsp?mode=Default" \
                  "&i=How+far+away+is+the+Moon%3F&appid=DEMO"


class TestWolframAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = WolframAPI()

    def test_build_query_url_valid(self):
        url = self.api._build_query_url(QueryUrl.SHORT, "i=what+is+this")
        self.assertEqual(url, f"{QueryUrl.SHORT}?appid={self.api._api_key}&i=what+is+this")

    def test_build_query_url_invalid_param_values(self):
        with self.assertRaises(ValueError):
            self.api._build_query_url(QueryUrl.FULL, None)
        with self.assertRaises(ValueError):
            self.api._build_query_url(None, "i=something")

    def test_build_query_url_invalid_param_types(self):
        with self.assertRaises(TypeError):
            self.api._build_query_url("http://api.wolframalpha.com/v2/result", "i=42")

        with self.assertRaises(TypeError):
            self.api._build_query_url(QueryUrl.SHORT, 42)

    def test_build_query_string_valid_minimal(self):
        query_str = self.api._build_query_string(**VALID_QUERY_MINIMAL)
        self.assertEqual(query_str, f"i=how+far+away+is+Miami%3F&units=nonmetric")

    def test_build_query_string_valid_lat_lng(self):
        query_str = self.api._build_query_string(**VALID_QUERY_LAT_LON)
        self.assertEqual(query_str, f"i=how+far+away+is+new+york%3F&units=nonmetric&latlong=47.4797%2C122.2079")

    def test_build_query_string_valid_ip(self):
        query_str = self.api._build_query_string(**VALID_QUERY_IP)
        self.assertEqual(query_str, f"i=how+far+away+is+Moscow%3F&units=metric&ip=50.47.129.133")

    def test_build_query_string_valid_lat_lng_ip(self):
        query_str = self.api._build_query_string(**VALID_QUERY_LAT_LON_IP)
        self.assertEqual(query_str, f"i=how+far+away+is+Bellevue%3F&units=nonmetric&latlong=47.4797%2C122.2079")

    def test_build_query_invalid_query(self):
        with self.assertRaises(ValueError):
            self.api._build_query_string(**INVALID_QUERY)

    def test_query_full_api(self):
        result = self.api._query_api(FULL_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)

    def test_query_simple_api(self):
        result = self.api._query_api(SIMPLE_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"], bytes)
        self.assertIsNone(result["encoding"], result["content"])

    def test_query_spoken_api(self):
        result = self.api._query_api(SPOKEN_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)

    def test_query_short_api(self):
        result = self.api._query_api(SHORT_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)

    def test_query_recognize_api(self):
        result = self.api._query_api(RECOGNIZE_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)

    def test_handle_query_invalid_type(self):
        resp = self.api.handle_query(api="basic")
        self.assertEqual(resp["status_code"], -1)

    def test_handle_query_invalid_query(self):
        resp = self.api.handle_query(api="simple")
        self.assertEqual(resp["status_code"], -1)

    def test_handle_query_invalid_response(self):
        resp = self.api.handle_query(api="short",
                                     query="i like",
                                     units="metric",
                                     ip="50.47.129.133")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 501)

    def test_handle_query_invalid_key(self):
        from copy import deepcopy
        valid_key = deepcopy(self.api._api_key)
        self.api._api_key = ""

        resp = self.api.handle_query(query="how far away is mars")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 403)
        self.assertIsInstance(resp["content"], bytes)
        self.assertIsInstance(resp["encoding"], str)
        self.assertIsInstance(resp["content"].decode(resp["encoding"]), str)

        self.api._api_key = valid_key

    def test_handle_query_valid(self):
        resp = self.api.handle_query(api="short",
                                     query="how far away is the moon?",
                                     units="metric",
                                     ip="50.47.129.133")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 200)
        self.assertIsInstance(resp["content"], bytes)
        self.assertIsInstance(resp["encoding"], str)
        self.assertIsInstance(resp["content"].decode(resp["encoding"]), str)
        cached = self.api.handle_query(api="short",
                                       query="how far away is the moon?",
                                       units="metric",
                                       ip="50.47.129.133")
        self.assertEqual(resp, cached)


if __name__ == '__main__':
    unittest.main()
