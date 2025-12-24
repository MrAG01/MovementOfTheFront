from configs.base_config import BaseConfig
from game.map.biome.biome_type import BiomeType


class Biome(BaseConfig):
    def __init__(self):
        self.can_build_on = True
        self.build_cost_multiplayer = 1.0
        self.build_time_multiplayer = 1.0

        self.type: BiomeType = BiomeType.LAND

    def serialize(self):
        return {
            "type": self.type.value,
            "can_build_on": self.can_build_on,
            "build_cost_multiplayer": self.build_cost_multiplayer,
            "build_time_multiplayer": self.build_time_multiplayer
        }

    def can_build(self):
        return self.can_build_on

    def is_liquid(self):
        return self.type == BiomeType.LIQUID

    def is_land(self):
        return self.type == BiomeType.LAND
