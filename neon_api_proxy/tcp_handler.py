import socketserver
import json

from neon_utils import LOG
from neon_api_proxy.controller import NeonAPIProxyController


class NeonAPITCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        default_encoding = 'utf-8'
        data = self.request.recv(1024).strip().decode(default_encoding)
        LOG.debug(f"Received request from '{self.client_address[0]}' : {data}")
        response = self.server.controller.resolve_query(json.loads(data))
        LOG.debug(f'Received response from controller: {response}')
        # Decoding all inner byte-like objects as they are not JSON-serializable
        normalized_response = {k: v.decode('utf-8', errors='replace') if isinstance(v, bytes) else v
                               for k, v in response.items()}
        encoded_response = json.dumps(normalized_response).encode(default_encoding)
        LOG.debug(f'Encoded response from controller: {encoded_response}')
        self.request.sendall(encoded_response)
