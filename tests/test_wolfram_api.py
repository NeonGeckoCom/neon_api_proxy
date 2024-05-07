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

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_api_proxy.wolfram_api import WolframAPI, QueryUrl


VALID_QUERY_IP = {"query": "how far away is Moscow?",
                  "units": "metric",
                  "ip": "50.47.129.133"}

VALID_QUERY_LAT_LON = {"query": "how far away is new york?",
                       "units": "imperial",
                       "lat": "47.4797",
                       "lng": "122.2079"}

VALID_QUERY_LAT_LON_IP = {"query": "how far away is Bellevue?",
                          "units": "nonmetric",  # Test backwards-compat.
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
        self.assertEqual(query_str, f"i=how+far+away+is+Miami%3F&units=imperial")

    def test_build_query_string_valid_lat_lng(self):
        query_str = self.api._build_query_string(**VALID_QUERY_LAT_LON)
        self.assertEqual(query_str, f"i=how+far+away+is+new+york%3F&units=imperial&latlong=47.4797%2C122.2079")

    def test_build_query_string_valid_ip(self):
        query_str = self.api._build_query_string(**VALID_QUERY_IP)
        self.assertEqual(query_str, f"i=how+far+away+is+Moscow%3F&units=metric&ip=50.47.129.133")

    def test_build_query_string_valid_lat_lng_ip(self):
        query_str = self.api._build_query_string(**VALID_QUERY_LAT_LON_IP)
        self.assertEqual(query_str, f"i=how+far+away+is+Bellevue%3F&units=imperial&latlong=47.4797%2C122.2079")

    def test_build_query_invalid_query(self):
        with self.assertRaises(ValueError):
            self.api._build_query_string(**INVALID_QUERY)

    def test_query_full_api(self):
        result = self.api._query_api(FULL_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)

    @unittest.skip("Wolfram API occasionally response with an error")
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

    def test_handle_query_valid_ip(self):
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

    def test_handle_query_valid_lat_lng(self):
        resp = self.api.handle_query(api="short",
                                     query="how far away is the moon?",
                                     units="metric",
                                     lat="47.4797",
                                     lng="-122.2079")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 200)
        self.assertIsInstance(resp["content"], bytes)
        self.assertIsInstance(resp["encoding"], str)
        self.assertIsInstance(resp["content"].decode(resp["encoding"]), str)

    def test_handle_query_valid_latlong(self):
        resp = self.api.handle_query(api="short",
                                     query="how far away is the moon?",
                                     units="metric",
                                     latlong="47.4797,-122.2079")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["status_code"], 200)
        self.assertIsInstance(resp["content"], bytes)
        self.assertIsInstance(resp["encoding"], str)
        self.assertIsInstance(resp["content"].decode(resp["encoding"]), str)

        same = self.api.handle_query(api="short",
                                     query="how far away is the moon?",
                                     units="metric",
                                     lat="47.4797",
                                     lng="-122.2079")
        self.assertEqual(resp, same)

    def test_get_wolfram_alpha_bytes_response(self):
        resp = self.api.handle_query(api="simple",
                                     query="Who is the prime minister of India")
        if resp["content"] != "Wolfram|Alpha did not understand your input":
            self.assertIsInstance(resp["content"], bytes)


if __name__ == '__main__':
    unittest.main()
