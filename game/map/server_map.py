import arcade
from game.map.biome.biome import Biome
import numpy as np


class ServerMap:
    def __init__(self, height_map: np.array, moisture_map: np.array = None, color_map: arcade.Texture = None):
        self.height_map: np.array = height_map
        self.moisture_map: np.array = moisture_map
        self.color_map: arcade.Texture = color_map
        self.scale_factor = 10

        self.biomes_colors_keys: dict[tuple[int, int, int, int], Biome] = {}

    def get_biome_at(self, x, y):
        color = self.color_map.image_data.image.getpixel((x, y))
        return self.biomes_colors_keys.get(color)

    def draw(self):
        arcade.draw_texture_rect(self.color_map, arcade.rect.XYWH(0, 0, self.color_map.width * self.scale_factor,
                                                                   self.color_map.height * self.scale_factor))
