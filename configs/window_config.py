import arcade

from configs.base_config import BaseConfig
from configs.notification_mixin import NotificationMixin
from utils.constants import ICON_PATH


class WindowConfig(BaseConfig, NotificationMixin):
    def __init__(self):
        super().__init__()
        self.fullscreen: bool = False
        self.resizable: bool = False
        self._auto_window_size: bool = False
        self._window_width: int = 1920 // 2
        self._window_height: int = 1080 // 2
        self.window_title: str = "Movement of the front"
        self.window_icon_path: str = ICON_PATH

        self.vsync: bool = True
        self.fps_limit: int = 0
        self._cached_display_size: tuple = arcade.get_display_size()

    @classmethod
    def from_dict(cls, data):
        config = cls.get_default()
        config.fullscreen = data["fullscreen"]
        config.resizable = data["resizable"]
        config.set_auto_window_resize(data["auto_window_resize"])
        config.set_width(data["window_width"])
        config.set_height(data["window_height"])
        config.window_title = data["window_title"]
        config.vsync = data["vsync"]
        config.fps_limit = data["fps_limit"]
        return config

    def serialize(self):
        return {
            "fullscreen": self.fullscreen,
            "resizable": self.resizable,
            "auto_window_resize": self._auto_window_size,
            "window_width": self._window_width,
            "window_height": self._window_height,
            "window_title": self.window_title,
            "vsync": self.vsync,
            "fps_limit": self.fps_limit,
        }

    @property
    def resolution(self):
        return self.window_width, self.window_height

    @property
    def window_width(self):
        if self._auto_window_size or self.fullscreen:
            return self._cached_display_size[0]
        else:
            return self._window_width

    @property
    def window_height(self):
        if self._auto_window_size or self.fullscreen:
            return self._cached_display_size[1]
        else:
            return self._window_height

    def set_fps(self, new_fps):
        if new_fps != 0:
            self.vsync = False
        self.fps_limit = new_fps
        self.notify_listeners()

    def set_width(self, width):
        self._window_width = width
        self.notify_listeners()

    def set_height(self, height):
        self._window_height = height
        self.notify_listeners()

    def set_resolution(self, width, height):
        self._window_width = width
        self._window_height = height
        self.notify_listeners()

    def set_auto_window_resize(self, arg):
        self._auto_window_size = arg
        self.notify_listeners()
