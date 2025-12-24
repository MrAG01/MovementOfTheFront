import arcade
import noise
import numpy as np
from PIL import Image

from game.map.biome.biome import Biome
from game.map.map_generation_settings import MapGenerationSettings
from game.map.server_map import ServerMap

#TODO: Генерацию deposits
class MapGenerator:
    def __init__(self, map_generation_settings, resource_manager, mods_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.settings: MapGenerationSettings = map_generation_settings
        self.biomes_colors: dict[str, tuple[int, int, int]] = self.resource_manager.get_biomes_colors()

    def _get_biome_color_by_name(self, name):
        r, g, b = self.biomes_colors.get(name, (0, 0, 0))
        return r, g, b, 255

    def get_biome_color(self, height, moisture):
        for biome_name, rules in self.settings.biomes_ratio.items():
            h_min, h_max = rules["height"]
            if not (h_min <= height <= h_max):
                continue

            m_range = rules.get("moisture")
            if m_range is None:
                return self._get_biome_color_by_name(biome_name)
            m_min, m_max = m_range
            if m_min <= moisture <= m_max:
                return self._get_biome_color_by_name(biome_name)
        available_biomes_names = list(self.biomes_colors.keys())
        if available_biomes_names:
            return self._get_biome_color_by_name(available_biomes_names[-1])
        else:
            return (0, 0, 0, 255)

    def _array_to_texture(self, array):
        return arcade.Texture(Image.fromarray(array, mode='RGBA'))

    def _generate_moisture_map(self):
        width, height = self.settings.width, self.settings.height
        map_raw = np.zeros((height, width))
        scale = self.settings.scale + 5
        octaves = 6
        persistence = 0.5
        lacunarity = 2
        seed = self.settings.seed

        for y in range(height):
            for x in range(width):
                nx = x / width - 0.5
                ny = y / height - 0.5

                value = noise.pnoise2(
                    nx * scale,
                    ny * scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=1024,
                    repeaty=1024,
                    base=seed % 128
                )
                map_raw[y][x] = int((value + 1) / 2 * 256)
        return map_raw

    def _generate_map(self, seed_offset=0):
        width, height = self.settings.width, self.settings.height
        map_raw = np.zeros((height, width))
        scale = self.settings.scale
        octaves = self.settings.octaves
        persistence = self.settings.persistence
        lacunarity = self.settings.lacunarity
        seed = self.settings.seed + seed_offset
        for y in range(height):
            for x in range(width):
                nx = x / width - 0.5
                ny = y / height - 0.5

                value = noise.pnoise2(
                    nx * scale,
                    ny * scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=1024,
                    repeaty=1024,
                    base=seed % 128
                )
                normalized = (value + 1) / 2

                stretched = ((normalized * 2) ** 2) / 2
                stretched = max(0.0, min(1.0, stretched))
                map_raw[y][x] =  int(stretched * 255)
        return map_raw

    def _generate_texture_map(self, height_map_array: np.array, moisture_map_array: np.array):
        width, height = self.settings.width, self.settings.height
        texture_map = np.zeros((width, height, 4), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                value = height_map_array[y][x] / 256.0
                moisture = moisture_map_array[y][x] / 256.0
                color = self.get_biome_color(value, moisture)
                texture_map[y][x] = color
        return self._array_to_texture(texture_map)

    def generate(self):
        height_map = self._generate_map()
        moisture_map = self._generate_moisture_map()
        color_map_texture = self._generate_texture_map(height_map, moisture_map)

        return ServerMap(height_map=height_map, moisture_map=moisture_map, color_map=color_map_texture)
