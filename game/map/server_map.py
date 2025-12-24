import base64
import io

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

    @staticmethod
    def serialize_biomes_colors_keys(biomes_color_keys):
        serialized = {}
        for key, biome in biomes_color_keys.items():
            serialized[key] = biome.serialize()
        return serialized

    @staticmethod
    def serialize_map(color_map: arcade.Texture):
        pil_img = color_map.image_data.image
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return base64.b64decode(img_bytes.read()).decode('utf-8')

    def serialize(self):
        return {
            "biomes_colors_keys": ServerMap.serialize_biomes_colors_keys(self.biomes_colors_keys),
            "color_map": ServerMap.serialize_map(self.color_map)
        }

    def get_biome_at(self, x, y):
        color = self.color_map.image_data.image.getpixel((x, y))
        return self.biomes_colors_keys.get(color)

    def draw(self):
        arcade.draw_texture_rect(self.color_map, arcade.rect.XYWH(0, 0, self.color_map.width * self.scale_factor,
                                                                  self.color_map.height * self.scale_factor))
