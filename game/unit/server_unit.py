import math

import arcade

from game.actions.events import Event, UnitEvents
from game.unit.unit_config import UnitConfig


class ServerUnit:
    NEXT_UNIT_ID = 1

    def __init__(self, owner_player, owner_id, unit_config, position, game_map):
        self.id = ServerUnit.NEXT_UNIT_ID
        ServerUnit.NEXT_UNIT_ID += 1

        self.game_map = game_map

        self.owner_player = owner_player
        self.owner_id = owner_id
        self.unit_config: UnitConfig = unit_config
        self.position = position

        self.health = unit_config.max_health

        self.hit_box_radius = unit_config.hit_box_radius

        self.dirty = True
        self.should_die = False
        self.path_step = None
        self.path = []

        self.events = []
        self.on_move_callbacks = set()

    def _notify_on_move_callback_listeners(self):
        for callback in self.on_move_callbacks:
            callback(self)

    def append_on_move_callback(self, callback):
        self.on_move_callbacks.add(callback)

    def remove_on_move_callback(self, callback):
        if callback in self.on_move_callbacks:
            self.on_move_callbacks.remove(callback)

    def move(self, arg):
        self.position += arg
        self._notify_on_move_callback_listeners()
        self.make_dirty()

    def move_xy(self, x, y):
        self.position += arcade.Vec2(x, y)
        self._notify_on_move_callback_listeners()
        self.make_dirty()

    def can_attack_building(self, building):
        attack_radius = self.unit_config.attack_radius + self.unit_config.hit_box_radius + building.config.size
        distance_sqr = (self.position - building.position).length_squared()
        return distance_sqr < attack_radius ** 2 and building.owner_id != self.owner_id

    def check_for_attack(self, other_unit):
        if self.owner_id == other_unit.owner_id:
            return
        distance = (self.position - other_unit.position).length()
        sum_of_radius = self.unit_config.hit_box_radius + other_unit.unit_config.hit_box_radius
        self_attack_distance = sum_of_radius + self.unit_config.attack_radius
        other_attack_distance = sum_of_radius + other_unit.unit_config.attack_radius

        first_can_attack = distance <= self_attack_distance
        second_can_attack = distance <= other_attack_distance
        return first_can_attack, second_can_attack

    def try_to_resolve_collision(self, other_unit):
        other_unit: ServerUnit
        is_enemy = self.owner_id != other_unit.owner_id

        delta = self.position - other_unit.position

        distance = delta.length()

        sum_of_radius = self.hit_box_radius + other_unit.hit_box_radius
        if is_enemy:
            required_distance = sum_of_radius
        else:
            required_distance = sum_of_radius * 0.7

        if distance < required_distance and distance > 0:
            overlap = required_distance - distance

            nx = delta.x / distance
            ny = delta.y / distance

            push_power_1 = self.unit_config.push_power
            push_power_2 = other_unit.unit_config.push_power
            push_power_sum = push_power_1 + push_power_2

            mass_1 = push_power_2 / push_power_sum
            mass_2 = push_power_1 / push_power_sum

            move_x = nx * overlap
            move_y = ny * overlap

            self.move(arcade.Vec2(move_x * mass_1, move_y * mass_1))
            other_unit.move(arcade.Vec2(-move_x * mass_2, -move_y * mass_2))

    def get_damage(self, damage):
        self.health -= damage
        self.make_dirty()

    def add_event(self, event):
        self.events.append(event)
        self.make_dirty()

    def get_events(self):
        if not self.events:
            return []
        events = self.events.copy()
        self.events.clear()
        return list(map(lambda event: event.serialize(), events))

    def make_dirty(self):
        self.dirty = True

    def is_dirty(self):
        return self.dirty

    def set_path(self, path):
        self.path = path
        self.add_event(Event(event_type=UnitEvents.NEW_PATH, data={"path": self.path}))
        self.path_step = 0

    def update(self, delta_time):
        if self.health <= 0:
            self.should_die = True
            return

        if self.health < self.unit_config.max_health:
            self.health += self.unit_config.regeneration * delta_time
            self.make_dirty()

            self.health = max(min(self.health, self.unit_config.max_health), 0)

        if self.path and self.path_step < len(self.path):
            speed_k = self.game_map.get_biome(self.position.x, self.position.y).get_speed_k()

            target_x, target_y = self.path[self.path_step]
            current_x, current_y = self.position.x, self.position.y

            dx = target_x - current_x
            dy = target_y - current_y
            distance = math.hypot(dx, dy)

            if distance >= 0:
                if distance > 0.1:
                    speed = self.unit_config.base_speed * speed_k
                    move_distance = speed * delta_time

                    if move_distance >= distance:
                        self.position = arcade.Vec2(target_x, target_y)
                        self._notify_on_move_callback_listeners()
                        self.make_dirty()
                        if self.path_step < len(self.path) - 1:
                            self.path_step += 1
                            self.make_dirty()
                    else:
                        dx_normalized = dx / distance
                        dy_normalized = dy / distance

                        self.move_xy(dx_normalized * move_distance,
                                     dy_normalized * move_distance)
                else:
                    self.position = arcade.Vec2(target_x, target_y)
                    self._notify_on_move_callback_listeners()
                    self.make_dirty()
                    if self.path_step < len(self.path) - 1:
                        self.path_step += 1
                        self.make_dirty()

    def serialize_static(self):
        return {
            "events": self.get_events(),
            "id": self.id,
            "owner_id": self.owner_id,
            "unit_config_name": self.unit_config.name,
            "hit_box_radius": self.hit_box_radius,

            "position": self.position,
            "health": self.health,
            "path_step": self.path_step
        }

    def serialize_dynamic(self):
        self.dirty = False
        return {
            "events": self.get_events(),
            "health": self.health,
            "position": self.position,
            "path_step": self.path_step
        }
