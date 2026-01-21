import time
from threading import Lock, Thread
import arcade
import pyglet

from GUI.ui_building_info_tablet import UIBuildingMenuTablet, UIBuildingBaseMenu
from game.actions.events import Event, GameEvents
from game.building.building_config import BuildingConfig
from game.building.client_building import ClientBuilding
from game.camera import Camera
from game.deposits.client_deposit import ClientDeposit
from game.game_state.client_game_state import ClientGameState
from input.input_handler import InputHandler
from network.client.network_connection import NetworkConnection
from network.client.request.client_requests import ClientRequest
from network.server.server_message import ServerResponse, ServerResponseType
from network.userdata import UserData
from input.keyboard_manager import KeyboardManager
from input.mouse_manager import MouseManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class GameClient:
    def __init__(self, config_manager, resource_manager, mods_manager, keyboard_manager, mouse_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager

        self.userdata: UserData = config_manager.register_config("userdata", UserData)
        self.connection = NetworkConnection(on_disconnect_callback=self._handle_disconnection)

        self.game_state: ClientGameState = None
        self.player_id = None

        self.input_handler = InputHandler(self.resource_manager, self.mods_manager, keyboard_manager,
                                          mouse_manager, 10, self.connection.send, self)
        self.commands_queue = None

        self.last_message_time = 0
        self.server_tick = 0

        self._receiving = False
        self._receive_thread = None
        self._lock = Lock()

        self.snapshot_listeners = []
        self.on_game_start_callbacks = []
        self.on_game_disconnect_callback = []

        self.client_names = []

    def get_clients_list(self):
        return self.client_names

    def _handle_disconnection(self):
        for callback in self.on_game_disconnect_callback:
            callback()

    def add_on_game_disconnect_callback(self, callback):
        self.on_game_disconnect_callback.append(callback)

    def remove_on_game_disconnect_callback(self, callback):
        if callback in self.on_game_disconnect_callback:
            self.on_game_disconnect_callback.remove(callback)

    def add_on_game_start_callback(self, callback):
        self.on_game_start_callbacks.append(callback)

    def remove_on_game_start_callback(self, callback):
        if callback in self.on_game_start_callbacks:
            self.on_game_start_callbacks.remove(callback)

    def add_on_snapshot_listener(self, callback):
        self.snapshot_listeners.append(callback)

    def _notify_snapshot_listeners(self):
        for callback in self.snapshot_listeners:
            callback(self)

    def get_self_player(self):
        if self.game_state:
            return self.game_state.players[self.player_id]

    def add_request(self, request):
        self.input_handler.add_request(request)

    def update(self, delta_time, pause):
        if not pause:
            self.input_handler.update(delta_time)
        if self.game_state:
            self.game_state.update_visual(delta_time)

    def draw(self, camera):
        if self.game_state is None:
            return
        self.game_state.draw(camera)
        self.input_handler.draw(camera)

    def _handle_server_receive(self, response: ServerResponse):

        if response.type == ServerResponseType.CONNECT_MESSAGE:
            self.player_id = response.data
            print("CONNECTED, ID: ", self.player_id)
        if response.type == ServerResponseType.SNAPSHOT:
            self.client_names = response.data["client_names"]
            for event in response.data["snapshot"]["events"]:
                event = Event.from_dict(event)
                if event == GameEvents.GAME_STARTED:
                    self.game_state = ClientGameState(self.resource_manager, self.mods_manager,
                                                      response.data["snapshot"]["data"] | event.data)
                    for callback in self.on_game_start_callbacks:
                        callback()
                elif event == GameEvents.GAME_OVER:
                    self.game_state = None
            if self.game_state is not None:
                self.game_state.update_from_snapshot(response.data["snapshot"]["data"])

            self._notify_snapshot_listeners()

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
                    time.sleep(1 / 10)
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
