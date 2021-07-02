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

import itertools
import urllib.parse
from enum import Enum
from typing import Union

from neon_api_proxy.cached_api import CachedAPI
from neon_api_proxy.exceptions import *


class QueryUrl(Enum):
    SIMPLE = "http://api.wolframalpha.com/v2/simple"
    SHORT = "http://api.wolframalpha.com/v2/result"
    SPOKEN = "http://api.wolframalpha.com/v2/spoken"
    FULL = "http://api.wolframalpha.com/v2/query"
    RECONGNIZE = "http://www.wolframalpha.com/queryrecognizer/query.jsp"
    CONVERSATION = "http://api.wolframalpha.com/v1/conversation.jsp"


class WolframAPI(CachedAPI):
    """
    API for querying Wolfram|Alpha.
    """

    def __init__(self):
        super().__init__("wolfram")
        self._api_key = ""  # TODO: Method to get this DM

    def _build_query_url(self, query_type: QueryUrl, query_url: str):
        if not query_type:
            raise ValueError(f"query_type not defined!")
        if not query_url:
            raise ValueError(f"query_url not defined!")
        if not isinstance(query_type, QueryUrl):
            raise TypeError(f"Not a QueryUrl: {query_url}")
        if not isinstance(query_url, str):
            raise TypeError(f"Not a string: {query_url}")
        if query_type == QueryUrl.RECONGNIZE:
            query_url = f"{query_url}&mode=Default"
        return f"{query_type}?appid={self._api_key}&{query_url}"

    @staticmethod
    def _build_query_string(**kwargs):
        if not kwargs.get("query"):
            raise ValueError(f"No query in request: {kwargs}")
        query_params = dict()
        query_params['i'] = kwargs.get("query")
        query_params['units'] = kwargs.get("units") if kwargs.get("units") == "metric" else "nonmetric"
        lat = kwargs.get("lat")
        lng = kwargs.get("lng")
        if lat and lng:
            query_params["latlong"] = f"{lat},{lng}"
        else:
            query_params["ip"] = kwargs.get("ip")

        query_params = {k: v for k, v in query_params.items() if v}
        query_data = itertools.chain(query_params.items())
        query_str = urllib.parse.urlencode(tuple(query_data))
        return query_str

    def handle_query(self, **kwargs) -> Union[str, bytes]:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'query' - string query to ask Wolfram|Alpha
          'api' - string api to query (simple, short, spoken, full, recognize, conversation)
          'units' - optional string "metric" or "nonmetric"
          'lat'+'lng' optional float or string lat/lng (separate keys)
          'ip' optional string origin IP Address for geolocation
        :return: string response, bytes for QueryUrl.SIMPLE
        """
        api = kwargs.get("api")
        if not api:
            query_type = QueryUrl.SHORT
        elif api == "simple":
            query_type = QueryUrl.SIMPLE
        elif api == "short":
            query_type = QueryUrl.SHORT
        elif api == "spoken":
            query_type = QueryUrl.SPOKEN
        elif api == "full":
            query_type = QueryUrl.FULL
        elif api == "recognize":
            query_type = QueryUrl.RECONGNIZE
        elif api == "conversation":
            query_type = QueryUrl.CONVERSATION
        else:
            raise ValueError(f"Unknown api requested: {api}")

        query_str = self._build_query_string(**kwargs)
        return self.query_api(self._build_query_url(query_type, query_str))

    def query_api(self, query: str):
        result = self.session.get(query)
        if result.status_code == 200:
            try:
                return result.content.decode("utf-8")
            except UnicodeDecodeError:
                return result.content
        else:
            raise APIError("Non-success Status Code Returned!", result.status_code)
