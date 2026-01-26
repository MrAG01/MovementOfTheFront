import base64
import time
import zlib
from PIL import Image, ImageFilter
import numpy
import numpy as np
import arcade
from arcade import SpriteList

from game.deposits.client_deposit import ClientDeposit
from game.vitual_border import VirtualBorder
from utils.space_hash_map import SpaceHashMap


class ClientMap:
    def __init__(self, resource_manager, mods_manager, map_data):
        self.biome_names: dict[int, str] = {int(k): v for k, v in map_data["biome_names"].items()}
        self.mods_manager = mods_manager
        self.biomes_map: numpy.array = ClientMap.decode_array(map_data["biomes_map"])
        self.deposits = {int(deposit_id): ClientDeposit(resource_manager, mods_manager, deposit_data) for
                         deposit_id, deposit_data in
                         map_data["deposits"].items()}

        self.resource_manager = resource_manager
        self.biomes_colors: dict[str, tuple[int, int, int]] = self.resource_manager.get_biomes_colors()
        self.color_map: arcade.Texture = self.generate_color_map(self.biomes_map)

        self.deposits_sprite_list = None

        self.width, self.height = self.get_size()
        self.deposits_space_map: SpaceHashMap = SpaceHashMap(self.deposits.values(), max(self.width // 5, 50),
                                                             max(self.height // 5, 50))

        self.virtual_borders = VirtualBorder(*self.get_size())

    def setup_deposits(self):
        self.deposits_sprite_list = SpriteList(use_spatial_hash=True)
        for deposit in self.deposits.values():
            self.deposits_sprite_list.append(deposit)

    def get_virtual_borders(self):
        return self.virtual_borders

    def get_biome(self, x, y):
        biome_name = self.biome_names[self.biomes_map[self.height - int(y)][int(x)]]
        biome = self.mods_manager.get_biome(biome_name)
        return biome

    def get_deposits_close_to(self, x, y):
        return self.deposits_space_map.get_at(x, y)

    def update_from_snapshot(self, snapshot):
        deposits_data = snapshot["deposits"]
        for deposit_id, deposit_data in deposits_data.items():
            deposit_id_int = int(deposit_id)
            if deposit_id_int in self.deposits:
                self.deposits[deposit_id_int].update_from_snapshot(deposits_data[deposit_id])

    def get_size(self):
        return self.color_map.size

    def _get_biome_color_by_name(self, name):
        r, g, b = self.biomes_colors.get(name, (0, 0, 0))
        return r, g, b, 255

    def _get_biome_color_by_id(self, biome_id):
        return self._get_biome_color_by_name(self.biome_names[int(biome_id)])

    def generate_color_map(self, biomes_map):
        height, width = biomes_map.shape
        color_array = np.zeros((height, width, 4), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                color_array[y, x] = self._get_biome_color_by_id(biomes_map[y, x])
        pil_image = Image.fromarray(color_array, "RGBA")

        return arcade.Texture(pil_image.filter(ImageFilter.GaussianBlur(radius=0.5)))

    @staticmethod
    def decode_array(map_data):
        if map_data is None:
            return None
        try:
            width = map_data["width"]
            height = map_data["height"]
            array_data = zlib.decompress(base64.b64decode(map_data["data"]))
            data_type = np.dtype(map_data.get("data_type", "int32"))
            print(f"DECODED MAP: {width}x{height}, ARRAY DATA LENGTH - {len(array_data)}, WITH TYPE {data_type}")
            return np.frombuffer(array_data, dtype=data_type).reshape(height, width)
        except Exception as e:
            print(e)
            return None

    def draw(self, camera):
        w, h = self.color_map.size
        arcade.draw_texture_rect(self.color_map, arcade.rect.LBWH(0, 0, w, h),
                                 pixelated=True)
        if not self.deposits_sprite_list:
            self.setup_deposits()
        self.deposits_sprite_list.draw(pixelated=True)
