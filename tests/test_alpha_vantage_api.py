# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
# BSD-3
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_api_proxy.alpha_vantage_api import AlphaVantageAPI


VALID_COMPANY_NAME = "Alphabet"
VALID_COMPANY_SYMBOL = "GOOGL"

INVALID_COMPANY_NAME = "Neon Gecko"
INVALID_COMPANY_SYMBOL = "NEONGECKO"


class TestAlphaVantageAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = AlphaVantageAPI()

    def test_get_symbol_valid(self):
        symbol_data = self.api._search_symbol(VALID_COMPANY_NAME)
        symbol_data = json.loads(symbol_data["content"])["bestMatches"]
        self.assertIsInstance(symbol_data, list)
        for s in symbol_data:
            self.assertIsInstance(s, dict)
        valid_one = [stock for stock in symbol_data if stock["1. symbol"] == "GOOGL"]
        self.assertEqual(valid_one[0]["1. symbol"], "GOOGL")

    def test_get_symbol_invalid_symbol(self):
        symbol_data = self.api._search_symbol(INVALID_COMPANY_NAME)
        self.assertIsInstance(symbol_data, dict)
        content = json.loads(symbol_data['content'])
        self.assertFalse(content["bestMatches"])

    def test_get_symbol_null_query(self):
        with self.assertRaises(ValueError):
            self.api._search_symbol("")

    def test_get_symbol_invalid_type(self):
        with self.assertRaises(TypeError):
            self.api._search_symbol(42)

    def test_get_quote_valid(self):
        quote = self.api._get_quote(VALID_COMPANY_SYMBOL)
        quote = json.loads(quote["content"])["Global Quote"]
        self.assertIsInstance(quote, dict)
        self.assertIsInstance(quote["05. price"], str)
        self.assertEqual(quote["01. symbol"], VALID_COMPANY_SYMBOL)

    def test_get_quote_company(self):
        quote = self.api._get_quote(VALID_COMPANY_NAME)
        self.assertIsInstance(quote, dict)
        self.assertEqual(quote["status_code"], 200)
        self.assertFalse(json.loads(quote["content"])["Global Quote"])

    def test_get_quote_invalid_symbol_type(self):
        with self.assertRaises(TypeError):
            self.api._get_quote(42)

    def test_get_quote_null_query(self):
        with self.assertRaises(ValueError):
            self.api._get_quote("")

    def test_handle_query_symbol_valid_company(self):
        data = self.api.handle_query(api="symbol",
                                     company=VALID_COMPANY_NAME)
        self.assertIsInstance(data, dict)
        data = json.loads(data["content"])['bestMatches'][0]
        self.assertIsInstance(data["1. symbol"], str)
        self.assertIsInstance(data["2. name"], str)
        self.assertIsInstance(data["4. region"], str)
        self.assertIsInstance(data["8. currency"], str)

    def test_handle_query_symbol_valid_symbol(self):
        data = self.api.handle_query(api="symbol",
                                     company=VALID_COMPANY_SYMBOL)
        data = json.loads(data["content"])["bestMatches"][0]
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["1. symbol"], str)
        self.assertIsInstance(data["2. name"], str)
        self.assertIsInstance(data["4. region"], str)
        self.assertIsInstance(data["8. currency"], str)

    def test_handle_query_quote_invalid_symbol(self):
        data = self.api.handle_query(api="quote",
                                     company=VALID_COMPANY_NAME)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["status_code"], -1)

    def test_handle_query_quote_valid_symbol(self):
        data = self.api.handle_query(api="quote",
                                     symbol=VALID_COMPANY_SYMBOL)
        data = json.loads(data["content"])["Global Quote"]
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["01. symbol"], str)
        self.assertIsInstance(data["05. price"], str)

    def test_handle_query_no_symbol_company(self):
        data = self.api.handle_query(api="quote")
        self.assertIsInstance(data, dict)
        self.assertEqual(data["status_code"], -1)

    def test_handle_query_invalid_api(self):
        data = self.api.handle_query(api="other",
                                     company=VALID_COMPANY_NAME)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["status_code"], -1)


if __name__ == '__main__':
    unittest.main()
