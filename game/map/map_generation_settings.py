from configs.base_config import BaseConfig
import random

DEFAULT_BIOMES_RATIO = {
    "ocean": {"height": [0.0, 0.5], "moisture": None},
    "beach": {"height": [0.5, 0.52], "moisture": None},
    "plain": {"height": [0.52, 0.6], "moisture": None},
    "forest": {"height": [0.6, 0.7], "moisture": None},
    "rocky": {"height": [0.7, 0.73], "moisture": None},
    "mountains": {"height": [0.73, 0.85], "moisture": None},
    "snow": {"height": [0.85, 1.0], "moisture": None}
}


class MapGenerationSettings(BaseConfig):
    def __init__(self, seed, biomes_ratio: dict[str, dict] = DEFAULT_BIOMES_RATIO, deposits_chance: dict[str, float] = {},
                 width=800, height=800, scale=2, octaves=6, persistence=0.5,
                 lacunarity=2.0):
        self.biomes_ratio = biomes_ratio
        self.deposits_chance = deposits_chance
        self.width = width
        self.height = height
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.seed = seed
