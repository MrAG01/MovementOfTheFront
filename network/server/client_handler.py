import socket

from network.client.request.client_requests import ClientRequest
from network.server.protocol import Protocol
from network.userdata import UserData


class ClientHandler:
    def __init__(self, client_id, client_socket, address, on_commands, on_disconnect):
        self.client_id = client_id
        self.client_socket = client_socket
        self.address = address
        self.on_commands = on_commands
        self.on_disconnect = on_disconnect
        self.buffer = bytearray()
        self.valid = False
        self.running = False

        self.userdata: UserData = None

    def make_valid(self):
        self.valid = True

    def is_valid(self):
        return self.valid

    def get_userdata(self):
        return self.userdata

    def send(self, data):
        try:
            self.client_socket.sendall(data)
        except (ConnectionError, socket.error):
            self.on_shutdown()

    def _decode_client_message(self, data):
        requests = []
        for raw_request in data:
            requests.append(ClientRequest.from_dict(raw_request))
        return requests

    def is_running(self):
        return self.running

    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                self.buffer.extend(data)
                while len(self.buffer) >= Protocol.HEADER_SIZE:
                    message, size = Protocol.decode(bytes(self.buffer))
                    requests: list[ClientRequest] = self._decode_client_message(message)
                    if size > 0:
                        self.on_commands(self, requests)
                        del self.buffer[:size]
                    else:
                        break
            except (socket.timeout, ConnectionError):
                break
        self.on_shutdown()

    def on_shutdown(self):
        if self.running:
            self.running = False
            self.on_disconnect(self.client_id)