import arcade

from game.map.client_map import ClientMap
from game.map.map_generation_settings import MapGenerationSettings
from game.map.map_generator import MapGenerator
from game.map.server_map import ServerMap


class ServerGameState:
    def __init__(self, _map):
        self.game_running = False
        self.map: ServerMap = _map


    def start_new_game(self, new_map_settings: MapGenerationSettings, resource_manager, mods_manager):
        map_generator = MapGenerator(new_map_settings, resource_manager, mods_manager)
        self.map = map_generator.generate()
        self.game_running = True

    def serialize_full(self):
        return self.serialize() | {
            "map": self.map.serialize()
        }

    def serialize(self):
        return {"game_running": "ITS SNAPSHOT!!!"}


class ClientGameState:
    def __init__(self, snapshot):
        self.map: ClientMap = ClientMap(snapshot.get("map"))

    def draw(self):
        self.map.draw()
