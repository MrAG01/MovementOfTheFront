import arcade
from configs.config_manager import ConfigManager
from configs.window_config import WindowConfig
from resources.input.keyboard_manager import KeyboardManager
from game.camera import Camera
from resources.input.mouse_manager import MouseManager


class MainWindow(arcade.Window):
    def __init__(self, resource_manager, config_manager: ConfigManager):

        self.resource_manager = resource_manager
        self.window_config = config_manager.register_config("window_config", WindowConfig)
        self.window_config.add_listener(self._on_window_config_changed_callback,
                                        notify_immediately=False)

        screen_width, screen_height = self.window_config.resolution
        super().__init__(width=screen_width,
                         height=screen_height,
                         title=self.window_config.window_title,
                         fullscreen=self.window_config.fullscreen,
                         resizable=self.window_config.resizable,
                         vsync=self.window_config.vsync)
        self.keyboard_manager = KeyboardManager(config_manager)
        self.mouse_manager = MouseManager()
        self._set_fps(self.window_config.fps_limit)

        self.test_camera = Camera(config_manager, self.keyboard_manager, self.mouse_manager, screen_width,
                                  screen_height)

    def _set_fps(self, new_fps):
        if new_fps > 0:
            interval = 1.0 / new_fps
            self.set_draw_rate(interval)
            self.set_update_rate(interval)
        else:
            self.set_draw_rate(1)
            self.set_update_rate(1)

    def _sync_values_with_config(self):
        self.set_caption(self.window_config.window_title)
        self.set_vsync(self.window_config.vsync)
        self.set_fullscreen(self.window_config.fullscreen)

        self._set_fps(self.window_config.fps_limit)
        width, height = self.window_config.resolution
        self.set_size(width, height)

    def _on_window_config_changed_callback(self, window_config: WindowConfig):
        self._sync_values_with_config()

    def on_update(self, delta_time: float):
        self.keyboard_manager.update()
        self.test_camera.update(delta_time)

    def on_draw(self):
        self.clear()
        self.test_camera.use()
        arcade.draw_circle_filled(100, 100, 50, arcade.color.Color(255, 0, 0))
