from dataclasses import dataclass

from components.item import Item
from configs.base_config import BaseConfig


@dataclass
class DepositConfig(BaseConfig):
    product_buildings: dict[str, list[Item]]