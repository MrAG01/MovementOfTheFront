import arcade

from configs.window_config import WindowConfig


class MainWindow(arcade.Window):
    def __init__(self, window_config):
        self.window_config: WindowConfig = window_config
        screen_width, screen_height = self.window_config.resolution
        super().__init__(screen_width,
                         screen_height,
                         self.window_config.window_title,
                         self.window_config.fullscreen,
                         self.window_config.resizable,
                         vsync=self.window_config.vsync)
