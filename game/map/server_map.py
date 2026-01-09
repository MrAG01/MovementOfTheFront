from game.map.biome.biome import Biome
import numpy as np
import zlib
import base64

from resources.mods.mods_manager.mods_manager import ModsManager


class ServerMap:
    def __init__(self, mods_manager, biomes_map: np.array = None, biome_names=None):
        self.mods_manager: ModsManager = mods_manager
        self.biomes_map: np.array = biomes_map
        self.biome_names: dict[int, str] = biome_names
        self.cached_output_network_message = None

    def get_biome(self, x, y) -> Biome:
        biome_name = self.biome_names[self.biomes_map[x, y]]
        return self.mods_manager.get_biome(biome_name)

    @staticmethod
    def serialize_array(array: np.array):
        shape = array.shape
        # print("UNIQUE VALUES IN MAP:", np.unique(array))
        return {
            "width": shape[1],
            "height": shape[0],
            "data": base64.b64encode(zlib.compress(array.tobytes())).decode('utf-8'),
            "data_type": str(array.dtype)
        }

    def serialize(self):
        if self.cached_output_network_message is None:
            self.cached_output_network_message = {
                "biome_names": self.biome_names,
                "biomes_map": ServerMap.serialize_array(self.biomes_map)
            }
        return self.cached_output_network_message
