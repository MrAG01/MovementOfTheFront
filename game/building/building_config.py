from dataclasses import dataclass
from components.items import Items
from configs.base_config import BaseConfig


@dataclass
class BuildingConfig(BaseConfig):
    cost: Items
    build_time: float = 1.0
    max_level: int = 1
    upgrades_cost: list[dict[str, int]] = None
    next_building_cost_multiplier: float = 1.0
    max_cost: dict[str, int] = None
    requirements_buildings: list[str] = None
    requirements_technologies: list[str] = None
    max_health: float = 100.0
    regeneration: float = 1.0
    conducts_roads: bool = False
    size: tuple[int, int] = (64, 64)

    # Производство (опционально)
    production: list[dict] = None
    consumption: dict[str, int] = None
    production_speed: float = 1.0

    # Оборона (опционально)
    reload_time: float = 1.0
    attack_radius: float = 50.0
    attack_type: str = None

    defence_radius: float = 100.0
    defence_power: float = 5.0

    can_target_air = False
    can_target_ground = True
    can_target_water = True
    can_target_buildings = True

    # Текстуры
    texture_name: str = None
