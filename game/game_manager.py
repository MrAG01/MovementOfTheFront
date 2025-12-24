from configs.config_manager import ConfigManager
from configs.game_config import GameConfig
from core.callback import Callback
from game.game_state import ServerGameState
from game.map.map_generation_settings import MapGenerationSettings
from network.client.game_client import GameClient
from network.server.game_server import GameServer
from network.server.game_server_config import GameServerConfig


class GameManager:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.register_config("game_config", GameConfig)
        self.client = None
        self.server = None

    def _server_callbacks_listener(self, callback):
        print(callback)

    def connect_to_room(self, ip_address, password):
        self.client = GameClient()
        callback = self.client.connect(self.server.get_ip(), self.server.get_port())
        if callback.is_error():
            self.client.disconnect()
            self.client = None
            return callback
        return Callback.ok("Joined successfully.")

    def create_new_multiplayer_room(self, new_world_settings: MapGenerationSettings, resource_manager, mods_manager, max_players=2, password=None):
        self.shutdown()
        server_config = GameServerConfig(ip_address="localhost",
                                         max_players=max_players,
                                         password=password)
        server_game_state = ServerGameState.create(new_world_settings, resource_manager, mods_manager)
        self.server = GameServer(server_config=server_config,
                                 server_game_state=server_game_state)
        self.server.add_listener(self._server_callbacks_listener)
        callback = self.server.start()

        if callback.is_error():
            self.server.shutdown()
            self.server = None
            return callback

        self.client = GameClient()
        callback = self.client.connect(self.server.get_ip(), self.server.get_port())
        if callback.is_error():
            self.client.disconnect()
            self.client = None
            return callback
        return Callback.ok("Room was created successfully.")

    def create_new_single_player(self, new_world_settings: MapGenerationSettings, resource_manager, mods_manager):
        self.shutdown()
        server_config = GameServerConfig(ip_address="localhost",
                                         max_players=1,
                                         password=None)
        server_game_state = ServerGameState.create(new_world_settings, resource_manager, mods_manager)

        self.server = GameServer(server_config=server_config,
                                 server_game_state=server_game_state)
        self.server.add_listener(self._server_callbacks_listener)
        callback = self.server.start()
        if callback.is_error():
            self.server.shutdown()
            self.server = None
            return callback

        self.client = GameClient()
        callback = self.client.connect(self.server.get_ip(), self.server.get_port())
        if callback.is_error():
            self.client.disconnect()
            self.client = None
            return callback
        return Callback.ok("Singleplayer game was created successfully.")

    def shutdown(self):
        if self.client:
            self.client.disconnect()
            self.client = None
        if self.server:
            self.server.shutdown()
            self.server = None
