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
import pytest

from mock.mock import Mock
from ovos_utils.log import LOG

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


IP_ADDR = "50.47.129.133"
VALID_LAT = "47.4797"
VALID_LNG = "-122.2079"
# TODO: Use mock returns for these tests
# TODO: Update to test local vs remote calls


class RequestAPITests(unittest.TestCase):
    def test_request_neon_api_valid(self):
        from neon_api_proxy.client import request_api, NeonAPI
        resp = request_api(NeonAPI.TEST_API, {"test": True})
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['status_code'], 200)

    def test_request_neon_api_not_implemented(self):
        from neon_api_proxy.client import request_api, NeonAPI
        resp = request_api(NeonAPI.NOT_IMPLEMENTED, {"request": "data"})
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['status_code'], 401)

    def test_request_neon_api_invalid_api(self):
        from neon_api_proxy.client import request_api
        with self.assertRaises(TypeError):
            request_api("alpha_vantage", {"company": "alphabet"})

    def test_request_neon_api_invalid_null_params(self):
        from neon_api_proxy.client import request_api, NeonAPI
        with self.assertRaises(ValueError):
            request_api(NeonAPI.ALPHA_VANTAGE, {})

    def test_request_neon_api_invalid_type_params(self):
        from neon_api_proxy.client import request_api, NeonAPI
        with self.assertRaises(TypeError):
            request_api(NeonAPI.ALPHA_VANTAGE, ["alphabet"])


class NeonAPIClientTests(unittest.TestCase):
    map_maker_key = None

    @classmethod
    def setUpClass(cls) -> None:
        def _override_find_key(*args, **kwargs):
            raise Exception("Test Exception; no key found")
        import neon_utils.authentication_utils
        neon_utils.authentication_utils.find_generic_keyfile = _override_find_key

        if os.getenv("MAP_MAKER_KEY"):
            cls.map_maker_key = os.environ.pop("MAP_MAKER_KEY")

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.map_maker_key:
            os.environ["MAP_MAKER_KEY"] = cls.map_maker_key

    def test_client_init_no_keys(self):
        from neon_api_proxy.client import NeonAPIProxyClient
        client = NeonAPIProxyClient({"test": "test"})
        self.assertEqual(set(client.service_instance_mapping.keys()),
                         {"api_test_endpoint"})

    def test_client_lazy_load(self):
        from neon_api_proxy.client import NeonAPI, request_api
        resp = request_api(NeonAPI.TEST_API, {"test": "test"})
        self.assertIsInstance(resp, dict)
        from neon_api_proxy.client import _CLIENT, NeonAPIProxyClient
        self.assertIsInstance(_CLIENT, NeonAPIProxyClient)

    def test_call_local_api(self):
        from neon_api_proxy.client import NeonAPI, request_api, init_client
        init_client()
        from neon_api_proxy.client import _CLIENT
        mock = Mock(wraps=_CLIENT.service_instance_mapping["api_test_endpoint"].handle_query)
        _CLIENT.service_instance_mapping["api_test_endpoint"].handle_query = mock
        args = [NeonAPI.TEST_API, {"test": "test"}]
        resp = request_api(*args)
        self.assertIsInstance(resp, dict)
        mock.assert_called_once()
        mock.assert_called_with(test="test", service=str(NeonAPI.TEST_API))


