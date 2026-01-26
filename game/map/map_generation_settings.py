from configs.base_config import BaseConfig

DEFAULT_BIOMES_RATIO = {
    "ocean": {"height": [0.0, 0.5], "moisture": None},
    "beach": {"height": [0.5, 0.52], "moisture": None},
    "plain": {"height": [0.52, 0.6], "moisture": None},
    "forest": {"height": [0.6, 0.7], "moisture": None},
    "rocky": {"height": [0.7, 0.8], "moisture": None},
    "mountains": {"height": [0.8, 0.85], "moisture": None},
    "snow": {"height": [0.85, 1.0], "moisture": None}
}

DEFAULT_DEPOSITS_NUMBERS = {
    "forest": 60,
    "gold_deposit": 15,
    "iron_deposit": 15,
    "stone_deposit": 20,
    "fertile_soil": 50,
    "pasture": 30
}


class MapGenerationSettings(BaseConfig):
    def __init__(self, seed, biomes_ratio: dict[str, dict] = DEFAULT_BIOMES_RATIO,
                 deposits_numbers: dict[str, float] = DEFAULT_DEPOSITS_NUMBERS,
                 width=800, height=800, scale=3, octaves=6, persistence=0.5,
                 lacunarity=2.0):



        self.biomes_ratio = biomes_ratio
        self.deposits_numbers = deposits_numbers
        self.width = width
        self.height = height

        max_side = max(width, height)

        self.scale = max_side / 800 * scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.seed = seed
