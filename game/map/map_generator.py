import noise
import numpy as np
from game.map.map_generation_settings import MapGenerationSettings
from game.map.server_map import ServerMap


class MapGenerator:
    def __init__(self, map_generation_settings, resource_manager, mods_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.settings: MapGenerationSettings = map_generation_settings
        self.biome_ids = {}
        for i, biome_name in enumerate(self.settings.biomes_ratio):
            self.biome_ids[biome_name] = i

    def get_biome_id(self, height, moisture):
        height = height / 255.0
        for biome_name, rules in self.settings.biomes_ratio.items():
            h_min, h_max = rules["height"]
            if not (h_min <= height <= h_max):
                continue

            m_range = rules.get("moisture")
            if m_range is None:
                return self.biome_ids[biome_name]
            m_min, m_max = m_range
            if m_min <= moisture <= m_max:
                return self.biome_ids[biome_name]
        available_biomes_names = list(self.biome_ids.keys())
        if available_biomes_names:
            return self.biome_ids[available_biomes_names[-1]]
        else:
            return 0

    def _get_height(self, x, y):
        nx = x / self.settings.width - 0.5
        ny = y / self.settings.height - 0.5

        value = noise.pnoise2(
            nx * self.settings.scale,
            ny * self.settings.scale,
            octaves=self.settings.octaves,
            persistence=self.settings.persistence,
            lacunarity=self.settings.lacunarity,
            repeatx=1024,
            repeaty=1024,
            base=self.settings.seed % 128
        )
        normalized = (value + 1) / 2

        stretched = ((normalized * 2) ** 2) / 2
        stretched = max(0.0, min(1.0, stretched))
        return int(stretched * 255)

    def _get_moisture(self, x, y):
        scale = self.settings.scale + 5
        nx = x / self.settings.width - 0.5
        ny = y / self.settings.height - 0.5

        value = noise.pnoise2(
            nx * scale,
            ny * scale,
            octaves=6,
            persistence=0.5,
            lacunarity=2,
            repeatx=1024,
            repeaty=1024,
            base=self.settings.seed % 128
        )
        return int((value + 1) / 2 * 256)

    def _generate_map(self):
        width, height = self.settings.width, self.settings.height
        biomes_map = np.zeros((width, height), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                value = self._get_height(x, y)
                moisture = self._get_moisture(x, y)
                biomes_map[y][x] = self.get_biome_id(value, moisture)
        return biomes_map

    def generate(self):
        biomes_map = self._generate_map()
        return ServerMap(mods_manager=self.mods_manager, biomes_map=biomes_map,
                         biome_names={v: k for k, v in self.biome_ids.items()})
