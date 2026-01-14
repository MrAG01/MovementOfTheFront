import arcade.color
from GUI.ui_progress_bar import UIProgressBar
from game.actions.events import Event, BuildingEvents
from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from game.camera import Camera
from resources.handlers.texture_handle import TextureHandle
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from resources.mods.mods_manager.mods_manager import ModsManager
from arcade.math import lerp
from arcade import Vec2


class ClientBuilding:
    interpolation_speed = 1.0

    def __init__(self, server_snapshot: dict, resource_manager, mods_manager):
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager: ModsManager = mods_manager
        self.id = server_snapshot["id"]
        self.owner_id = server_snapshot["owner_id"]
        self.position = Vec2(*server_snapshot["position"])
        self._target_health = self.health = server_snapshot["health"]
        self.level = server_snapshot["level"]

        self.config: BuildingConfig = self.mods_manager.get_building(server_snapshot["config_name"])

        self.state = BuildingState(server_snapshot["state"])
        self.building_progress = server_snapshot["building_progress"]

        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.name)
        self.outline_texture: TextureHandle = self.resource_manager.get_texture(self.config.outline_texture_name)

        self.selected = False
        self.outline_enabled = False

        x, y = self.position
        w, h = self.texture.get_size()

        self.progress_bar_slider = UIProgressBar(
            x=x,
            y=y + h,
            width=w,
            height=10,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(200, 200, 50),
            border_color=arcade.color.Color(0, 0, 0)
        )
        self.progress_bar_active = False
        self.progress_bar_slider_state = 0
        self.progress_bar_slider_max = 0

        self._apply_events([Event.from_dict(event_data) for event_data in server_snapshot["events"]])

    def enable_selection(self):
        self.selected = True

    def disable_selection(self):
        self.selected = False

    def enable_outline(self):
        if not self.selected:
            self.outline_enabled = True

    def disable_outline(self):
        self.outline_enabled = False

    def update_from_snapshot(self, snapshot):
        self.owner_id = snapshot["owner_id"]
        self._target_health = snapshot["health"]
        self.state = BuildingState(snapshot["state"])
        self.level = snapshot["level"]
        self.building_progress = snapshot["building_progress"]
        self._apply_events([Event.from_dict(event_data) for event_data in snapshot["events"]])

    def update_visual(self, delta_time):
        if self.health != self._target_health:
            self.health = lerp(self.health, self._target_health, min(self.interpolation_speed * delta_time, 1.0))

        if self.progress_bar_active:
            self.progress_bar_slider_state += delta_time
            if self.progress_bar_slider_max <= self.progress_bar_slider_state:
                self.progress_bar_slider_state = 0
                self.progress_bar_active = False
            self.progress_bar_slider.set_state(self.progress_bar_slider_state)

    def _apply_events(self, events: list[Event]):
        for event in events:
            if event.event_type == BuildingEvents.PRODUCTION_STARTED.value:
                self.progress_bar_active = True
                self.progress_bar_slider_max = event.data["time"]
                self.progress_bar_slider_state = 0

    def draw(self, camera: Camera):
        zoom_k = 1 / camera.zoom
        self.update_visual(1 / 60)
        if self.state == BuildingState.IDLE:
            if self.selected:
                self.outline_texture.draw(self.position.x, self.position.y, zoom_k * 1.1, zoom_k * 1.1,
                                          color=arcade.color.Color(196, 196, 196))
                self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k)
            elif self.outline_enabled:
                self.outline_texture.draw(self.position.x, self.position.y, zoom_k * 1.1, zoom_k * 1.1,
                                          color=arcade.color.Color(128, 128, 128))
                self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k)
            else:
                self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k)
        elif self.state == BuildingState.BUILDING:

            self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k,
                              alpha=255 * self.building_progress)
