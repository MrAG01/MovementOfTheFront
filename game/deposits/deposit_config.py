from dataclasses import dataclass
from components.items import Items
from configs.base_config import BaseConfig


@dataclass
class DepositConfig(BaseConfig):
    name: str
    product_buildings: dict[str, dict[str, float, str, Items]]
    required_biomes: list[str]

    min_capacity: int
    max_capacity: int

    @classmethod
    def from_dict(cls, data):
        for building_name in data["product_buildings"]:
            production = Items.from_dict(data["product_buildings"][building_name]["production"])
            data["product_buildings"][building_name]["production"] = production
        return cls(**data)
