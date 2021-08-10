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

import socketserver

from neon_utils import LOG
from neon_utils.socket_utils import *


class NeonAPITCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_message = get_packet_data(self.request)
        received_message_decoded = b64_to_dict(received_message)
        LOG.debug(f"Received request from '{self.client_address[0]}' : {received_message_decoded}")
        response = self.server.controller.resolve_query(received_message_decoded)
        LOG.debug(f'Received response from controller status_code={response["status_code"]}')
        encoded_response = dict_to_b64(response)
        LOG.debug(f'Encoded response from controller len={len(encoded_response)}')
        self.request.sendall(encoded_response)