class WolframAlphaTests(unittest.TestCase):
    def test_get_geolocation_ip(self):
        from neon_api_proxy.client.wolfram_alpha import get_geolocation_params
        location = get_geolocation_params(ip=IP_ADDR)
        self.assertIsInstance(location, dict)
        self.assertEqual(location, {"ip": IP_ADDR})

    def test_get_geolocation_lat_lng(self):
        from neon_api_proxy.client.wolfram_alpha import get_geolocation_params
        location = get_geolocation_params(lat=VALID_LAT, lng=VALID_LNG)
        self.assertIsInstance(location, dict)
        self.assertEqual(location, {"latlong": f"{VALID_LAT},{VALID_LNG}"})

    def test_get_geolocation_null(self):
        from neon_api_proxy.client.wolfram_alpha import get_geolocation_params
        from neon_utils.net_utils import get_ip_address
        location = get_geolocation_params()
        self.assertIsInstance(location, dict)
        self.assertEqual(location, {"ip": get_ip_address()})

    def test_api_to_url_valid(self):
        from neon_api_proxy.client.wolfram_alpha import api_to_url, QueryApi
        self.assertEqual(api_to_url(QueryApi.SIMPLE), "http://api.wolframalpha.com/v2/simple")
        self.assertEqual(api_to_url(QueryApi.SHORT), "http://api.wolframalpha.com/v2/result")
        self.assertEqual(api_to_url(QueryApi.SPOKEN), "http://api.wolframalpha.com/v2/spoken")
        self.assertEqual(api_to_url(QueryApi.FULL), "http://api.wolframalpha.com/v2/query")
        self.assertEqual(api_to_url(QueryApi.RECOGNIZE), "http://www.wolframalpha.com/queryrecognizer/query.jsp")
        self.assertEqual(api_to_url(QueryApi.CONVERSATION), "http://api.wolframalpha.com/v1/conversation.jsp")

    def test_api_to_url_invalid_null_api(self):
        from neon_api_proxy.client.wolfram_alpha import api_to_url
        with self.assertRaises(ValueError):
            api_to_url(None)

    def test_api_to_url_invalid_type_api(self):
        from neon_api_proxy.client.wolfram_alpha import api_to_url
        with self.assertRaises(TypeError):
            api_to_url("simple")

    def test_get_wolfram_alpha_response_spec_api_key(self):
        from neon_api_proxy.client.wolfram_alpha import get_wolfram_alpha_response, QueryApi
        resp = get_wolfram_alpha_response("Convert 42 mi to km", QueryApi.SPOKEN, app_id="DEMO")
        self.assertIsInstance(resp, str)
        self.assertEqual(resp, '42 miles is equivalent to about 67.6 kilometers')

    def test_get_wolfram_alpha_bytes_response(self):
        from neon_api_proxy.client.wolfram_alpha import get_wolfram_alpha_response, QueryApi
        resp = get_wolfram_alpha_response("Who is the prime minister of India", QueryApi.SIMPLE)
        if resp != "Wolfram|Alpha did not understand your input":
            self.assertIsInstance(resp, bytes)

    def test_get_wolfram_alpha_response_no_api_key(self):
        from neon_api_proxy.client.wolfram_alpha import get_wolfram_alpha_response, QueryApi
        resp = get_wolfram_alpha_response("Who is the prime minister of India", QueryApi.SIMPLE, app_id=None)
        if resp == "Wolfram|Alpha did not understand your input":
            LOG.warning("Wolfram Alpha returned an invalid response (known occasional bug)")
        else:
            self.assertIsInstance(resp, bytes)


# class AlphaVantageTests(unittest.TestCase):
#     def test_get_stock_symbol_spec_key(self):
#         from neon_api_proxy.client.alpha_vantage import search_stock_by_name
#         matches = search_stock_by_name("tencent", api_key="demo")
#         self.assertIsInstance(matches, list)
#         for match in matches:
#             self.assertIsInstance(match, dict)
#             self.assertEqual(match["region"], "United States")
#         self.assertEqual(matches[0]["symbol"], "TCEHY")
#
#     def test_get_stock_symbol_conf_key(self):
#         from neon_api_proxy.client.alpha_vantage import search_stock_by_name
#         matches = search_stock_by_name("alphabet")
#         self.assertIsInstance(matches, list)
#         for match in matches:
#             self.assertIsInstance(match, dict)
#             self.assertEqual(match["region"], "United States")
#         self.assertEqual(matches[0]["symbol"], "GOOGL")
#
#     @pytest.mark.skip  # TODO: This fails due to cached valid response
#     def test_get_stock_symbol_invalid_key(self):
#         from neon_api_proxy.client.alpha_vantage import search_stock_by_name
#         matches = search_stock_by_name("alphabet", api_key="demo")
#         self.assertIsInstance(matches, list)
#         self.assertEqual(len(matches), 0)
#
#     def test_get_stock_symbol_no_results(self):
#         from neon_api_proxy.client.alpha_vantage import search_stock_by_name
#         matches = search_stock_by_name("google")
#         self.assertIsInstance(matches, list)
#         self.assertEqual(len(matches), 0)
#
#     def test_get_stock_quote_spec_key(self):
#         from neon_api_proxy.client.alpha_vantage import get_stock_quote
#         quote = get_stock_quote("IBM", api_key="demo")
#         self.assertIsInstance(quote, dict)
#         self.assertEqual(set(quote.keys()), {"symbol", "price", "close"})
#         self.assertEqual(quote["symbol"], "IBM")
#
#     def test_get_stock_quote_conf_key(self):
#         from neon_api_proxy.client.alpha_vantage import get_stock_quote
#         quote = get_stock_quote("GOOGL")
#         self.assertIsInstance(quote, dict)
#         self.assertEqual(set(quote.keys()), {"symbol", "price", "close"}, quote)
#         self.assertEqual(quote["symbol"], "GOOGL")
#
#     def test_get_stock_quote_invalid_key(self):
#         from neon_api_proxy.client.alpha_vantage import get_stock_quote
#         quote = get_stock_quote("MSFT", api_key="INVALID")
#         self.assertIsInstance(quote, dict)
#         if "symbol" in quote.keys():
#             LOG.warning("Invalid API key produced valid result!")
#             self.assertEqual(quote.get("symbol"), "MSFT")
#         else:
#             self.assertTrue(quote.get("error"), quote)
#
#     def test_get_stock_quote_invalid_symbol(self):
#         from neon_api_proxy.client.alpha_vantage import get_stock_quote
#         quote = get_stock_quote("International Business Machines")
#         self.assertIsInstance(quote, dict)
#         self.assertTrue(quote.get("error"))
#
#     def test_get_stock_quote_no_api_key(self):
#         from neon_api_proxy.client.alpha_vantage import get_stock_quote
#         quote = get_stock_quote("IBM", api_key=None)
#         self.assertIsInstance(quote, dict)
#         self.assertEqual(set(quote.keys()), {"symbol", "price", "close"})
#         self.assertEqual(quote["symbol"], "IBM")
#
#     def test_get_stock_symbol_no_api_key(self):
#         from neon_api_proxy.client.alpha_vantage import search_stock_by_name
#         matches = search_stock_by_name("tencent", api_key=None)
#         self.assertIsInstance(matches, list)
#         for match in matches:
#             self.assertIsInstance(match, dict)
#             self.assertEqual(match["region"], "United States")
#         self.assertEqual(matches[0]["symbol"], "TCEHY")


