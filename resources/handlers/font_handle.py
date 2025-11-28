from resources.handlers.resource_handle import ResourceHandle
import arcade


class FontHandle(ResourceHandle):
    def _load(self):
        self.resource = arcade.load_font(self.path)
        self._loaded = True
