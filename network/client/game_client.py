import time
from socket import socket
from threading import Lock, Thread

from game.game_state import ClientGameState
from network.client.network_connection import NetworkConnection


class InputHandler:
    pass


class GameClient:
    def __init__(self):
        self.connection = NetworkConnection()

        self.game_state = ClientGameState()
        self.player_id = None

        self.input_handler = InputHandler()
        self.commands_queue = None

        self.last_message_time = 0
        self.server_tick = 0

        self._receiving = False
        self._receive_thread = None
        self._lock = Lock()

    def _handle_server_receive(self, data):
        print("MESSAGE FROM SERVER:", data)

    def _receive_loop(self):
        while self._receiving:
            try:
                data = self.connection.receive()
                if data:
                    self._handle_server_receive(data)
                else:
                    time.sleep(0.05)
            except (ConnectionError, socket.timeout):
                self.disconnect()
                break

    def connect(self, ip, port):
        callback = self.connection.connect(ip, port)
        if callback.is_error():
            return callback

        self._receiving = True
        self._receive_thread = Thread(
            target=self._receive_loop,
            daemon=True,
            name="ClientReceiveThread"
        )
        self._receive_thread.start()
        return callback

    def disconnect(self):
        with self._lock:
            self._receiving = False
        if self._receive_thread:
            self._receive_thread.join(timeout=0.1)
        if self.connection.connected:
            self.connection.close()
