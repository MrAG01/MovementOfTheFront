from game.deposits.server_deposit import ServerDeposit
from game.map.biome.biome import Biome
import numpy as np
import zlib
import base64

from resources.mods.mods_manager.mods_manager import ModsManager


class ServerMap:
    def __init__(self, deposits, mods_manager, biomes_map: np.array = None, biome_names=None):
        self.deposits: dict[int, ServerDeposit] = deposits
        self.mods_manager: ModsManager = mods_manager
        self.biomes_map: np.array = biomes_map
        self.biome_names: dict[int, str] = biome_names
        self.cached_output_network_message = None
        self.width, self.height = self.biomes_map.shape

    def get_biome(self, x, y) -> Biome:
        biome_name = self.biome_names[self.biomes_map[self.height - int(y)][int(x)]]
        biome = self.mods_manager.get_biome(biome_name)
        # print(f"TRYING TO GET BIOME: {biome_name}, SUCCESS: {biome is not None}")
        return biome

    def update(self, delta_time):
        for deposit in self.deposits.values():
            deposit.update(delta_time)

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

    def serialize_dynamic(self):
        return {
            "deposits": {deposit_id: deposit.serialize_dynamic() for deposit_id, deposit in self.deposits.items() if
                         deposit.is_dirty()}
        }

    def serialize_static(self):
        if self.cached_output_network_message is None:
            self.cached_output_network_message = {
                "biome_names": self.biome_names,
                "biomes_map": ServerMap.serialize_array(self.biomes_map),
                "deposits": {deposit_id: deposit.serialize_static() for deposit_id, deposit in self.deposits.items()}
            }
        return self.cached_output_network_message
