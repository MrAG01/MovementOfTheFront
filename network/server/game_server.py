from threading import Thread

from network.server.game_server_config import GameServerConfig
from network.server.server_callbacks import ServerCallback
import socket


class GameServer:
    def __init__(self, server_config: GameServerConfig):
        self.server_config = server_config
        self.listeners_callbacks = set()
        self.server_socket: socket.socket = None
        self._client_threads = []
        self._running = False

    def add_listener(self, callback):
        self.listeners_callbacks.add(callback)

    def remove_listener(self, callback):
        if callback in self.listeners_callbacks:
            self.listeners_callbacks.remove(callback)

    def _send_message_to_listeners(self, message: ServerCallback):
        for callback in self.listeners_callbacks:
            callback(message)

    def get_ip(self):
        return self.server_config.get_ip()

    def get_port(self):
        if self.server_socket is None:
            return None
        return self.server_socket.getsockname()[1]

    def get_max_players(self):
        return self.server_config.get_max_players()

    def has_password(self):
        return self.server_config.has_password()

    def _get_password_hash(self):
        return self.server_config.get_password_hash()

    def _is_valid_password(self, password_hash):
        return self._get_password_hash() == password_hash

    def _get_free_port(self):
        pass

    def _init_sockets(self):
        if self.server_socket is not None:
            return
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.get_ip(), 0))
        self.server_socket.listen()

    def _handle_client(self, client_socket, address):
        pass

    def _start_handle_client_thread(self, client_socket, address):
        if len(self._client_threads) >= self.get_max_players():
            client_socket.send(b"Server is full")
            client_socket.close()
            return

        client_thread = Thread(target=self._handle_client, args=(client_socket, address), daemon=True)
        client_thread.start()
        self._client_threads.append(client_thread)

    def _main_cycle(self):
        self._send_message_to_listeners(ServerCallback.ok("Waiting for connections..."))
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                self._send_message_to_listeners(ServerCallback.ok(f"New connection: {address}"))

                self._start_handle_client_thread(client_socket, address)

            except socket.timeout:
                continue
            except OSError as error:
                if self._running:
                    self._send_message_to_listeners(ServerCallback.error(f"Client accept error: {error}"))
                else:
                    break

    def start(self):
        try:
            self._init_sockets()
            self._running = True
            self._send_message_to_listeners(ServerCallback.ok(f"Server started on {self.get_ip()}:{self.get_port()}"))
            self._main_cycle()
        except Exception as error:
            self._send_message_to_listeners(ServerCallback.error(f"Unexpected error: {error}. Server wasnt created."))
        finally:
            self.on_shutdown()

    def on_shutdown(self):
        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None
            self._running = False

        for thread in self._client_threads:
            thread.join(timeout=2.0)
