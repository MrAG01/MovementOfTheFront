import arcade
from pyglet.event import EVENT_HANDLE_STATE

from configs.config_manager import ConfigManager
from configs.window_config import WindowConfig
from game.camera import Camera
from game.map.map_generation_settings import MapGenerationSettings
from game.map.map_generator import MapGenerator
from game.map.server_map import ServerMap
from resources.input.keyboard_manager import KeyboardManager
from resources.input.mouse_manager import MouseManager
from scenes.main_menu_view import MainMenuView


class MainWindow(arcade.Window):
    def __init__(self, resource_manager, mods_manager, game_manager, config_manager: ConfigManager,
                 server_logger_manager):

        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
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

        self.show_view(
            MainMenuView(self.show_view, game_manager, self.resource_manager, self.mods_manager, server_logger_manager,
                         config_manager, self.keyboard_manager, self.mouse_manager))

    def _set_fps(self, new_fps):
        if new_fps > 0:
            interval = 1.0 / new_fps
            self.set_draw_rate(interval)
            self.set_update_rate(interval)
        else:
            self.set_draw_rate(1)
            self.set_update_rate(1)

    def on_resize(self, width: int, height: int):
        self.window_config.set_resolution(width, height)

    def _sync_values_with_config(self):
        self.set_caption(self.window_config.window_title)
        self.set_vsync(self.window_config.vsync)
        self.set_fullscreen(self.window_config.fullscreen)

        self._set_fps(self.window_config.fps_limit)

        width, height = self.window_config.resolution
        if (width, height) != (self.width, self.height):
            self.set_size(width, height)

    def _on_window_config_changed_callback(self, window_config: WindowConfig):
        self._sync_values_with_config()

    def on_update(self, delta_time: float):
        super().on_update(delta_time)
        self.keyboard_manager.update()
