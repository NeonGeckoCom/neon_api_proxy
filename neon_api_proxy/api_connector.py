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
# Authors: Guy Daniels, Daniel McKnight, Elon Gasper, Richard Leeds, Kirill Hrymailo
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import pika.channel

from typing import Optional
from neon_utils import LOG
from neon_utils.socket_utils import b64_to_dict, dict_to_b64
from neon_mq_connector.connector import MQConnector, ConsumerThread

from neon_api_proxy.controller import NeonAPIProxyController


class NeonAPIMQConnector(MQConnector):
    """Adapter for establishing connection between Neon API and MQ broker"""

    def __init__(self, config: dict, service_name: str, proxy: NeonAPIProxyController):
        """
            Additionally accepts message bus connection properties

            :param config: dictionary containing MQ configuration data
            :param service_name: name of the service instance
        """
        super().__init__(config, service_name)

        self.vhost = '/neon_api'
        self.proxy = proxy

    def handle_api_input(self,
                         channel: pika.channel.Channel,
                         method: pika.spec.Basic.Deliver,
                         properties: pika.spec.BasicProperties,
                         body: bytes):
        """
            Handles input requests from MQ to Neon API

            :param channel: MQ channel object (pika.channel.Channel)
            :param method: MQ return method (pika.spec.Basic.Deliver)
            :param properties: MQ properties (pika.spec.BasicProperties)
            :param body: request body (bytes)
        """
        message_id = None
        try:
            if body and isinstance(body, bytes):
                request = b64_to_dict(body)
                tokens = self.extract_agent_tokens(request)

                message_id = tokens.pop('message_id', request.get("message_id", None))
                LOG.info(f"request={request}; message_id={message_id}")

                respond = self.proxy.resolve_query(request)
                LOG.info(f"message={message_id} status={respond.get('status_code')}")

                try:
                    respond['content'] = bytes(respond.get('content', b'')).decode(encoding='utf-8')
                except Exception as e:
                    LOG.error(e)
                respond = {**respond, **tokens}
                LOG.debug(f"respond={respond}")
                data = dict_to_b64(respond)

                routing_key = request.get('routing_key', 'neon_api_output')
                # queue declare is idempotent, just making sure queue exists
                channel.queue_declare(queue=routing_key)
                channel.basic_publish(exchange='',
                                      routing_key=routing_key,
                                      body=data,
                                      properties=pika.BasicProperties(expiration='1000')
                                      )
                channel.basic_ack(method.delivery_tag)
            else:
                raise TypeError(f'Invalid body received, expected: bytes string; got: {type(body)}')
        except Exception as e:
            LOG.error(f"message_id={message_id}")
            LOG.error(e)

    @staticmethod
    def extract_agent_tokens(msg_data: dict) -> dict:
        """
            Extracts tokens from msg data based on received "agent"

            :param msg_data: desired message data
            :return: dictionary containing tokens dedicated to resolved agent
        """
        tokens = dict()
        request_agent = msg_data.pop('agent', 'undefined')
        if 'klatchat' in request_agent:
            LOG.info('Resolved agent is "klatchat"')
            tokens['cid'] = msg_data.pop("cid", None)
            tokens['message_id'] = tokens['replied_message'] = msg_data.get('messageID', None)
        else:
            LOG.warning('Failed to resolve an agent from the message data')
        return tokens

    def handle_error(self, thread, exception):
        LOG.error(exception)
        LOG.info(f"Restarting Consumers")
        self.stop()
        self.run()

    def pre_run(self, **kwargs):
        self.register_consumer("neon_api_consumer", self.vhost, 'neon_api_input', self.handle_api_input, auto_ack=False)
        self.register_consumer("neon_api_consumer_targeted",
                               self.vhost,
                               f'neon_api_input_{self.service_id}',
                               self.handle_api_input, auto_ack=False)

    # TODO: Remove below methods after MQ Connector dep bumped to 0.2.0 DM
    def run(self, **kwargs):
        self.pre_run(**kwargs)
        self.run_consumers()

    def stop(self):
        pass
