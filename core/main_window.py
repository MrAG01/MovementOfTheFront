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
    def __init__(self, resource_manager, mods_manager, game_manager, config_manager: ConfigManager):

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

        # self.show_view(MainMenuView(self.show_view, game_manager, self.resource_manager))
        self.camera = Camera(config_manager, self.keyboard_manager, self.mouse_manager, screen_width, screen_height)
        biomes_ratio = {
            "ocean": {"height": [0.0, 0.5], "moisture": None},
            "beach": {"height": [0.5, 0.52], "moisture": None},
            "plain": {"height": [0.52, 0.6], "moisture": None},
            "forest": {"height": [0.6, 0.7], "moisture": None},
            "rocky": {"height": [0.7, 0.73], "moisture": None},
            "mountains": {"height": [0.73, 0.85], "moisture": None},
            "snow": {"height": [0.85, 1.0], "moisture": None}
        }

        map_generator = MapGenerator(MapGenerationSettings(biomes_ratio), self.resource_manager, self.mods_manager)
        self.map = map_generator.generate()

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

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.map.draw()

    def on_update(self, delta_time: float):
        self.keyboard_manager.update()
        self.camera.update(delta_time)
