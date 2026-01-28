import random

import arcade

from components.item import Item
from components.items import Items
from game.actions.events import Event, PlayerEvents
from game.building.server_building import ServerBuilding
from game.inventory.server_inventory import ServerInventory
from game.map.server_map import ServerMap
from game.unit.server_unit import ServerUnit
from resources.mods.mods_manager.mods_manager import ModsManager


class ServerPlayer:
    def __init__(self, player_id, inventory, buildings, units, team):
        self.player_id = player_id

        self.buildings: dict[int, ServerBuilding] = buildings
        self.units: dict[int, ServerUnit] = units

        self.houses_capacity = 0
        self.max_houses_capacity = 0

        self.inventory: ServerInventory = ServerInventory(inventory, buildings)
        self.events = []
        self.town_hall = None

        self.team = team
        self.attached_game_state = None
        self.death = False
        self.dirty = True

    def generate_town_hall(self, mods_manager: ModsManager):
        map: ServerMap = self.attached_game_state.map
        w, h = map.get_size()
        x, y = random.randint(int(w * 0.1), int(w - w * 0.1)), random.randint(int(h * 0.1), int(h - h * 0.1))
        while not map.get_biome(x, y).can_build_on:
            x, y = random.randint(int(w * 0.1), int(w - w * 0.1)), random.randint(int(h * 0.1), int(h - h * 0.1))
        self.town_hall = ServerBuilding.create_new(self, self.player_id, mods_manager.get_building("town_hall"),
                                                   1, arcade.Vec2(x, y),
                                                   mods_manager)
        self.buildings[self.town_hall.id] = self.town_hall
        self.max_houses_capacity += self.town_hall.config.units_capacity

    def attach_game_state(self, game_state):
        self.attached_game_state = game_state

    def _add_unit(self, unit_config, position):
        if self.attached_game_state:
            required_capacity = unit_config.required_capacity
            # if self.houses_capacity + required_capacity > self.max_houses_capacity:
            #    return False

            # self.houses_capacity += required_capacity
            unit = ServerUnit(self, self.player_id, unit_config, position, self.attached_game_state.map)
            self.units[unit.id] = unit
            self.add_event(Event(event_type=PlayerEvents.SPAWN_UNIT, data=unit.serialize_static()))
            self.attached_game_state.register_unit(unit)
            self.make_dirty()
            return True
        else:
            return False

    def get_building(self, building_id):
        if building_id not in self.buildings:
            return
        return self.buildings[building_id]

    def make_dirty(self):
        self.dirty = True

    def is_dirty(self):
        return self.dirty

    def add_event(self, event):
        self.events.append(event)
        self.make_dirty()

    def update(self, delta_time):
        buildings_die_list = []
        for building in self.buildings.values():
            building.update(delta_time)
            if building.is_dirty():
                self.make_dirty()
            if building.should_die:
                buildings_die_list.append(building)

        if self.town_hall.should_die:
            self.death = True
            self.attached_game_state.player_base_destroyed(self)

        for death_building in buildings_die_list:
            self.remove_building(death_building.id)

        unit_die_list = []
        for unit in self.units.values():
            unit.update(delta_time)
            if unit.is_dirty():
                self.make_dirty()
            if unit.should_die:
                unit_die_list.append(unit)
                self.make_dirty()

        for death_unit in unit_die_list:
            self.delete_unit(death_unit)

    @classmethod
    def create_new(cls, player_id, team):
        return cls(player_id=player_id,
                    inventory=Items({"food": Item("food", 100),
                                    "wood": Item("wood", 100)}),
                   #inventory=Items({"food": Item("food", 1000),
                   #                 "wood": Item("wood", 1000),
                   #    "planks": Item("planks", 150),
                   #                 "stone": Item("stone", 100),
                    #                "peoples": Item("peoples", 100)}),
                   buildings={},
                   units={},
                   team=team)

    def try_to_set_building_production(self, building_id, production_index):
        if building_id not in self.buildings:
            return
        building = self.buildings[building_id]
        building.set_production_index(production_index)

    def add_building(self, building: ServerBuilding):
        self.buildings[building.id] = building
        # self.inventory.add_building(building)
        self.max_houses_capacity += building.config.units_capacity

        self.add_event(Event(event_type=PlayerEvents.BUILD,
                             data=building.serialize_static()))

    def delete_unit(self, unit):
        unit_id = unit.id
        if unit_id not in self.units:
            return
        self.add_event(Event(event_type=PlayerEvents.DELETE_UNIT,
                             data=unit_id))
        if self.attached_game_state:
            self.attached_game_state.remove_unit(unit)
        del self.units[unit_id]

    def remove_building(self, building_id):
        if building_id not in self.buildings:
            return
        building = self.buildings[building_id]
        building.detach_deposit()
        self.attached_game_state.remove_building(building)
        self.add_event(Event(event_type=PlayerEvents.DESTROY,
                             data=building_id))
        del self.buildings[building_id]

    def try_to_make_new_unit_path(self, unit_id, new_path):
        if unit_id not in self.units:
            return
        unit = self.units[unit_id]
        unit.set_path(new_path)

    def try_to_add_unit_in_queue(self, building_id, unit_type):
        if building_id not in self.buildings:
            return
        building = self.buildings[building_id]
        building.try_to_add_unit_in_queue(unit_type)

    def get_events(self):
        if not self.events:
            return []
        events = self.events.copy()
        self.events.clear()
        return list(map(lambda event: event.serialize(), events))

    def serialize_dynamic(self):
        self.dirty = False
        return {
            "events": self.get_events(),
            "inventory": self.inventory.serialize_dynamic(),
            "buildings": {building_id: building.serialize_dynamic() for building_id, building in self.buildings.items()
                          if building.is_dirty()},
            "units": {unit_id: unit.serialize_static() for unit_id, unit in self.units.items() if unit.is_dirty()},
            "max_houses_capacity": self.max_houses_capacity,
            "houses_capacity": self.houses_capacity
        }

    def serialize_static(self):
        return {
            "id": self.player_id,
            "inventory": self.inventory.serialize_static(),
            "buildings": {building_id: building.serialize_static() for building_id, building in self.buildings.items()},
            "units": {unit_id: unit.serialize_static() for unit_id, unit in self.units.items()},
            "team": self.team,
            "max_houses_capacity": self.max_houses_capacity,
            "houses_capacity": self.houses_capacity
        }
