import socketserver
import json
import base64

from neon_utils import LOG
from neon_api_proxy.controller import NeonAPIProxyController

# Limit maximum size to 10 MB;
# Implied by the fact that TCP client aborts the connection once has its packet delivered to server
# thus preventing from sequential traversing
MAX_PACKET_SIZE = 10485760


def get_packet_data(socket, sequentially=False, batch_size=2048) -> bytes:
    """
        Gets all packet data by reading TCP socket stream sequentially
        :@param socket: TCP socket
        :@param sequentially: TCP socket
        :@param batch_size: size of packet added through one sequence

        :@return bytes string representing the received data
    """
    if sequentially:
        fragments = []
        while True:
            chunk = socket.recv(batch_size)
            if not chunk:
                break
            fragments.append(chunk)
        data = b''.join(fragments)
    else:
        data = bytes(socket.recv(MAX_PACKET_SIZE))
    return data


def decode_b64_msg(message: bytes) -> dict:
    """
        Decodes base64 bytes string to python dictionary
        @param message: string bytes to decode

        @return decoded dictionary
    """
    return eval(json.loads(base64.b64decode(message).decode()))


def encode_b64_msg(message: dict) -> bytes:
    """
        Encodes python dictionary into base64 bytes
        @param message: python dictionary to encode

        @return encoded bytes string
    """
    return base64.b64encode(json.dumps(str(message)).encode())


class NeonAPITCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_message = get_packet_data(self.request)
        received_message_decoded = decode_b64_msg(received_message)
        LOG.debug(f"Received request from '{self.client_address[0]}' : {received_message_decoded}")
        response = self.server.controller.resolve_query(received_message_decoded)
        LOG.debug(f'Received response from controller: {response}')
        encoded_response = encode_b64_msg(response)
        LOG.debug(f'Encoded response from controller: {encoded_response}')
        self.request.sendall(encoded_response)
