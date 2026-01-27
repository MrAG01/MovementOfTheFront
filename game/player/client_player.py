import time

import arcade
from arcade import SpriteList

from game.actions.events import PlayerEvents, Event
from game.building.client_building import ClientBuilding
from game.inventory.client_inventory import ClientInventory
from game.unit.client_unit import ClientUnit
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from utils.space_hash_map import SpaceHashMap


class ClientPlayer:
    def __init__(self, snapshot, resource_manager, mods_manager, game_state):
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.game_state = game_state
        self.id = snapshot["id"]
        self.inventory = ClientInventory(snapshot["inventory"])
        self.team = snapshot["team"]
        self.team_color: arcade.color.Color = self.resource_manager.get_team_color(self.team)
        self.buildings: dict[int, ClientBuilding] = self._deserialize_objects_with_ids(snapshot["buildings"],
                                                                                       ClientBuilding,
                                                                                       team_color=self.team_color)
        self.units: dict[int, ClientUnit] = self._deserialize_objects_with_ids(snapshot["units"], ClientUnit)

        self.buildings_space_map: SpaceHashMap = SpaceHashMap(self.buildings.values(), 100)
        self.units_space_map: SpaceHashMap = SpaceHashMap(self.units.values(), 30)

        self.max_houses_capacity = 0
        self.houses_capacity = 0

        self.buildings_sprite_list = None

    def get_town_hall(self):
        for building in self.buildings.values():
            if building.config.name == "town_hall":
                return building

    def setup_buildings_sprite_list(self):
        self.buildings_sprite_list = SpriteList(use_spatial_hash=True)
        for building in self.buildings.values():
            self.buildings_sprite_list.append(building)

    def get_buildings_in_rect(self, rect: list | tuple):
        return self.buildings_space_map.get_in_rect(rect)

    def get_units_in_rect(self, rect: list | tuple):
        return self.units_space_map.get_in_rect(rect)

    def get_units_close_to(self, x, y):
        return self.units_space_map.get_at(x, y)

    def get_closest_buildings_to(self, x, y):
        return self.buildings_space_map.get_at(x, y)

    def update_visual(self, delta_time):
        for building in list(self.buildings.values()):
            building.update_visual(delta_time)
        for unit in list(self.units.values()):
            unit.update_visual(delta_time)

    def draw(self, camera, draw_buildings_alpha, is_self):
        # start_time = time.time()
        alpha = 128 if draw_buildings_alpha else 255
        if not self.buildings_sprite_list:
            self.setup_buildings_sprite_list()

        if is_self:
            for building in list(self.buildings.values()):
                building.draw_non_static(camera, alpha)
        self.buildings_sprite_list.draw(pixelated=True)

        for unit in list(self.units.values()):
            unit.draw(self.team_color, camera, is_self)

        # end_time = time.time()
        # delta = end_time - start_time
        # if delta:
        #    print(
        #        f"DRAWING TIME: {delta:.5f}; MAX FPS: {1 / delta:.1f}")

    def is_owner(self, building: ClientBuilding):
        return self.id == building.owner_id

    def _handle_events(self, events):
        for event in events:
            if event.event_type == PlayerEvents.BUILD.value:
                data = event.data
                building = ClientBuilding(data, self.resource_manager, self.mods_manager, self.team_color)
                self.buildings[data["id"]] = building
                self.game_state.register_building(building)
                self.buildings_space_map.add(building)
                if self.buildings_sprite_list:
                    self.buildings_sprite_list.append(building)
            elif event.event_type == PlayerEvents.DESTROY.value:
                data = event.data
                building = self.buildings[data]
                self.game_state.remove_building(building)
                self.buildings_space_map.remove(building)
                if self.buildings_sprite_list:
                    self.buildings_sprite_list.remove(building)
                del self.buildings[data]
            elif event.event_type == PlayerEvents.SPAWN_UNIT.value:
                data = event.data
                unit = ClientUnit(data, self.resource_manager, self.mods_manager, self.game_state.map)
                self.units[data["id"]] = unit
                self.game_state.register_unit(unit)
                self.units_space_map.add(unit)
            elif event.event_type == PlayerEvents.DELETE_UNIT.value:
                data = event.data
                unit = self.units[data]
                self.units_space_map.remove(unit)
                self.game_state.remove_unit(unit)
                del self.units[data]

    def update_from_snapshot(self, snapshot):
        self.inventory.update_from_snapshot(snapshot["inventory"])

        self._handle_events([Event.from_dict(event) for event in snapshot["events"]])

        buildings_data = snapshot["buildings"]
        for building_id in buildings_data:
            if int(building_id) in self.buildings:
                self.buildings[int(building_id)].update_from_snapshot(buildings_data[building_id])

        units_data = snapshot["units"]
        for unit_id in units_data:
            if int(unit_id) in self.units:
                self.units[int(unit_id)].update_from_snapshot(units_data[unit_id])

        self.max_houses_capacity = snapshot["max_houses_capacity"]
        self.houses_capacity = snapshot["houses_capacity"]

    def _deserialize_objects_with_ids(self, data, class_, **kwargs):
        return {int(id): class_(object_data, self.resource_manager, self.mods_manager, **kwargs) for
                id, object_data in data.items()}
