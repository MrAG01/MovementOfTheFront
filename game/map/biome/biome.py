from configs.base_config import BaseConfig
from game.map.biome.biome_type import BiomeType


class Biome(BaseConfig):
    def __init__(self, can_build_on, build_cost_multiplayer, build_time_multiplayer, unit_speed_multiplayer, type):
        self.can_build_on = can_build_on
        self.build_cost_multiplayer = build_cost_multiplayer
        self.build_time_multiplayer = build_time_multiplayer
        self.unit_speed_multiplayer = unit_speed_multiplayer

        self.type: BiomeType = type

    @classmethod
    def from_dict(cls, data):
        return cls(can_build_on=data["can_build_on"],
                   build_cost_multiplayer=data["build_cost_multiplayer"],
                   build_time_multiplayer=data["build_time_multiplayer"],
                   unit_speed_multiplayer=data["unit_speed_multiplayer"],
                   type=BiomeType(data["type"]))

    def serialize(self):
        return {
            "type": self.type.value,
            "can_build_on": self.can_build_on,
            "build_cost_multiplayer": self.build_cost_multiplayer,
            "unit_speed_multiplayer": self.unit_speed_multiplayer,
            "build_time_multiplayer": self.build_time_multiplayer
        }

    def can_build(self):
        return self.can_build_on

    def is_liquid(self):
        return self.type == BiomeType.LIQUID

    def is_land(self):
        return self.type == BiomeType.LAND

    def get_speed_k(self):
        return self.unit_speed_multiplayer
