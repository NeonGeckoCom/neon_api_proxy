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

import os
import sys
import unittest
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_api_proxy.cached_api import CachedAPI


class TestCachedAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = CachedAPI("test")

    def test_cached_request(self):
        url = "https://neon.ai"
        res = self.api.session.get(url, timeout=10)
        cached = self.api.session.get(url, timeout=10)
        self.assertTrue(cached.from_cache)
        self.assertEqual(res.content, cached.content)

    def test_request_no_cache(self):
        url = "https://neon.ai"
        res = self.api.session.get(url, timeout=10)
        with self.api.session.cache_disabled():
            cached = self.api.session.get(url, timeout=10)
            self.assertFalse(cached.from_cache)
        self.assertEqual(res.content, cached.content)

    def test_get_with_cache_timeout(self):
        url = "https://chatbotsforum.org"
        res = self.api.get_with_cache_timeout(url, 5)
        self.assertFalse(res.from_cache)
        cached = self.api.get_with_cache_timeout(url, 15)
        self.assertTrue(cached.from_cache)
        self.assertEqual(res.content, cached.content)
        sleep(5)
        expired = self.api.get_with_cache_timeout(url)
        self.assertFalse(expired.from_cache)

    def test_get_bypass_cache(self):
        url = "https://klat.com"
        res = self.api.get_with_cache_timeout(url)
        self.assertFalse(res.from_cache)
        cached = self.api.get_with_cache_timeout(url)
        self.assertTrue(cached.from_cache)
        no_cache = self.api.get_bypass_cache(url)
        self.assertFalse(no_cache.from_cache)


if __name__ == '__main__':
    unittest.main()
