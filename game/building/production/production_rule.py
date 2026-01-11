from dataclasses import dataclass

from components.items import Items
from configs.base_config import BaseConfig


@dataclass
class ProductionRule(BaseConfig):
    time: float
    input: Items
    output: Items

    @classmethod
    def from_dict(cls, data):
        return cls(
            time=data["time"],
            input=Items.from_dict(data["input"]),
            output=Items.from_dict(data["output"])
        )