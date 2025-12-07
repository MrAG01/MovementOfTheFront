import arcade

from components.building.base_building import Building
from components.building.building_config import BuildingConfig
from configs.config_manager import ConfigManager
from configs.window_config import WindowConfig
from coordinators.game_coordinator import GameCoordinator
from coordinators.menu_coordinator import MenuCoordinator
from scenes.scene_manager import SceneManager


class MainWindow(arcade.Window):
    def __init__(self, resource_manager, config_manager: ConfigManager):
        self.resource_manager = resource_manager
        config_manager.add_listener(self._on_config_changed_callback, WindowConfig)
        self.window_config: WindowConfig = config_manager.get_window_config()

        screen_width, screen_height = self.window_config.resolution
        super().__init__(width=screen_width,
                         height=screen_height,
                         title=self.window_config.window_title,
                         fullscreen=self.window_config.fullscreen,
                         resizable=self.window_config.resizable,
                         vsync=self.window_config.vsync)
        self._set_fps(self.window_config.fps_limit)

        self.scene_manager = SceneManager()
        self.game_coordinator = GameCoordinator(self.scene_manager)
        self.menu_coordinator = MenuCoordinator(self.scene_manager, self.game_coordinator)

        self.bc = BuildingConfig("LH", {})
        self.bc.building_animation_name = "lumberjack_hut_building"
        self.bc.base_texture_name = "lumberjack_hut_base"
        self.building = Building(self.resource_manager, self.bc)

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

    def _on_config_changed_callback(self, config_manager: ConfigManager):
        self.window_config = config_manager.get_window_config()
        self._sync_values_with_config()

    def on_update(self, delta_time: float):
        self.scene_manager.on_update(delta_time, self)
        self.menu_coordinator.update(delta_time, self)
        self.game_coordinator.update(delta_time, self)
        self.building.update(delta_time)

    def on_draw(self):
        self.clear()
        self.scene_manager.draw(self)
        self.building.draw()

    def on_shutdown(self):
        self.scene_manager.on_shutdown()
