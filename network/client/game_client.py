import time
from fileinput import close
from threading import Lock, Thread
import arcade
import pyglet

from game.actions.events import Event, GameEvents
from game.building.building_config import BuildingConfig
from game.building.client_building import ClientBuilding
from game.camera import Camera
from game.deposits.client_deposit import ClientDeposit
from game.game_state.client_game_state import ClientGameState
from network.client.network_connection import NetworkConnection
from network.client.request.client_requests import ClientRequest
from network.server.server_message import ServerResponse, ServerResponseType
from network.userdata import UserData
from resources.input.keyboard_manager import KeyboardManager
from resources.input.mouse_manager import MouseManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class InputHandler:
    def __init__(self, resource_manager, mods_manager, keyboard_manager, mouse_manager, tick_rate, send_callback,
                 client):
        self.pending_requests = []
        self.send_callback = send_callback
        self.client: GameClient = client
        self.player = self.client.get_self_player()

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

        self.wanted_select_building_exist = None
        self.selected_building_exist = None

    def _try_to_get_player(self):
        self.player = self.client.get_self_player()

    def attach_camera(self, camera):
        self.camera = camera

    def unselect_building_place(self):
        self.selected_building_config = None
        self.selected_building_type = None
        self.selected_building_texture = None

    def _on_escape_pressed(self):
        self.unselect_building_place()

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("unselect_building", on_pressed_callback=self._on_escape_pressed)
        self.mouse_manager.register_on_pressed_callback(self.on_mouse_pressed)

    def try_build(self, building_name):
        if self.selected_building_type == building_name:
            self.unselect_building_place()
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
            self.pending_requests.append(ClientRequest.create_ping_request())
            self.send_callback([request.serialize() for request in self.pending_requests])
            self.pending_requests.clear()
        if self.camera is None:
            return
        sx, sy = self.mouse_manager.get_mouse_pos()
        x, y, _ = self.camera.unproject(arcade.Vec2(sx, sy))

        closest_building = self._get_closest_buildings(x, y)

        if closest_building is not None:
            # print(closest_building.position)
            if self.wanted_select_building_exist is not None:
                if self.wanted_select_building_exist != closest_building:
                    self.wanted_select_building_exist.disable_outline()
                    self.wanted_select_building_exist = closest_building
                    self.wanted_select_building_exist.enable_outline()
            else:
                self.wanted_select_building_exist = closest_building
                self.wanted_select_building_exist.enable_outline()
        else:
            if self.wanted_select_building_exist is not None:
                self.wanted_select_building_exist.disable_outline()
            self.wanted_select_building_exist = None

    def _get_closest_deposit(self, x, y):
        if self.selected_building_config.can_place_on_deposit:
            deposits_close = self.client.game_state.map.get_deposits_close_to(x, y)
            closest_deposit = [40 ** 2, None]
            for deposit in deposits_close:
                deposit: ClientDeposit
                if deposit.has_owner():
                    continue
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
        if button == pyglet.window.mouse.RIGHT:
            if self.selected_building_type:
                self.unselect_building_place()
        if button != pyglet.window.mouse.LEFT:
            return

        if self.selected_building_exist is not None:
            self.selected_building_exist.disable_selection()
            self.selected_building_exist = None

        if self.selected_building_type:
            x, y, _ = self.camera.unproject(arcade.Vec2(x, y))
            linked_deposit = self._get_closest_deposit(x, y)
            if linked_deposit:
                x, y = linked_deposit.position
                arg = linked_deposit.can_place_building_on(self.selected_building_type)
            else:
                arg = False
            biome = self.client.game_state.map.get_biome(x, y)

            can_build = biome.can_build_on and (
                    (self.selected_building_config.can_place_on_deposit and arg) or
                    self.selected_building_config.can_place_not_on_deposit)
            if can_build:
                self.add_request(ClientRequest.create_build_request(x, y, self.selected_building_type, linked_deposit))
        elif self.wanted_select_building_exist is not None:
            self.selected_building_exist = self.wanted_select_building_exist
            self.selected_building_exist.enable_selection()

    def _get_closest_buildings(self, x, y):
        if self.player is None:
            self._try_to_get_player()
            return

        close_buildings = self.player.get_closest_buildings_to(x, y)
        # print(len(close_buildings))
        closest_buildings = [20 ** 2, None]
        for building in close_buildings:
            building: ClientBuilding

            dx, dy = building.position
            distance_sqr = (x - dx) ** 2 + (y - dy) ** 2
            if distance_sqr < closest_buildings[0]:
                closest_buildings[0] = distance_sqr
                closest_buildings[1] = building
        closest_building = closest_buildings[1]
        if closest_building is not None:
            return closest_building
        return None

    def draw(self, camera: Camera):
        if self.camera is None:
            self.attach_camera(camera)

        sx, sy = self.mouse_manager.get_mouse_pos()
        x, y, _ = camera.unproject(arcade.Vec2(sx, sy))

        if self.selected_building_texture:
            zoom_k = 1 / camera.zoom
            linked_deposit = self._get_closest_deposit(x, y)

            if linked_deposit:
                x, y = linked_deposit.position
                arg = linked_deposit.can_place_building_on(self.selected_building_type)
            else:
                arg = False
            biome = self.client.game_state.map.get_biome(x, y)

            can_build = biome.can_build_on and (
                    (self.selected_building_config.can_place_on_deposit and arg) or
                    self.selected_building_config.can_place_not_on_deposit)
            color = arcade.color.Color(0, 255, 0) if can_build else arcade.color.Color(255, 0, 0)
            self.selected_building_texture.draw(x, y, zoom_k, zoom_k, color=color)


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
