from game.map.map_generation_settings import MapGenerationSettings
from game.map.server_map import ServerMap


class ServerGameState:
    def __init__(self, _map):
        self.game_started = False
        self.map = _map

    @classmethod
    def create(cls, new_map_settings: MapGenerationSettings):
        game = cls(_map=ServerMap.generate(new_map_settings))
        return game


class ClientGameState:
    pass
