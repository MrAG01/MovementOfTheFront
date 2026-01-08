import time
from threading import Thread, Lock
from game.game_state import ServerGameState
from network.client.request.client_request_type import ClientRequestType
from network.server.client_handler import ClientHandler
from network.server.game_server_config import GameServerConfig
from core.callback import Callback
import socket
from network.server.protocol import Protocol
from network.server.server_message import ServerResponse
from network.userdata import UserData


class GameServer:
    def __init__(self, ip_address, server_config: GameServerConfig, server_game_state: ServerGameState,
                 server_logger_manager=None):
        self.server_logger_manager = server_logger_manager
        self.ip_address = ip_address

        self.thread_lock = Lock()

        self.server_config = server_config
        self.listeners_callbacks = set()
        self.server_socket: socket.socket = None
        self._client_threads = []

        self._main_cycle_thread: Thread = None
        self._running = False

        self.clients_names = []
        self.clients = {}  # id -> handler
        self.game_state = server_game_state
        self.next_player_id = 1

    def start_game(self):
        self.game_state.start_game()

    def serialize_for_server_logger(self):
        return self.server_config.serialize_for_server_logger() | {
            "ip_address": self.get_ip(),
            "port": self.get_port(),
            "players": len(self.clients)
        }

    def _add_in_server_logger(self):
        if self.server_logger_manager is None:
            return
        thread = Thread(target=self.server_logger_manager.add_server,
                        args=(self.serialize_for_server_logger(),),
                        daemon=True)
        thread.start()

    def _update_server_logger(self):
        if self.server_logger_manager is None:
            return
        thread = Thread(target=self.server_logger_manager.update_server,
                        args=(self.serialize_for_server_logger(),),
                        daemon=True)
        thread.start()

    def _delete_server_from_logger(self):
        if self.server_logger_manager is None:
            return
        thread = Thread(target=self.server_logger_manager.delete_server,
                        args=({"ip_address": self.get_ip()},),
                        daemon=True)
        thread.start()

    def add_listener(self, callback):
        self.listeners_callbacks.add(callback)

    def remove_listener(self, callback):
        if callback in self.listeners_callbacks:
            self.listeners_callbacks.remove(callback)

    def _send_message_to_listeners(self, message: Callback):
        for callback in self.listeners_callbacks:
            callback(message)

    def get_ip(self):
        return self.ip_address

    def get_port(self):
        if self.server_socket is None:
            return None
        if hasattr(self, "_port_cache") and self._port_cache is not None:
            return self._port_cache
        else:
            self._port_cache = self.server_socket.getsockname()[1]
        return self._port_cache

    def get_max_players(self):
        return self.server_config.get_max_players()

    def has_password(self):
        return self.server_config.has_password()

    def _get_password(self):
        return self.server_config.get_password()

    def _is_valid_password(self, password_hash):
        return self._get_password() == password_hash

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
        with self.thread_lock:
            handler = ClientHandler(
                client_id=self.next_player_id,
                client_socket=client_socket,
                address=address,
                on_commands=self._handle_player_commands,
                on_disconnect=self._handle_player_disconnect
            )
            self.clients[self.next_player_id] = handler
            self.next_player_id += 1
        self._update_server_logger()
        handler.run()

    def _handle_player_commands(self, client_handler, commands):
        for command in commands:
            match command.type:
                case ClientRequestType.CONNECT:
                    if self.server_config.has_password():
                        if not self._is_valid_password(command.data.get("password")):
                            client_handler.on_shutdown()
                            break
                    client_handler.userdata = UserData.from_dict(command.data["user_data"])
                    client_handler.make_valid()
                    self.clients_names.append(client_handler.userdata.username)
                case _:
                    print(command.type)
                    print(command.data)

    def _handle_player_disconnect(self, client_id):
        del self.clients[client_id]

    def _start_handle_client_thread(self, client_socket, address):
        if len(self._client_threads) >= self.get_max_players():
            client_socket.sendall(Protocol.encode(ServerResponse.create_disconnect_message("Server is full").serialize()))
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
        snapshot = ServerResponse.create_snapshot(self.game_state.serialize())
        snapshot_raw = Protocol.encode(snapshot.serialize())

        for client_id, client_handle in self.clients.items():
            client_handle.send(snapshot_raw)

    def _game_loop(self):
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

    def _run_main_cycle(self):
        try:
            self._main_cycle()
        except Exception as error:
            self._send_message_to_listeners(Callback.error(f"Server error: {error}."))
        finally:
            self._on_shutdown()

    def start(self):
        try:
            self._init_sockets()
            self._running = True
            callback = Callback.ok(f"Server started on {self.get_ip()}:{self.get_port()}")
            self._main_cycle_thread = Thread(target=self._run_main_cycle, daemon=True)
            self._game_loop_thread = Thread(target=self._game_loop, daemon=True)
            self._main_cycle_thread.start()
            self._game_loop_thread.start()
            self._add_in_server_logger()

            self._send_message_to_listeners(callback)
            return callback
        except Exception as error:
            callback = Callback.error(f"Unexpected error: {error}. Server wasnt created.")
            self._send_message_to_listeners(callback)
            return callback

    def shutdown(self):
        self._on_shutdown()

    def _on_shutdown(self):
        if not self._running:
            return
        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None
        self._running = False
        if hasattr(self, "_port_cache"):
            self._port_cache = None
        for thread in self._client_threads:
            thread.join(timeout=2.0)
        self._game_loop_thread.join(timeout=2.0)
        self._main_cycle_thread.join(timeout=3.0)
        self._delete_server_from_logger()
