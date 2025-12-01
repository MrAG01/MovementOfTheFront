from dataclasses import dataclass


@dataclass
class BuildingConfig:
    name: str
    description: str
    cost: dict[str, int]
    build_time: float
    max_level: int
    next_worker_cost_multiplier: float
    next_building_cost_multiplier: float
    max_cost: dict[str, int]
    requirements_buildings: list[str]
    requirements_technologies: list[str]
    max_health: float
    regeneration: float
    conducts_roads: bool
    size: tuple[int, int]

    # Производство (опционально)
    production: dict[str, int]
    consumption: dict[str, int]
    workers_slots: int
    production_speed: float

    # Оборона (опционально)


    base_texture_name: str
    texture_name: str
    building_animation_name: str

    building_sound_name: str
    working_sound_name: str
