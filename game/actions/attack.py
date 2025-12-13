from dataclasses import dataclass
from configs.base_config import BaseConfig


@dataclass
class Attack(BaseConfig):
    value: float = 1.0
    armor_piercing: float = 1.0
    is_incendiary: bool = False
    incendiary_time: float = 0.0
    incendiary_damage: float = 0.0
