import json
import socket
import struct

from core.callback import Callback
from network.server.protocol import Protocol


class NetworkConnection:
    def __init__(self, ip="localhost", port=8888, on_disconnect_callback=None):
        self._clear()
        self.connected = False
        if ip and port:
            self.connect(ip, port)
        self.on_disconnect_callback = on_disconnect_callback


    def _clear(self):
        self.ip = None
        self.port = None
        self.socket = None
        self.buffer = b""

    def connect(self, ip, port):
        if self.connected:
            self.close()
        self._clear()

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.socket.setblocking(False)
            self.connected = True
            self.ip = ip
            self.port = port
            return Callback.ok("Connected to server successfully")
        except Exception as error:
            self.connected = False
            return Callback.error(f"Connection error: {error}")

    def send(self, data):
        try:
            encoded = Protocol.encode(data)
            self.socket.sendall(encoded)
        except ConnectionResetError:
            self.close()

    def receive(self):
        received_messages = []
        try:
            chunk = self.socket.recv(4096)
            if chunk:
                self.buffer += chunk
        except (socket.timeout, BlockingIOError):
            pass
        except ConnectionError:
            return []
        while len(self.buffer) >= Protocol.HEADER_SIZE:
            try:
                data, read_size = Protocol.decode(self.buffer)
                received_messages.append(data)
                self.buffer = self.buffer[read_size:]
            except ValueError:
                break
            except (json.JSONDecodeError, struct.error) as error:
                print(f"Decoding error: {error}")
                self.buffer = b""
                break

        return received_messages

    def close(self):
        if self.connected and self.socket:
            self.socket.close()
        self._clear()
        self.connected = False
        self.on_disconnect_callback()
