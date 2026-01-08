import time
from http.client import responses
from socket import socket
from threading import Lock, Thread

from game.actions.events import Event, GameEvents
from game.game_state import ClientGameState
from network.client.network_connection import NetworkConnection
from network.client.request.client_requests import ClientRequest
from network.server.protocol import Protocol
from network.server.server_message import ServerResponse, ServerResponseType
from network.userdata import UserData


class InputHandler:
    pass


class GameClient:
    def __init__(self, config_manager, resource_manager):
        self.resource_manager = resource_manager
        self.userdata: UserData = config_manager.register_config("userdata", UserData)
        self.connection = NetworkConnection()

        self.game_state: ClientGameState = None
        self.player_id = None

        self.input_handler = InputHandler()
        self.commands_queue = None

        self.last_message_time = 0
        self.server_tick = 0

        self._receiving = False
        self._receive_thread = None
        self._lock = Lock()

    def draw(self):
        if self.game_state is None:
            return
        self.game_state.draw()

    def _handle_server_receive(self, response: ServerResponse):
        # print(response)
        if response.type == ServerResponseType.SNAPSHOT:
            for event in response.data["events"]:
                event = Event.from_dict(event)
                print(event.event_type)
                if event == GameEvents.GAME_STARTED:
                    self.game_state = ClientGameState(self.resource_manager, event.data)
                elif event == GameEvents.GAME_OVER:
                    self.game_state = None
            if self.game_state is not None:
                self.game_state.update_from_snapshot(response.data)
        elif response.type == ServerResponseType.ERROR:
            print("ERROR: ", response.data)
        elif response.type == ServerResponseType.DISCONNECT:
            print("DISCONNECTED: ", response.data)
            self.disconnect()

    def _receive_loop(self):
        while self._receiving:
            try:
                data = self.connection.receive()
                if data:
                    for resp in data:
                        self._handle_server_receive(ServerResponse.from_dict(resp))
                else:
                    time.sleep(0.05)
            except (ConnectionError, TimeoutError):
                self.disconnect()
                break

    def connect(self, ip, port, password):
        callback = self.connection.connect(ip, port)
        if callback.is_error():
            return callback
        self.connection.send([ClientRequest.create_connect_request(self.userdata, password).serialize()])

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
