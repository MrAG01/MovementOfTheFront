from arcade import Vec2
from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from game.object_types import ObjectType
from network.network_object import NetworkObject
from game.actions.events import BuildingEvents, Event


class ServerBuilding(NetworkObject):
    def __init__(self, owner_id, config: BuildingConfig, position: Vec2):
        super().__init__(owner_id)
        self.config = config
        self.position: Vec2 = position
        self.health = self.config.max_health
        self.level = 1
        self._type: ObjectType = ObjectType.BUILDING

        self.state = BuildingState.BUILDING

        self.building_timer = self.config.build_time
        self.add_event(Event(BuildingEvents.BUILDING_START_BUILDING))

    def update(self, delta_time: float):
        if self.state == BuildingState.BUILDING:
            self.building_timer -= delta_time
            if self.building_timer <= 0:
                self.state = BuildingState.IDLE
                self.add_event(Event(BuildingEvents.BUILDING_END_BUILDING))

        if self.health < self.config.max_health:
            self.health += self.config.regeneration * delta_time
            self.health = max(min(self.health, self.config.max_health), 0)

    def serialize(self):
        return {
            "type": self._type,
            "data": {
                "id": self.id,
                "owner_id": self.owner,
                "state": self.state,
                "config_name": self.config,
                "position": [self.position.x, self.position.y],
                "health": self.health,
                "level": self.level,
                "building_timer": self.building_timer,
                "events": self.get_events()
            }
        }
