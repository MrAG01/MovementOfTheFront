from dataclasses import dataclass
from components.items import Items
from configs.base_config import BaseConfig
from game.building.consumption.consumption_rule import ConsumptionRule
from game.building.production.production_rule import ProductionRule
from resources.handlers.texture_handle import TextureHandle


@dataclass
class BuildingConfig(BaseConfig):
    name: str

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

    can_place_on_deposit: bool = False
    can_place_not_on_deposit: bool = True

    # Производство (опционально)
    production: list[ProductionRule] = None
    consumption: ConsumptionRule = None

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
    outline_texture_name: str = None

    @classmethod
    def from_dict(cls, data):
        data["cost"] = Items.from_dict(data["cost"])
        if "production" in data:
            data["production"] = [ProductionRule.from_dict(rule) for rule in data["production"]]
        if "consumption" in data:
            data["consumption"] = ConsumptionRule.from_dict(data["consumption"])
        return cls(**data)
