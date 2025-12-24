import base64
from PIL import Image
import arcade

from game.map.biome.biome import Biome


class ClientMap:
    def __init__(self, map_data):
        self.color_map: arcade.Texture = ClientMap.decode_image(map_data["color_map"])
        self.biome_colors_keys = ClientMap.decode_biomes_color_key(map_data["biome_colors_keys"])

        min_size = min(self.color_map.size)
        self.size_k = (1080 / min_size) / 3

    def draw(self):
        w, h = self.color_map.size
        arcade.draw_texture_rect(self.color_map, arcade.rect.XYWH(0, 0, w * self.size_k, h * self.size_k),
                                 pixelated=True)

    def get_biome_at(self, x, y):
        color = self.color_map.image_data.image.getpixel((x, y))
        return self.biomes_colors_keys.get(color)

    @staticmethod
    def decode_biomes_color_key(raw_data):
        for key, raw_biome in raw_data.items():
            raw_data[key] = Biome.from_dict(raw_biome)
        return raw_data

    @staticmethod
    def decode_image(img_str_encoded: str):
        img_raw_bytes = base64.b64decode(img_str_encoded.encode('utf-8'))
        pil_image = Image.open(img_raw_bytes)
        return arcade.Texture(pil_image)
