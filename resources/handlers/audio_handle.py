from resources.handlers.resource_handle import ResourceHandle
import arcade


class AudioHandle(ResourceHandle):
    audio_cache = {}

    @classmethod
    def clear_cache(cls):
        cls.audio_cache.clear()

    def _load(self):
        if self.path in self.audio_cache:
            self.resource = self.audio_cache[self.path]
        else:
            self.resource = arcade.load_sound(self.path)
            self.audio_cache[self.path] = self.resource
        self._loaded = True
