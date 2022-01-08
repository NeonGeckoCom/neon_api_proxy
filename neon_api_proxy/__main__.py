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

import argparse
import socketserver

from ovos_utils import wait_for_exit_signal

from neon_api_proxy.api_connector import NeonAPIMQConnector
from neon_api_proxy.config import get_proxy_config
from neon_api_proxy.controller import NeonAPIProxyController
from neon_api_proxy.socket_handler import NeonAPITCPHandler


def run_tcp_handler(config_data: dict = None):
    """
        Runs threaded TCP socket on specified address and port
        @param config_data: dict with configuration data for the ProxyController
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


def run_mq_handler():
    """
    Start the ProxyController and MQConnector services
    """
    config_data = get_proxy_config()
    proxy = NeonAPIProxyController(config_data)
    connector = NeonAPIMQConnector(config=None, service_name='neon_api_connector', proxy=proxy)
    connector.run()
    wait_for_exit_signal()


def main():
    run_mq_handler()


if __name__ == "__main__":
    main()
