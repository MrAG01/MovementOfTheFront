import random

import arcade
from arcade import Vec2
from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from game.building.consumption.consumption_executor import ConsumptionExecutor
from game.building.production.production_executor import ProductionExecutor
from game.unit.server_unit import ServerUnit
from game.unit.unit_config import UnitConfig
from network.network_object import NetworkObject
from game.actions.events import BuildingEvents, Event


class ServerBuilding:
    NEXT_BUILDING_ID = 1

    def __init__(self, owner_player, owner_id, mods_manager, config, position: Vec2, health, level, state,
                 building_timer):
        self.id = ServerBuilding.NEXT_BUILDING_ID
        ServerBuilding.NEXT_BUILDING_ID += 1

        self.mods_manager = mods_manager
        self.owner_id = owner_id
        self.owner_player = owner_player

        self.config: BuildingConfig = config
        self.position: Vec2 = position
        self.health = health
        self.level = level

        self.state = state

        self.building_timer = building_timer
        self.build_time = building_timer

        self.production_index = -1
        if self.config.production is not None:
            self.production_executor = ProductionExecutor(self.owner_player.inventory,
                                                          self.make_dirty)
            self.production_executor_stopped_flag = False
        else:
            self.production_executor = None

        if self.config.consumption is not None:
            self.consumption_executor = ConsumptionExecutor(self.owner_player.inventory,
                                                            self.config.consumption)
        else:
            self.consumption_executor = None

        self.dirty = True
        self.events = []
        self.linked_deposit = None

        self.units_queue = []

        self.add_event(Event(BuildingEvents.BUILDING_START_BUILDING, data={"build_time": self.build_time}))

    def get_events(self):
        if not self.events:
            return []
        events = self.events.copy()
        self.events.clear()
        return list(map(lambda event: event.serialize(), events))

    def add_event(self, event):
        self.events.append(event)
        self.make_dirty()

    def try_to_add_unit_in_queue(self, unit_type):
        if not self.config.can_spawn_units:
            return
        if unit_type in self.config.can_spawn_units:
            unit_config: UnitConfig = self.mods_manager.get_unit(unit_type)
            build_time = unit_config.build_time
            self.units_queue.append([unit_config, build_time])
            self.add_event(Event(event_type=BuildingEvents.UNIT_ADD_IN_QUEUE, data={"unit_type": unit_type}))

    def set_linked_deposit(self, deposit):
        self.linked_deposit = deposit

    def detach_deposit(self):
        if self.linked_deposit:
            self.linked_deposit.detach_mine()
            self.linked_deposit = None

    def working(self):
        return self.state == BuildingState.IDLE and (
                self.consumption_executor is None or
                self.consumption_executor.is_running())

    def is_dirty(self):
        return self.dirty

    def make_dirty(self):
        self.dirty = True

    @classmethod
    def create_new(cls, owner_player, owner_id, config, time_multiplier, position, mods_manager):
        return cls(
            owner_player=owner_player,
            owner_id=owner_id,
            mods_manager=mods_manager,
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
            if self.consumption_executor is not None:
                self.consumption_executor.update(delta_time)
            working = self.working()
            if working and self.units_queue:
                last = self.units_queue[-1]
                last[1] -= delta_time
                if last[1] <= 0:
                    dx = random.randint(-100, 100) / 10
                    dy = random.randint(-100, 100) / 10
                    self.owner_player._add_unit(last[0], self.position + arcade.Vec2(dx, dy))
                    self.units_queue.pop()

            if self.production_executor is not None:
                if self.production_executor.is_running():
                    if self.working():
                        if self.production_executor_stopped_flag:
                            self.production_executor_stopped_flag = False
                            self.add_event(Event(event_type=BuildingEvents.PRODUCTION_CONTINUE))
                        self.production_executor.update(delta_time)
                    else:
                        if not self.production_executor_stopped_flag:
                            self.production_executor_stopped_flag = True
                            self.add_event(Event(event_type=BuildingEvents.PRODUCTION_STOPPED))
                else:
                    rule = self.config.production[self.production_index]
                    if self.production_executor.try_start(rule):
                        self.production_executor_stopped_flag = False
                        self.add_event(Event(event_type=BuildingEvents.PRODUCTION_STARTED,
                                             data={"time": rule.time}))

        if self.health < self.config.max_health:
            self.health += self.config.regeneration * delta_time
            self.make_dirty()
            self.health = max(min(self.health, self.config.max_health), 0)

    def serialize_static(self):
        self.dirty = False
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "state": self.state.value,
            "config_name": self.config.name,
            "position": [self.position.x, self.position.y],
            "health": self.health,
            "level": self.level,
            "events": self.get_events(),
            "units_queue": [(a, b.name) for a, b in self.units_queue]
        }

    def serialize_dynamic(self):
        self.dirty = False
        return {
            "owner_id": self.owner_id,
            "state": self.state.value,
            "health": self.health,
            "level": self.level,
            "events": self.get_events(),
            "production_index": self.production_index,
            "units_queue": [(a.name, b) for a, b in self.units_queue]
        }
