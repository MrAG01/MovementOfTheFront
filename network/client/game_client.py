import time
from threading import Lock, Thread
from game.actions.events import Event, GameEvents
from game.camera import Camera
from game.game_state.client_game_state import ClientGameState
from input.input_handler import InputHandler
from network.client.network_connection import NetworkConnection
from network.client.request.client_requests import ClientRequest
from network.server.server_message import ServerResponse, ServerResponseType
from network.userdata import UserData
from resources.handlers.music_handle import MusicHandle
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class GameClient:
    def __init__(self, config_manager, resource_manager: ResourceManager, mods_manager, keyboard_manager,
                 mouse_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager

        self.userdata: UserData = config_manager.register_config("userdata", UserData)
        self.connection = NetworkConnection(on_disconnect_callback=self._handle_disconnection)

        self.camera: Camera = None

        self.game_state: ClientGameState = None
        self.player_id = None

        self.buildings_sounds_noise: MusicHandle = resource_manager.get_music("buildings_noise")

        self.input_handler = InputHandler(self.resource_manager, self.mods_manager, keyboard_manager,
                                          mouse_manager, 10, self.connection.send, self)
        self.commands_queue = None

        self.last_message_time = 0
        self.server_tick = 0

        self.game_view = None

        self._receiving = False
        self._receive_thread = None
        self._lock = Lock()

        self.snapshot_listeners = []
        self.on_game_start_callbacks = []
        self.on_game_disconnect_callback = []

        self.client_names = []

    def attach_game_view(self, game_view):
        self.game_view = game_view

    def attach_camera(self, camera):
        self.camera = camera

    def get_clients_list(self):
        return self.client_names

    def _handle_disconnection(self):
        # print(f"HANDLING DISCONNECTION: {len(self.on_game_disconnect_callback)}")
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

    def draw(self, camera: Camera):
        zoom = camera.zoom
        projection = camera.projection

        # player = self.get_self_player()
        # if player:
        #    buildings_around = player.get_buildings_in_rect(projection.lbwh)
        # print(len(buildings_around))
        #    self.buildings_sounds_noise.set_volume(0.01 * len(buildings_around) * zoom)

        if self.game_state is None:
            return
        has_alpha = self.input_handler.units_mode
        self.game_state.draw(camera, has_alpha)
        self.input_handler.draw(camera)

    def _handle_server_receive(self, response: ServerResponse):
        if response.type == ServerResponseType.CONNECT_MESSAGE:
            self.player_id = response.data
            #print("CONNECTED, ID: ", self.player_id)
        if response.type == ServerResponseType.SNAPSHOT:
            self.client_names = response.data["client_names"]
            for event in response.data["snapshot"]["events"]:
                event = Event.from_dict(event)
                if event == GameEvents.GAME_STARTED:
                   # print("GAME STARTED!!!")
                    self.game_state = ClientGameState(self.resource_manager, self.mods_manager,
                                                      response.data["snapshot"]["data"] | event.data, self.player_id)
                   # print("GAME STATE CREATED SUCCESSFULLY!!! ")
                    self_player = self.get_self_player()
                    if self_player is not None:
                        town_hall = self_player.get_town_hall()
                        if town_hall is not None:
                            if self.camera is not None:
                                self.camera.focus_at(town_hall.position, town_hall.size)

                    #self.buildings_sounds_noise.play(volume=1.0,
                    #                                 loop=True)
                    for callback in self.on_game_start_callbacks:
                        callback()
                elif event == GameEvents.GAME_OVER:
                    if self.game_view:
                        self.game_view.init_winner_menu(event.data)
                elif event == GameEvents.PLAYER_DIED:
                    died_player_id = event.data
                    #print(f"PLAYER DIED: {died_player_id}, {self.player_id}")
                    if died_player_id == self.player_id:

                        self.input_handler.on_self_died()

            if self.game_state is not None:
                self.game_state.update_from_snapshot(response.data["snapshot"]["data"])

            self._notify_snapshot_listeners()

        elif response.type == ServerResponseType.ERROR:
            print("ERROR: ", response.data)
        elif response.type == ServerResponseType.DISCONNECT:
          #  print("DISCONNECTED: ", response.data)
            self.disconnect()

    def _receive_loop(self):
        while self._receiving:
            try:
                data = self.connection.receive()
                if data:
                    for resp in data:
                        self._handle_server_receive(ServerResponse.from_dict(resp))
                else:
                    time.sleep(1 / 20)
            except (ConnectionError, TimeoutError):
                # self.disconnect()
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
        if self.connection:
            self.connection.close()
