from arcade import Vec2
from game.building.building_state import BuildingState
from network.network_object import NetworkObject
from game.actions.events import BuildingEvents, Event



class ServerBuilding(NetworkObject):
    def __init__(self, owner_id, config, position: Vec2, health, level, state, building_timer):
        super().__init__(owner_id)
        self.config = config
        self.position: Vec2 = position
        self.health = health
        self.level = level

        self.state = state

        self.building_timer = building_timer
        self.add_event(Event(BuildingEvents.BUILDING_START_BUILDING))

    @classmethod
    def create_new(cls, owner_id, config, time_multiplier, position):
        return cls(owner_id=owner_id,
                   config=config,
                   position=position,
                   health=config.max_health,
                   level=1,
                   state=BuildingState.BUILDING,
                   building_timer=config.build_time * time_multiplier)

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
            "id": self.id,
            "owner_id": self.owner,
            "state": self.state,
            "config_name": self.config.name,
            "position": [self.position.x, self.position.y],
            "health": self.health,
            "level": self.level,
            "building_timer": self.building_timer,
            "events": self.get_events()
        }
