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

from neon_utils.configuration_utils import NGIConfig

from neon_api_proxy.owm_api import OpenWeatherAPI
from neon_api_proxy.alpha_vantage_api import AlphaVantageAPI
from neon_api_proxy.wolfram_api import WolframAPI
from neon_api_proxy.test_api import TestAPI


class NeonAPIProxyController:
    """
        Generic module for binding between service name and actual service for fulfilling request
    """

    # Mapping between string service name and actual class
    service_class_mapping = {
        'wolfram_alpha': WolframAPI,
        'alpha_vantage': AlphaVantageAPI,
        'open_weather_map': OpenWeatherAPI,
        'api_test_endpoint': TestAPI
    }

    def __init__(self, config: dict = None):
        """
            @param config: configurations dictionary
        """
        self.config = config or NGIConfig("ngi_auth_vars")["api_services"]
        self.service_instance_mapping = self.init_service_instances(self.service_class_mapping)

    def init_service_instances(self, service_class_mapping: dict) -> dict:
        """
            Maps service classes to their instances
            @param service_class_mapping: dictionary containing mapping between service string name
                    and python class representing it

            @return dictionary containing mapping between service string name
                    and instance of python class representing it
        """
        service_mapping = dict()
        for item in list(service_class_mapping):
            api_key = self.config.get("SERVICES", self.config).get(item, {}).get("api_key") if self.config else None
            service_mapping[item] = service_class_mapping[item](api_key=api_key)
        return service_mapping

    def resolve_query(self, query: dict) -> dict:
        """
            Generically resolves input query dictionary by mapping its "service" parameter
            @param query: dictionary with query parameters
            @return: response from the destination service
        """
        target_service = query.get('service', None)
        message_id = query.pop('message_id', None)
        if target_service and target_service in list(self.service_instance_mapping):
            resp = self.service_instance_mapping[target_service].handle_query(**query)
        else:
            resp = {
                "status_code": 401,
                "content": f"Unresolved service name: {target_service}",
                "encoding": "utf-8"
            }
        resp['message_id'] = message_id
        return resp
