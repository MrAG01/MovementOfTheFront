import arcade

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
        self.buildings: dict[int, ClientBuilding] = self._deserialize_objects_with_ids(snapshot["buildings"],
                                                                                       ClientBuilding)
        self.units: dict[int, ClientUnit] = self._deserialize_objects_with_ids(snapshot["units"], ClientUnit)
        self.team = snapshot["team"]

        self.buildings_space_map: SpaceHashMap = SpaceHashMap(self.buildings.values(), 100)
        self.units_space_map: SpaceHashMap = SpaceHashMap(self.units.values(), 30)

        self.team_color = self.resource_manager.get_team_color(self.team)

    def get_units_in_rect(self, rect: list):
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


    def draw(self, camera):
        for building in list(self.buildings.values()):
            building.draw(self.team_color, camera)
        for unit in list(self.units.values()):
            unit.draw(self.team_color, camera)

    def is_owner(self, building: ClientBuilding):
        return self.id == building.owner_id

    def _handle_events(self, events):
        for event in events:
            if event.event_type == PlayerEvents.BUILD.value:
                data = event.data
                building = ClientBuilding(data, self.resource_manager, self.mods_manager)
                self.buildings[data["id"]] = building
                self.buildings_space_map.add(building)
            elif event.event_type == PlayerEvents.DESTROY.value:
                data = event.data
                building = self.buildings[data]
                self.buildings_space_map.remove(building)
                del self.buildings[data]
            elif event.event_type == PlayerEvents.SPAWN_UNIT.value:
                data = event.data
                unit = ClientUnit(data, self.resource_manager, self.mods_manager, self.game_state.map)
                self.units[data["id"]] = unit
                self.units_space_map.add(unit)
            elif event.event_type == PlayerEvents.DELETE_UNIT.value:
                data = event.data
                unit = self.units[data]
                self.units_space_map.remove(unit)
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

    def _deserialize_objects_with_ids(self, data, class_):
        return {int(id): class_(object_data, self.resource_manager, self.mods_manager) for
                id, object_data in data.items()}
