from arcade import Vec2
from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from game.building.consumption.consumption_executor import ConsumptionExecutor
from game.building.production.production_executor import ProductionExecutor
from network.network_object import NetworkObject
from game.actions.events import BuildingEvents, Event


class ServerBuilding(NetworkObject):
    def __init__(self, owner_player, owner_id, config, position: Vec2, health, level, state, building_timer):
        super().__init__(owner_id)
        self.owner_player = owner_player

        self.config: BuildingConfig = config
        self.position: Vec2 = position
        self.health = health
        self.level = level

        self.state = state

        self.building_timer = building_timer
        self.build_time = building_timer
        self.add_event(Event(BuildingEvents.BUILDING_START_BUILDING))

        self.production_index = -1
        if self.config.production is not None:
            self.production_executor = ProductionExecutor(self.owner_player.inventory,
                                                          self.make_dirty)
        else:
            self.production_executor = None

        if self.config.consumption is not None:
            self.consumption_executor = ConsumptionExecutor(self.owner_player.inventory,
                                                            self.config.consumption)
        else:
            self.consumption_executor = None

        self.dirty = True

    def working(self):
        return self.state == BuildingState.IDLE and (
                self.consumption_executor is None or
                self.consumption_executor.is_running())

    def is_dirty(self):
        return self.dirty

    def make_dirty(self):
        self.dirty = True

    @classmethod
    def create_new(cls, owner_player, owner_id, config, time_multiplier, position):
        return cls(
            owner_player=owner_player,
            owner_id=owner_id,
            config=config,
            position=position,
            health=config.max_health,
            level=1,
            state=BuildingState.BUILDING,
            building_timer=config.build_time * time_multiplier)

    def update(self, delta_time: float):
        # print(f"UPDATING BUILDING: {delta_time}, BUILDING TIMER: {self.building_timer}")
        if self.state == BuildingState.BUILDING:
            self.building_timer -= delta_time
            if self.building_timer <= 0:
                self.state = BuildingState.IDLE
                self.add_event(Event(BuildingEvents.BUILDING_END_BUILDING))
            self.make_dirty()

        if self.state == BuildingState.IDLE:
            if self.production_executor is not None:
                if self.production_executor.is_running():
                    self.production_executor.update(delta_time)
                else:
                    self.production_executor.try_start(self.config.production[self.production_index])
            if self.consumption_executor is not None:
                self.consumption_executor.update(delta_time)

        if self.health < self.config.max_health:
            self.health += self.config.regeneration * delta_time
            self.make_dirty()
            self.health = max(min(self.health, self.config.max_health), 0)

    def serialize_static(self):
        self.dirty = False
        return {
            "id": self.id,
            "owner_id": self.owner,
            "state": self.state.value,
            "config_name": self.config.name,
            "position": [self.position.x, self.position.y],
            "health": self.health,
            "level": self.level,
            "building_progress": 1 - (self.building_timer / self.build_time),
            "events": self.get_events()
        }

    def serialize_dynamic(self):
        self.dirty = False
        return {
            "owner_id": self.owner,
            "state": self.state.value,
            "health": self.health,
            "level": self.level,
            "building_progress": 1 - (self.building_timer / self.build_time),
            "events": self.get_events(),
            "production_index": self.production_index
        }
