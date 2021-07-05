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

import urllib.parse

from enum import Enum
from neon_api_proxy.cached_api import CachedAPI
from neon_utils.log_utils import LOG


class QueryUrl(Enum):
    def __str__(self):
        return self.value
    SYMBOL = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH"  # keywords=, apikey=
    QUOTE = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE"  # symbol=, apikey=


class AlphaVantageAPI(CachedAPI):
    """
    API for querying Alpha Vantage.
    """

    def __init__(self):
        super().__init__("alphavantage")
        self._api_key = "V27C6HB4CW5CBU7H"
        self.preferred_market = "United States"

    def _search_symbol(self, query: str) -> dict:
        if not query:
            raise ValueError(f"Query is None")
        elif not isinstance(query, str):
            raise TypeError(f"Query is not a str: {query} ({type(query)})")
        query_params = {"keywords": query,
                        "apikey": self._api_key}
        query_str = urllib.parse.urlencode(query_params)
        resp = self.session.get(f"{QueryUrl.SYMBOL}&{query_str}")
        if not resp.ok:
            LOG.error(f"API Query error ({resp.status_code}): {query}")
            return {}
        else:
            resp_json = resp.json().get("bestMatches")
            if not resp_json:
                return dict()
            # Filter by perferred market
            matches = [co for co in resp_json if co.get("4. region") == self.preferred_market]
            if not matches:
                matches = resp_json
            match = matches[0]
            stock = {"symbol": match['1. symbol'],
                     "name": match['2. name'],
                     "region": match['4. region'],
                     'currency': match['8. currency']
                     }
            return stock

    def _get_quote(self, symbol: str):
        if not symbol:
            raise ValueError(f"symbol is None")
        elif not isinstance(symbol, str):
            raise TypeError(f"symbol is not a str: {symbol} ({type(symbol)})")
        query_params = {"symbol": symbol,
                        "apikey": self._api_key}
        query_str = urllib.parse.urlencode(query_params)
        with self.session.request_expire_after(180):
            resp = self.session.get(f"{QueryUrl.QUOTE}&{query_str}")
        if not resp.ok:
            LOG.error(f"API Query error ({resp.status_code}): {symbol}")
            return {"status_code": resp.status_code,
                    "symbol": symbol}
        else:
            quote = resp.json().get("Global Quote")
            if not quote:
                return {}
            quote = {"price": str(round(float(quote['05. price']), 2)),
                     "symbol": quote['01. symbol']
                     }
            LOG.debug(quote)
            return quote

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'symbol' - optional string stock symbol to query
          'company' - optional string company name to query
          'api' - optional string 'symbol' or 'quote'
        :return: dict containing stock data from URL response
        """
        api = kwargs.get("api")
        if not api:
            query_type = QueryUrl.QUOTE
        elif api == "symbol":
            query_type = QueryUrl.SYMBOL
        elif api == "quote":
            query_type = QueryUrl.QUOTE
        else:
            return {"status_code": -1,
                    "content": f"Unknown api requested: {api}",
                    "encoding": None}

        try:
            symbol = kwargs.get('symbol')
            company = kwargs.get('company')
            search_term = symbol or company
            if not search_term:
                return {"status_code": -1,
                        "content": f"No search term provided",
                        "encoding": None}

            if query_type == QueryUrl.SYMBOL:
                return self._search_symbol(search_term)
            else:
                data = self._search_symbol(search_term)
                symbol = data.get("symbol")
                quote = self._get_quote(symbol)
                return {**quote, **data}
        except Exception as e:
            return {"status_code": -1,
                    "content": repr(e),
                    "encoding": None}

    def _query_api(self, query: str) -> dict:
        """
        Queries the Wolfram|Alpha API and returns a dict with the status, content, and encoding
        :param query: URL to query
        :return: dict response containing: `status_code`, `content`, and `encoding`
        """
        result = self.session.get(query)
        if not result.ok:
            # 501 = Wolfram couldn't understand
            # 403 = Invalid API Key Provided
            LOG.warning(f"API Query error ({result.status_code}): {query}")
        return {"status_code": result.status_code,
                "content": result.content,
                "encoding": result.encoding}
