from dataclasses import dataclass

from components.items import Items
from configs.base_config import BaseConfig


@dataclass
class UnitConfig(BaseConfig):
    name: str

    cost: Items
    build_time: float = 1.0

    max_health: float = 100
    regeneration: float = 0.2

    texture_radius: float = 10
    hit_box_radius: float = 20

    units_damage: float = 1
    push_power: float = 0.05

    @classmethod
    def from_dict(cls, data):
        data["cost"] = Items.from_dict(data["cost"])
        return cls(**data)
