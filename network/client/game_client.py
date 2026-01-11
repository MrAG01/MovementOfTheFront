import time
from threading import Lock, Thread

import arcade

from game.actions.events import Event, GameEvents
from game.building.building_config import BuildingConfig
from game.camera import Camera
from game.deposits.server_deposit import ClientDeposit
from game.game_state.client_game_state import ClientGameState
from network.client.network_connection import NetworkConnection
from network.client.request.client_requests import ClientRequest
from network.server.server_message import ServerResponse, ServerResponseType
from network.userdata import UserData
from resources.handlers.texture_handle import TextureHandle
from resources.input.keyboard_manager import KeyboardManager
from resources.input.mouse_manager import MouseManager
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class InputHandler:
    def __init__(self, resource_manager, mods_manager, keyboard_manager, mouse_manager, tick_rate, send_callback,
                 client):
        self.pending_requests = []
        self.send_callback = send_callback
        self.client: GameClient = client

        self.keyboard_manager: KeyboardManager = keyboard_manager
        self.mouse_manager: MouseManager = mouse_manager

        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager

        self.tick_time = 1 / tick_rate
        self.time_counter = 0
        self.camera = None
        self._setup_key_binds()

        self.selected_building_config: BuildingConfig = None
        self.selected_building_type = None
        self.selected_building_texture = None

    def attach_camera(self, camera):
        self.camera = camera

    def _on_escape_pressed(self):
        self.selected_building_config = None
        self.selected_building_type = None
        self.selected_building_texture = None

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("unselect_building", on_pressed_callback=self._on_escape_pressed)
        self.mouse_manager.register_on_pressed_callback(self.on_mouse_pressed)

    def try_build(self, building_name):
        if self.selected_building_type == building_name:
            self.selected_building_type = None
            self.selected_building_texture = None
            self.selected_building_config = None
        else:
            self.selected_building_type = building_name
            self.selected_building_texture = self.resource_manager.get_texture(building_name)
            self.selected_building_config = self.mods_manager.get_building(building_name)

    def add_request(self, request):
        self.pending_requests.append(request)

    def update(self, delta_time):
        self.time_counter += delta_time
        if self.time_counter >= self.tick_time:
            self.time_counter = 0
            self.send_callback([request.serialize() for request in self.pending_requests])
            self.pending_requests.clear()

    def _get_closest_deposit(self, x, y):
        if self.selected_building_config.can_place_on_deposit:
            deposits_close = self.client.game_state.map.get_deposits_close_to(x, y)
            closest_deposit = [40 ** 2, None]
            for deposit in deposits_close:
                deposit: ClientDeposit
                dx, dy = deposit.position
                distance_sqr = (x - dx) ** 2 + (y - dy) ** 2
                if distance_sqr < closest_deposit[0]:
                    closest_deposit[0] = distance_sqr
                    closest_deposit[1] = deposit
            closest_deposit = closest_deposit[1]
            if closest_deposit is not None:
                return closest_deposit
        return None

    def on_mouse_pressed(self, x, y, button, modifiers):
        if self.camera is None:
            return
        if self.selected_building_type:
            x, y, _ = self.camera.unproject(arcade.Vec2(x, y))
            linked_deposit = self._get_closest_deposit(x, y)
            if linked_deposit:
                x, y = linked_deposit.position
            biome = self.client.game_state.map.get_biome(x, y)

            can_build = biome.can_build_on and (
                    (self.selected_building_config.can_place_on_deposit and linked_deposit is not None) or
                    self.selected_building_config.can_place_not_on_deposit)
            if can_build:
                self.add_request(ClientRequest.create_build_request(x, y, self.selected_building_type, linked_deposit))

    def draw(self, camera: Camera):
        if self.camera is None:
            self.attach_camera(camera)

        if self.selected_building_texture:
            sx, sy = self.mouse_manager.get_mouse_pos()
            x, y, _ = camera.unproject(arcade.Vec2(sx, sy))
            zoom_k = 1 / camera.zoom
            linked_deposit = self._get_closest_deposit(x, y)

            if linked_deposit:
                x, y = linked_deposit.position
            biome = self.client.game_state.map.get_biome(x, y)

            can_build = biome.can_build_on and (
                        (self.selected_building_config.can_place_on_deposit and linked_deposit is not None) or
                        self.selected_building_config.can_place_not_on_deposit)

            color = arcade.color.Color(0, 255, 0) if can_build else arcade.color.Color(255, 0, 0)

            self.selected_building_texture.draw(x, y, zoom_k, zoom_k, color=color)


class GameClient:
    def __init__(self, config_manager, resource_manager, mods_manager, keyboard_manager, mouse_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager

        self.userdata: UserData = config_manager.register_config("userdata", UserData)
        self.connection = NetworkConnection()

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
            for event in response.data["events"]:
                event = Event.from_dict(event)
                if event == GameEvents.GAME_STARTED:
                    self.game_state = ClientGameState(self.resource_manager, self.mods_manager,
                                                      response.data["data"] | event.data)
                elif event == GameEvents.GAME_OVER:
                    self.game_state = None
            if self.game_state is not None:
                self.game_state.update_from_snapshot(response.data["data"])

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
