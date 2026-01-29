import math

import arcade

from GUI.ui_objects_progress_bar import UIObjectsProgressBar
from game.actions.events import Event, UnitEvents
from game.unit.unit_config import UnitConfig
from game.vitual_border import VirtualBorder
from resources.handlers.texture_handle import TextureHandle


class ClientUnit:
    def __init__(self, snapshot, resource_manager, mods_manager, map):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.map = map
        self.id = snapshot["id"]
        self.owner_id = snapshot["owner_id"]

        self.virtual_borders: VirtualBorder = map.get_virtual_borders()

        self.config: UnitConfig = mods_manager.get_unit(snapshot["unit_config_name"])
        self.hit_box_radius = snapshot["hit_box_radius"]
        self.health = snapshot["health"]
        self._position = arcade.Vec2(*snapshot["position"])
        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.name)

        self.setup_gui()
        self._apply_events(snapshot["events"])

        self.selected = False
        self.path_step = 0
        self.path = []
        self.predicted_position = arcade.Vec2(*self._position)

        self.update_borders_next_frame = True
        self.on_move_callbacks = set()

    def try_to_resolve_collision(self, other_unit):
        other_unit: ClientUnit
        is_enemy = self.owner_id != other_unit.owner_id

        x1, y1 = self.predicted_position
        x2, y2 = other_unit.predicted_position

        dx = x1 - x2
        dy = y1 - y2

        distance = math.hypot(dx, dy)

        sum_of_radius = self.hit_box_radius + other_unit.hit_box_radius
        if is_enemy:
            required_distance = sum_of_radius
        else:
            required_distance = sum_of_radius * 0.7

        if distance < required_distance and distance > 0:
            overlap = required_distance - distance

            nx = dx / distance
            ny = dy / distance

            push_power_1 = self.config.push_power
            push_power_2 = other_unit.config.push_power
            push_power_sum = push_power_1 + push_power_2

            mass_1 = push_power_2 / push_power_sum
            mass_2 = push_power_1 / push_power_sum

            move_x = nx * overlap
            move_y = ny * overlap

            self.predicted_position = self.predicted_position + arcade.Vec2(move_x * mass_1, move_y * mass_1)
            self._notify_on_move_callback_listeners()
            other_unit.predicted_position = other_unit.predicted_position + arcade.Vec2(-move_x * mass_2,
                                                                                        -move_y * mass_2)
            other_unit._notify_on_move_callback_listeners()

    def can_attack_building(self, building):
        attack_radius = self.config.attack_radius + self.config.hit_box_radius + building.config.size
        distance_sqr = (self._position - building.position).length_squared()
        return distance_sqr < attack_radius ** 2 and building.owner_id != self.owner_id

    def _notify_on_move_callback_listeners(self):
        for callback in self.on_move_callbacks:
            callback(self)

    @property
    def position(self):
        return self.predicted_position

    def append_on_move_callback(self, callback):
        self.on_move_callbacks.add(callback)

    def remove_on_move_callback(self, callback):
        if callback in self.on_move_callbacks:
            self.on_move_callbacks.remove(callback)

    def disable_selection(self):
        self.selected = False

    def enable_selection(self):
        self.selected = True

    def setup_gui(self):
        x, y = self._position
        radius = self.config.texture_radius * 2
        self.health_bar_slider = UIObjectsProgressBar(
            center_x=x,
            top_y=y,
            offset_height=-radius / 2 - 1,
            width=radius,
            height=radius * 0.2,
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
        if self._position != new_pos:
            self._position = new_pos
            self._notify_on_move_callback_listeners()

            distance = (self._position - self.predicted_position).length()
            if distance > 5:
                self.predicted_position = self.predicted_position + (self._position - self.predicted_position) * 0.5

        self.path_step = snapshot["path_step"]
        self._apply_events([Event.from_dict(data) for data in snapshot["events"]])

    def draw(self, team_color, camera, is_self):
        w, h = self.texture.get_size()
        k = (self.config.texture_radius * 2) / w
        draw_x, draw_y = self.predicted_position.x, self.predicted_position.y

        if self.selected:
            arcade.draw_circle_filled(draw_x, draw_y, self.config.texture_radius + 0.5,
                                      arcade.color.Color(200, 200, 200),
                                      num_segments=16)

        self.texture.draw(draw_x, draw_y, color=team_color, scale_x=k, scale_y=k)

        # if self.health != self.config.max_health:
        self.health_bar_slider.center_x = draw_x
        self.health_bar_slider.top_y = draw_y
        self.health_bar_slider.on_draw(camera, 0)

        if is_self and self.path:
            true_path = [(draw_x, draw_y), *self.path[self.path_step:]]
            arcade.draw_line_strip(true_path, arcade.color.Color(255, 255, 255, 100), 3 / camera.zoom)

        # if self.update_borders_next_frame:
        #    self.virtual_borders.draw_unit_field_of_view(50, self.position.x, self.position.y,
        #                                                 arcade.color.Color(255, 0, 0, 50))
