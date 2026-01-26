from arcade import Sound

from resources.handlers.resource_handle import ResourceHandle
import arcade


class MusicHandle(ResourceHandle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._player = None

    def _load(self):
        self.resource: Sound = arcade.load_sound(self.path, streaming=True)
        self._loaded = True

    def play(self, volume: float = 1.0,
             pan: float = 0.0,
             loop: bool = False,
             speed: float = 1.0):
        resource = super().get()
        self._player = resource.play(volume, pan, loop, speed)

    def set_volume(self, volume):
        if self._player:
            self.resource.set_volume(volume, self._player)
