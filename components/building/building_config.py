from dataclasses import dataclass
from components.bullets.base_bullet import BaseBullet


@dataclass
class BuildingConfig:
    name: str
    cost: dict[str, int]
    description: str = ""
    build_time: float = 1.0
    max_level: int = 1
    next_worker_cost_multiplier: float = 1.0
    next_building_cost_multiplier: float = 1.0
    max_cost: dict[str, int] = None
    requirements_buildings: list[str] = None
    requirements_technologies: list[str] = None
    max_health: float = 100.0
    regeneration: float = 1.0
    conducts_roads: bool = False
    size: tuple[int, int] = (50, 50)

    # Производство (опционально)
    production: dict[str, int] = None
    consumption: dict[str, int] = None
    workers_slots: int = 5
    production_speed: float = 1.0

    # Оборона (опционально)
    reload_time: float = 1.0
    attack_radius: float = 100.0
    turret_rotate_speed: float = 5.0
    bullet: BaseBullet = None
    can_target_projectiles = False
    can_target_air = False
    can_target_ground = True
    can_target_water = True
    can_target_buildings = True

    base_texture_name: str = None
    texture_name: str = None
    turret_texture_name: str = None
    building_animation_name: str = None

    building_sound_name: str = None
    working_sound_name: str = None
