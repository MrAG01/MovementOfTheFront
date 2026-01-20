import arcade

from GUI.ui_objects_progress_bar import UIObjectsProgressBar
from game.actions.events import Event, UnitEvents
from game.unit.unit_config import UnitConfig
from resources.handlers.texture_handle import TextureHandle


class ClientUnit:
    def __init__(self, snapshot, resource_manager, mods_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.id = snapshot["id"]
        self.owner_id = snapshot["owner_id"]

        self.config: UnitConfig = mods_manager.get_unit(snapshot["unit_config_name"])

        self.hit_box_radius = snapshot["hit_box_radius"]

        self.health = snapshot["health"]
        self.position = arcade.Vec2(*snapshot["position"])

        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.name)

        self.setup_gui()
        self._apply_events(snapshot["events"])

        self.on_move_callbacks = set()

        self.selected = False

        self.path_step = 0
        self.path = []

    def disable_selection(self):
        self.selected = False

    def enable_selection(self):
        self.selected = True

    def setup_gui(self):
        x, y = self.position
        w, h = self.texture.get_size()

        self.health_bar_slider = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-h / 2 - 4,
            width=w - 4,
            height=12,
            bg_color=arcade.color.Color(50, 50, 50),
            bar_color=arcade.color.Color(50, 150, 50),
            border_color=arcade.color.Color(0, 0, 0)
        )
        self.health_bar_slider.start(self.config.max_health)

    def _apply_events(self, events: list[Event]):
        for event in events:
            #print(event)
            if event.event_type == UnitEvents.NEW_PATH.value:
                self.path = event.data["path"]

    def update_from_snapshot(self, snapshot):
        self.health = snapshot["health"]
        self.health_bar_slider.set_state(self.health)

        new_pos = arcade.Vec2(*snapshot["position"])
        if new_pos != self.position:
            self.position = new_pos
            self._notify_on_move_callback_listeners()
        self.path_step = snapshot["path_step"]
        self._apply_events([Event.from_dict(data) for data in snapshot["events"]])

    def _notify_on_move_callback_listeners(self):
        for callback in self.on_move_callbacks:
            callback(self)

    def append_on_move_callback(self, callback):
        self.on_move_callbacks.add(callback)

    def remove_on_move_callback(self, callback):
        if callback in self.on_move_callbacks:
            self.on_move_callbacks.remove(callback)

    def draw(self, team_color, camera):
        w, h = self.texture.get_size()

        k = (self.config.texture_radius * 2) / w

        if self.selected:
            arcade.draw_circle_filled(self.position.x, self.position.y, self.config.texture_radius + 1,
                                      arcade.color.Color(200, 200, 200))

        self.texture.draw(self.position.x, self.position.y, color=team_color, scale_x=k, scale_y=k)
        if self.health != self.config.max_health:
            self.health_bar_slider.center_x = self.position.x
            self.health_bar_slider.top_y = self.position.y
            self.health_bar_slider.on_draw(camera, 0)

        if self.path:
            true_path = [(self.position.x, self.position.y), *self.path[self.path_step:]]
            arcade.draw_line_strip(true_path, arcade.color.Color(255, 255, 255, 100), 3 / camera.zoom)
