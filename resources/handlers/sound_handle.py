from resources.handlers.resource_handle import ResourceHandle
import arcade


class SoundHandle(ResourceHandle):
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

    def play(self, volume: float = 1.0,
             pan: float = 0.0,
             loop: bool = False,
             speed: float = 1.0, ):
        resource: arcade.Sound = self.get()
        resource.play(volume, pan, loop, speed)
