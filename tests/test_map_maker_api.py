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
from neon_api_proxy.services.map_maker_api import MapMakerAPI

VALID_LAT = "47.4797"
VALID_LON = "-122.2079"

INVALID_LAT = "a"
INVALID_LON = "b"

VALID_ADDRESS = "Kirkland"
VALID_ADDRESS_2 = "New York New York"

INVALID_ADDRESS = ""


class TestMapMakerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = MapMakerAPI()

    def test_geocode_lookup(self):
        valid_response = self.api.handle_query(address=VALID_ADDRESS)
        self.assertEqual(valid_response['status_code'], 200)
        self.assertEqual(valid_response["encoding"].lower(), "utf-8")
        valid_location = json.loads(valid_response["content"])[0]
        self.assertAlmostEqual(float(valid_location['lat']), 47.69, delta=0.02)
        self.assertAlmostEqual(float(valid_location['lon']), -122.19,
                               delta=0.02)

        valid_response_2 = self.api.handle_query(address=VALID_ADDRESS_2)
        self.assertEqual(valid_response_2['status_code'], 200)
        self.assertEqual(valid_response_2["encoding"].lower(), "utf-8")
        valid_location = json.loads(valid_response_2["content"])[0]
        self.assertAlmostEqual(float(valid_location['lat']), 36.10, delta=0.02)
        self.assertAlmostEqual(float(valid_location['lon']), -115.17,
                               delta=0.02)

        # Test language
        valid_es_location = self.api.handle_query(address=VALID_ADDRESS,
                                                  lang_code="es-us")
        self.assertEqual(valid_es_location['status_code'], 200)
        self.assertEqual(valid_es_location["encoding"].lower(), "utf-8")
        es_location = json.loads(valid_es_location["content"])[0]
        self.assertNotEqual(valid_location, es_location)
        self.assertEqual(valid_location['lat'], es_location['lat'])
        self.assertEqual(valid_location['lon'], es_location['lon'])

        invalid_response = self.api.handle_query(address=INVALID_ADDRESS)
        self.assertEqual(invalid_response['status_code'], -1)

    def test_reverse_lookup(self):
        valid_response = self.api.handle_query(lat=VALID_LAT, lon=VALID_LON)
        self.assertEqual(valid_response['status_code'], 200)
        self.assertEqual(valid_response["encoding"].lower(), "utf-8")
        valid_location = json.loads(valid_response["content"])['address']
        self.assertEqual(valid_location['state'], "Washington", valid_location)
        self.assertEqual(valid_location['town'], "Renton", valid_location)

        # Test language
        valid_es_location = self.api.handle_query(lat=VALID_LAT, lon=VALID_LON,
                                                  lang_code="es")
        self.assertEqual(valid_es_location['status_code'], 200)
        self.assertEqual(valid_es_location["encoding"].lower(), "utf-8")
        es_location = json.loads(valid_es_location["content"])['address']
        self.assertNotEqual(valid_location, es_location)

        invalid_response = self.api.handle_query(lat=VALID_LAT, lon=None)
        self.assertEqual(invalid_response['status_code'], -1)

        invalid_coords = self.api.handle_query(lat=INVALID_LAT, lon=INVALID_LON)
        self.assertNotEqual(invalid_coords['status_code'], 200)


if __name__ == '__main__':
    unittest.main()
