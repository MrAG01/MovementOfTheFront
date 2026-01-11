from dataclasses import dataclass
from components.items import Items
from configs.base_config import BaseConfig


@dataclass
class ConsumptionRule(BaseConfig):
    time: float
    production: Items

    @classmethod
    def from_dict(cls, data):
        return cls(
            time=data["time"],
            production=Items.from_dict(data["production"])
        )