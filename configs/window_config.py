from dataclasses import dataclass
from utils.constants import ICON_PATH

@dataclass
class WindowConfig:
    fullscreen: bool = True
    resizable: bool = False
    auto_window_size: bool = True
    window_width: int = 1920
    window_height: int = 1080
    window_title: str = "Movement of the front"
    window_icon_path: str = ICON_PATH

    vsync: bool = True
    # если 0 -> нет ограничения
    fps_limit: int = 0

    @classmethod
    def get_default(cls):
        return cls()

    @property
    def resolution(self):
        return self.window_width, self.window_height

    def set_fps(self, new_fps):
        if new_fps != 0:
            self.vsync = False
        self.fps_limit = new_fps

    def set_vsync(self, vsync):
        self.vsync = vsync

    def set_fullscreen(self, fullscreen):
        self.fullscreen = fullscreen