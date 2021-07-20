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
import json
import argparse
import socketserver

from neon_utils import LOG
from neon_api_proxy.controller import NeonAPIProxyController
from neon_api_proxy.socket_handler import NeonAPITCPHandler


def main(config_data: dict = None):
    """
        Runs threaded TCP socket on specified address and port
        @param config_data: dict with configuration data
    """
    parser = argparse.ArgumentParser(description='Parameters for TCP socket server')

    parser.add_argument('--host',
                        type=str,
                        default='127.0.0.1',
                        help='Socket host (defaults to 127.0.0.1)')
    parser.add_argument('--port',
                        type=int,
                        default=8555,
                        help='Socket port (defaults to 8555)')
    args = parser.parse_args()

    host, port = args.host, args.port

    with socketserver.ThreadingTCPServer((host, port), NeonAPITCPHandler) as server:
        server.controller = NeonAPIProxyController(config=config_data)
        server.serve_forever()


if __name__ == "__main__":
    config_path = os.environ.get('NEON_API_PROXY_CONFIG_PATH', 'config.json')
    _config_data = None
    try:
        with open(os.path.expanduser(config_path)) as input_file:
            _config_data = json.load(input_file)
    except Exception as e:
        LOG.error(e)
    finally:
        main(config_data=_config_data)
