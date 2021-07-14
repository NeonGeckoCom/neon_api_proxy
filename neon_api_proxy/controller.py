import os
import json

from neon_api_proxy.owm_api import OpenWeatherAPI
from neon_api_proxy.alpha_vantage_api import AlphaVantageAPI
from neon_api_proxy.wolfram_api import WolframAPI


class NeonAPIProxyController:
    """
        Generic module for binding between service name and actual service for fulfilling request
    """

    # Mapping between string service name and actual class
    service_class_mapping = {
        'wolfram_alpha': WolframAPI,
        'alpha_vantage': AlphaVantageAPI,
        'open_weather_map': OpenWeatherAPI
    }

    def __init__(self, config: dict = None):
        """
            @param config: configurations dictionary
        """
        self.config = config

    def resolve_query(self, query: dict) -> dict:
        """
            Generically resolves input query dictionary by mapping its "service" parameter
            @param query: dictionary with query parameters
            @return: response from the destination service
        """
        target_service = query.get('service', None)
        if target_service and target_service in list(self.service_class_mapping):
            api_key = None
            if os.environ.get('ENV', None) == 'DEV':
                api_key = self.config['SERVICES'][target_service]['api_key'] if self.config else None
            resp = self.service_class_mapping[target_service](api_key=api_key).handle_query(**query)
        else:
            resp = {
                "status_code": 401,
                "content": f"Unresolved service name: {target_service}",
                "encoding": "utf-8"
            }
        return resp