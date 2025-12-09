import time
from threading import Thread

from game.game_state import GameState
from network.server.game_server_config import GameServerConfig
from core.callback import Callback
import socket


class ClientHandler:
    def __init__(self, client_id, client_socket, address, on_command, on_disconnect):
        self.client_id = client_id
        self.client_socket = client_socket
        self.address = address
        self.on_command = on_command
        self.on_disconnect = on_disconnect

    def run(self):
        pass

    def on_shutdown(self):
        pass


class GameServer:
    def __init__(self, server_config: GameServerConfig):
        self.server_config = server_config
        self.listeners_callbacks = set()
        self.server_socket: socket.socket = None
        self._client_threads = []
        self._running = False

        self.clients = {}
        self.game_state = GameState()
        self.next_player_id = 1

    def add_listener(self, callback):
        self.listeners_callbacks.add(callback)

    def remove_listener(self, callback):
        if callback in self.listeners_callbacks:
            self.listeners_callbacks.remove(callback)

    def _send_message_to_listeners(self, message: Callback):
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
        handler = ClientHandler(
            client_id=self.next_player_id,
            client_socket=client_socket,
            address=address,
            on_command=self._handle_player_command,
            on_disconnect=self._handle_player_disconnect
        )
        self.clients[self.next_player_id] = handler
        self.next_player_id += 1
        handler.run()

    def _handle_player_command(self, client_handler, command):
        pass

    def _handle_player_disconnect(self, client_id):
        self.clients[client_id].on_shutdown()
        del self.clients[client_id]

    def _start_handle_client_thread(self, client_socket, address):
        if len(self._client_threads) >= self.get_max_players():
            client_socket.send(b"Server is full")
            client_socket.close()
            return

        client_thread = Thread(target=self._handle_client, args=(client_socket, address), daemon=True)
        client_thread.start()
        self._client_threads.append(client_thread)

    def _process_commands(self):
        pass

    def _update_game_state(self):
        pass

    def _send_snapshots(self):
        pass

    def game_loop(self):
        tick_rate = 20
        tick_duration = 1.0 / tick_rate
        while self._running:
            start_time = time.time()

            self._process_commands()
            self._update_game_state()
            self._send_snapshots()

            end_time = time.time()
            sleep_time = max(0.0, tick_duration - (end_time - start_time))
            time.sleep(sleep_time)

            self.game_state.tick += 1
            self.game_state.time = end_time

    def _main_cycle(self):
        self._send_message_to_listeners(Callback.ok("Waiting for connections..."))
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                self._send_message_to_listeners(Callback.ok(f"New connection: {address}"))

                self._start_handle_client_thread(client_socket, address)

            except socket.timeout:
                continue
            except OSError as error:
                if self._running:
                    self._send_message_to_listeners(Callback.error(f"Client accept error: {error}"))
                else:
                    break

    def start(self):
        try:
            self._init_sockets()
            self._running = True
            self._send_message_to_listeners(Callback.ok(f"Server started on {self.get_ip()}:{self.get_port()}"))
            self._main_cycle()
        except Exception as error:
            self._send_message_to_listeners(Callback.error(f"Unexpected error: {error}. Server wasnt created."))
        finally:
            self.on_shutdown()

    def on_shutdown(self):
        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None
            self._running = False

        for thread in self._client_threads:
            thread.join(timeout=2.0)
