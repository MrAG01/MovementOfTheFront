from game.actions.events import PlayerEvents, Event
from game.building.client_building import ClientBuilding
from game.inventory.client_inventory import ClientInventory
from utils.space_hash_map import SpaceHashMap


class ClientPlayer:
    def __init__(self, snapshot, resource_manager, mods_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.id = snapshot["id"]
        self.inventory = ClientInventory(snapshot["inventory"])
        self.buildings: dict[int, ClientBuilding] = self._deserialize_buildings(snapshot["buildings"])

        self.buildings_space_map: SpaceHashMap = SpaceHashMap(self.buildings, 100)

    def get_closest_buildings_to(self, x, y):
        return self.buildings_space_map.get_at(x, y)

    def draw(self, camera):
        for building in list(self.buildings.values()):
            building.draw(camera)

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

    def update_from_snapshot(self, snapshot):
        self.inventory.update_from_snapshot(snapshot["inventory"])

        self._handle_events([Event.from_dict(event) for event in snapshot["events"]])

        buildings_data = snapshot["buildings"]
        for building_id in buildings_data:
            if int(building_id) in self.buildings:
                self.buildings[int(building_id)].update_from_snapshot(buildings_data[building_id])

    def _deserialize_buildings(self, data):
        return {int(building_id): ClientBuilding(building_data, self.resource_manager, self.mods_manager) for
                building_id, building_data in data.items()}
