import numpy as np
import zlib
import base64


class ServerMap:
    def __init__(self, biomes_map: np.array = None, biome_names=None):
        self.biomes_map: np.array = biomes_map
        self.biome_names: dict[int, str] = biome_names

        self.cached_output_network_message = None

    @staticmethod
    def serialize_array(array: np.array):
        shape = array.shape
        #print("UNIQUE VALUES IN MAP:", np.unique(array))
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
