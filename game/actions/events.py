import time
from enum import Enum


class Event:
    def __init__(self, event_type, data=None):
        self.event_type = event_type
        self.data = data

    def serialize(self):
        return {
            "event_type": self.event_type.value,
            "data": self.data or {}
        }


class ServerEvents(Enum):
    pass


class GameEvents(Enum):
    GAME_STARTED = "game_started"
    GAME_OVER = "game_over"


class BuildingEvents(Enum):
    BUILDING_START_BUILDING = "building_start_building"
    BUILDING_END_BUILDING = "building_end_building"
    BUILDING_TOOK_DAMAGE = "building_took_damage"
    BUILDING_DESTROYED = "building_destroyed"
    BUILDING_ATTACKING = "building_attacking"
