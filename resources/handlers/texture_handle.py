from resources.handlers.resource_handle import ResourceHandle
import arcade

from utils.os_utils import get_file_info


class TextureHandle(ResourceHandle):
    textures_cache = {}

    @classmethod
    def clear_cache(cls):
        cls.textures_cache.clear()

    def _load(self):
        if self.path in self.textures_cache:
            self.resource = self.textures_cache[self.path]
        else:
            self.resource = arcade.load_texture(self.path)
            self.textures_cache[self.path] = self.resource
        self._loaded = True

    def get_size(self):
        texture = self.get()
        if texture:
            return texture.width, texture.height
        return 0, 0

    def draw(self, x, y, scale_x=1, scale_y=1, alpha=255, pixelated=True, color=arcade.color.WHITE):
        texture = self.get()
        if texture is None:
            return
        arcade.draw_texture_rect(
            texture,
            arcade.XYWH(x, y, texture.width * scale_x, texture.height * scale_y),
            alpha=alpha,
            pixelated=pixelated,
            color=color
        )

    def __repr__(self):
        name, ext, path = get_file_info(self.path)
        return f"TextureHandle({name}{ext})"
