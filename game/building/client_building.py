import arcade.color

from GUI.ui_objects_progress_bar import UIObjectsProgressBar
from game.actions.events import Event, BuildingEvents
from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from game.camera import Camera
from resources.handlers.texture_handle import TextureHandle
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from resources.mods.mods_manager.mods_manager import ModsManager
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
        self.units_queue = server_snapshot["units_queue"]

        self.config: BuildingConfig = self.mods_manager.get_building(server_snapshot["config_name"])

        self.state = BuildingState(server_snapshot["state"])

        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.name)
        self.outline_texture: TextureHandle = self.resource_manager.get_texture(self.config.outline_texture_name)

        self.selected = False
        self.outline_enabled = False
        self.setup_gui()
        self._apply_events([Event.from_dict(event_data) for event_data in server_snapshot["events"]])

        self.on_unit_queue_changed_callback = None

        self.on_move_callbacks = set()

    def _notify_on_move_callback_listeners(self):
        for callback in self.on_move_callbacks:
            callback(self)

    def append_on_move_callback(self, callback):
        self.on_move_callbacks.add(callback)

    def remove_on_move_callback(self, callback):
        if callback in self.on_move_callbacks:
            self.on_move_callbacks.remove(callback)

    def set_on_unit_queue_changed_callback(self, callback):
        self.on_unit_queue_changed_callback = callback

    def reset_on_unit_queue_changed_callback(self):
        self.on_unit_queue_changed_callback = None

    def setup_gui(self):
        x, y = self.position
        w, h = self.texture.get_size()

        self.progress_bar_slider = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-h / 2 - 4,
            width=w - 4,
            height=12,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(150, 150, 50),
            border_color=arcade.color.Color(0, 0, 0)
        )

        self.building_state_progress_bar = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-h / 2 - 4,
            width=w - 4,
            height=12,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(50, 50, 150),
            border_color=arcade.color.Color(0, 0, 0)
        )

        self.health_state_progress_bar = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-h / 2 - 4,
            width=w - 4,
            height=12,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(50, 150, 50),
            border_color=arcade.color.Color(0, 0, 0)
        )
        self.health_state_progress_bar.start(self.config.max_health)

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
        self.health_state_progress_bar.set_state(self.health)
        self.state = BuildingState(snapshot["state"])
        self.level = snapshot["level"]
        self.units_queue = snapshot["units_queue"]
        self._apply_events([Event.from_dict(event_data) for event_data in snapshot["events"]])

    def update_visual(self, delta_time):
        self.progress_bar_slider.on_update(delta_time)
        if self.state == BuildingState.BUILDING:
            self.building_state_progress_bar.on_update(delta_time)

    def _apply_events(self, events: list[Event]):
        for event in events:
            if event.event_type == BuildingEvents.BUILDING_START_BUILDING.value:
                self.building_state_progress_bar.start(event.data["build_time"])
            elif event.event_type == BuildingEvents.BUILDING_END_BUILDING.value:
                self.building_state_progress_bar.stop()
            elif event.event_type == BuildingEvents.PRODUCTION_STARTED.value:
                self.progress_bar_slider.start(event.data["time"])
            elif event.event_type == BuildingEvents.PRODUCTION_STOPPED.value:
                self.progress_bar_slider.stop()
            elif event.event_type == BuildingEvents.PRODUCTION_CONTINUE.value:
                self.progress_bar_slider.continue_()
            elif event.event_type == BuildingEvents.UNIT_ADD_IN_QUEUE.value:
                if self.on_unit_queue_changed_callback:
                    self.on_unit_queue_changed_callback()

    def draw(self, team_color, camera: Camera):
        zoom_k = 1 / camera.zoom
        if self.state == BuildingState.IDLE:
            if self.selected:
                self.outline_texture.draw(self.position.x, self.position.y, zoom_k * 1.1, zoom_k * 1.1,
                                          color=arcade.color.Color(196, 196, 196))
            elif self.outline_enabled:
                self.outline_texture.draw(self.position.x, self.position.y, zoom_k * 1.1, zoom_k * 1.1,
                                          color=arcade.color.Color(128, 128, 128))
            self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k, color=team_color)

            y = 0
            if self.health != self.config.max_health:
                self.health_state_progress_bar.on_draw(camera, y)
                y += 16
            self.progress_bar_slider.on_draw(camera, y)
        elif self.state == BuildingState.BUILDING:

            self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k,
                              alpha=128,
                              color=team_color)
            self.building_state_progress_bar.on_draw(camera, 0)
