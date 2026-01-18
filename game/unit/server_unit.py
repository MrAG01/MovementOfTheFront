import math

import arcade

from game.unit.unit_config import UnitConfig


class ServerUnit:
    NEXT_UNIT_ID = 1

    def __init__(self, owner_player, owner_id, unit_config, position):
        self.id = ServerUnit.NEXT_UNIT_ID
        ServerUnit.NEXT_UNIT_ID += 1

        self.owner_player = owner_player
        self.owner_id = owner_id
        self.unit_config: UnitConfig = unit_config
        self.position = position

        self.health = unit_config.max_health

        self.hit_box_radius = unit_config.hit_box_radius

        self.dirty = True

        self.path_step = None
        self.path = []

        self.events = []

    def move(self, arg):
        self.position += arg
        self.make_dirty()

    def try_to_resolve_collision(self, other_unit):
        other_unit: ServerUnit
        x1, y1 = self.position
        x2, y2 = other_unit.position

        dx = x1 - x2
        dy = y1 - y2

        distance = math.hypot(dx, dy)
        required_distance = self.hit_box_radius + other_unit.hit_box_radius

        if distance < required_distance and distance > 0:
            overlap = required_distance - distance

            nx = dx / distance
            ny = dy / distance

            push_power_1 = self.unit_config.push_power
            push_power_2 = other_unit.unit_config.push_power
            push_power_sum = push_power_1 + push_power_2

            mass_1 = push_power_2 / push_power_sum
            mass_2 = push_power_1 / push_power_sum

            move_x = nx * overlap
            move_y = ny * overlap

            self.move(arcade.Vec2(move_x * mass_1, move_y * mass_1))
            other_unit.move(arcade.Vec2(-move_x * mass_2, -move_y * mass_2))

            if self.owner_id != other_unit.owner_id:
                self.health -= other_unit.unit_config.units_damage
                other_unit.health -= self.unit_config.units_damage

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
        self.path_step = 0

    def update(self, delta_time):
        if self.health < self.unit_config.max_health:
            self.health += self.unit_config.regeneration * delta_time
            self.make_dirty()
            self.health = max(min(self.health, self.unit_config.max_health), 0)

    def serialize_static(self):
        return {
            "events": self.get_events(),
            "id": self.id,
            "owner_id": self.owner_id,
            "unit_config_name": self.unit_config.name,
            "hit_box_radius": self.hit_box_radius,

            "position": self.position,
            "health": self.health
        }

    def serialize_dynamic(self):
        self.dirty = False
        return {
            "events": self.get_events(),
            "health": self.health,
            "position": self.position
        }
