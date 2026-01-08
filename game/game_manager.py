import hashlib

from configs.config_manager import ConfigManager
from core.callback import Callback
from game.camera import Camera
from game.game_state import ServerGameState
from game.map.map_generation_settings import MapGenerationSettings
from network.client.game_client import GameClient
from network.server.game_server import GameServer
from network.server.game_server_config import GameServerConfig


class GameManager:
    def __init__(self, config_manager: ConfigManager, resource_manager):
        self.config_manager = config_manager
        self.resource_manager = resource_manager
        self.client: GameClient = None
        self.server: GameServer = None

    def _server_callbacks_listener(self, callback):
        print(callback)

    def apply_camera(self, camera: Camera):
        if self.client.game_state:
            width, height = self.client.game_state.map.get_size()
            camera.define_borders(width, height)

    def connect_to_room(self, ip_address, port, password):
        self.client = GameClient(self.config_manager, self.resource_manager)
        callback = self.client.connect(ip_address, port, password)
        if callback.is_error():
            self.client.disconnect()
            self.client = None
            return callback
        return Callback.ok("Joined successfully.")

    def create_new_multiplayer_room(self, game_state: ServerGameState, server_config: GameServerConfig,
                                    server_logger_manager):
        self.shutdown()
        self.server = GameServer(ip_address="localhost",
                                 server_config=server_config,
                                 server_game_state=game_state,
                                 server_logger_manager=server_logger_manager)
        self.server.add_listener(self._server_callbacks_listener)
        callback = self.server.start()

        if callback.is_error():
            self.server.shutdown()
            self.server = None
            return callback

        self.client = GameClient(self.config_manager, self.resource_manager)
        callback = self.client.connect(self.server.get_ip(), self.server.get_port(), server_config.get_password())
        if callback.is_error():
            self.client.disconnect()
            self.client = None
            return callback
        return Callback.ok("Room was created successfully.")

    def start_game(self):
        if self.server is None:
            return
        self.server.start_game()

    def draw(self):
        self.client.draw()

    def shutdown(self):
        if self.client:
            self.client.disconnect()
            self.client = None
        if self.server:
            self.server.shutdown()
            self.server = None