class OpenWeatherMapTests(unittest.TestCase):
    def test_get_forecast_valid_str(self):
        from neon_api_proxy.client.open_weather_map import get_forecast
        data = get_forecast(VALID_LAT, VALID_LNG)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["current"], dict)
        self.assertIsInstance(data["minutely"], list)
        self.assertIsInstance(data["hourly"], list)
        self.assertIsInstance(data["daily"], list)

    def test_get_forecast_valid_float(self):
        from neon_api_proxy.client.open_weather_map import get_forecast
        data = get_forecast(float(VALID_LAT), float(VALID_LNG))
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["current"], dict)
        self.assertIsInstance(data["minutely"], list)
        self.assertIsInstance(data["hourly"], list)
        self.assertIsInstance(data["daily"], list)

    def test_get_current_weather(self):
        from neon_api_proxy.client.open_weather_map import get_current_weather
        data = get_current_weather(VALID_LAT, VALID_LNG)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["weather"], list)
        self.assertIsInstance(data["weather"][0], dict)

        self.assertIsInstance(data["main"], dict)

    def test_get_forecast_invalid_location(self):
        from neon_api_proxy.client.open_weather_map import get_forecast
        data = get_forecast("lat", "lon")
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['error'], str)

    @pytest.mark.skip  # TODO: This inconsistently returns valid results
    def test_get_forecast_invalid_key(self):
        from neon_api_proxy.client.open_weather_map import get_forecast
        data = get_forecast(VALID_LAT, VALID_LNG, api_key="test")
        self.assertIsInstance(data, dict)
        self.assertEqual(data['cod'], '401')

    def test_get_forecast_no_api_key(self):
        from neon_api_proxy.client.open_weather_map import get_forecast
        data = get_forecast(VALID_LAT, VALID_LNG, api_key=None)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["current"], dict)
        self.assertIsInstance(data["minutely"], list)
        self.assertIsInstance(data["hourly"], list)
        self.assertIsInstance(data["daily"], list)


class MapMakerTests(unittest.TestCase):
    def test_get_coordinates(self):
        from neon_api_proxy.client.map_maker import get_coordinates

        # Valid request
        lat, lon = get_coordinates("Kirkland")
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

        # Invalid request
        with self.assertRaises(RuntimeError):
            get_coordinates("")

    def test_get_address(self):
        from neon_api_proxy.client.map_maker import get_address

        # Valid Request
        address = get_address(VALID_LAT, VALID_LNG)
        self.assertEqual(address['state'], "Washington")
        self.assertEqual(address['city'], "Renton", address)

        # Invalid Request
        with self.assertRaises(RuntimeError):
            get_address('', '')
