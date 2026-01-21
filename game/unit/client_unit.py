import math

import arcade

from GUI.ui_objects_progress_bar import UIObjectsProgressBar
from game.actions.events import Event, UnitEvents
from game.unit.unit_config import UnitConfig
from resources.handlers.texture_handle import TextureHandle


class ClientUnit:
    def __init__(self, snapshot, resource_manager, mods_manager, map):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.map = map
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
        self.predicted_position = arcade.Vec2(*self.position)

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
            if event.event_type == UnitEvents.NEW_PATH.value:
                self.path = event.data["path"]
                self.path_step = 0

    def update_visual(self, delta_time):
        if self.path and self.path_step < len(self.path):
            speed_k = self.map.get_biome(self.predicted_position.x, self.predicted_position.y).get_speed_k()

            target_x, target_y = self.path[self.path_step]
            current_x, current_y = self.predicted_position.x, self.predicted_position.y

            dx = target_x - current_x
            dy = target_y - current_y
            distance = math.hypot(dx, dy)

            if distance > 0:
                if distance > 0.1:
                    speed = self.config.base_speed * speed_k
                    move_distance = speed * delta_time

                    if move_distance >= distance:
                        self.predicted_position = arcade.Vec2(target_x, target_y)
                        self.path_step += 1
                        self._notify_on_move_callback_listeners()
                    else:
                        dx_normalized = dx / distance
                        dy_normalized = dy / distance
                        new_x = current_x + dx_normalized * move_distance
                        new_y = current_y + dy_normalized * move_distance
                        self.predicted_position = arcade.Vec2(new_x, new_y)
                        self._notify_on_move_callback_listeners()
                else:
                    self.predicted_position = arcade.Vec2(target_x, target_y)
                    self.path_step += 1
                    self._notify_on_move_callback_listeners()

    def update_from_snapshot(self, snapshot):
        self.health = snapshot["health"]
        self.health_bar_slider.set_state(self.health)

        new_pos = arcade.Vec2(*snapshot["position"])

        if new_pos != self.predicted_position:
            correction_threshold = 0.0
            distance_to_server = math.dist((new_pos.x, new_pos.y),
                                           (self.predicted_position.x, self.predicted_position.y))

            if distance_to_server > correction_threshold:
                self.predicted_position = new_pos
            else:
                interpolation_factor = 0.9
                new_x = self.predicted_position.x + (new_pos.x - self.predicted_position.x) * interpolation_factor
                new_y = self.predicted_position.y + (new_pos.y - self.predicted_position.y) * interpolation_factor
                self.predicted_position = arcade.Vec2(new_x, new_y)

            self.position = arcade.Vec2(self.predicted_position.x, self.predicted_position.y)
            self._notify_on_move_callback_listeners()
        else:
            self.position = new_pos

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
        draw_x, draw_y = self.predicted_position.x, self.predicted_position.y

        if self.selected:
            arcade.draw_circle_filled(draw_x, draw_y, self.config.texture_radius + 1,
                                      arcade.color.Color(200, 200, 200))

        self.texture.draw(draw_x, draw_y, color=team_color, scale_x=k, scale_y=k)

        if self.health != self.config.max_health:
            self.health_bar_slider.center_x = draw_x
            self.health_bar_slider.top_y = draw_y
            self.health_bar_slider.on_draw(camera, 0)

        if self.path:
            true_path = [(draw_x, draw_y), *self.path[self.path_step:]]
            arcade.draw_line_strip(true_path, arcade.color.Color(255, 255, 255, 100), 3 / camera.zoom)
