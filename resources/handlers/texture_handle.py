from resources.handlers.resource_handle import ResourceHandle
import arcade


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
