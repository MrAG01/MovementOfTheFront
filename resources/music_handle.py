from resources.resource_handle import ResourceHandle
import arcade


class MusicHandle(ResourceHandle):
    def _load(self):
        self.resource = arcade.load_sound(self.path, streaming=True)
        self._loaded = True
