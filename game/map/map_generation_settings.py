from configs.base_config import BaseConfig
import random


class MapGenerationSettings(BaseConfig):
    def get_biome(self, height, moisture):
        if height < 0.5:
            return "ocean"
        elif height < 0.51:
            return "beach"
        elif height < 0.6:
            if moisture > 0.5:
                return "forest"
            elif moisture > 0.4:
                return "plain"
            else:
                return "beach"
        elif height < 0.62:
            return "rocky"
        elif height < 0.65:
            return "mountains"
        else:
            return "snow"

    def __init__(self, biomes_ratio: dict[str, dict],
                 width=800, height=800, scale=2, octaves=6, persistence=0.5,
                 lacunarity=2.0, seed=52):
        self.biomes_ratio = biomes_ratio
        self.width = width
        self.height = height
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.seed = random.randint(0, 1000)
