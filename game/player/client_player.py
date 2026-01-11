from game.actions.events import PlayerEvents, Event
from game.building.client_building import ClientBuilding
from game.inventory.client_inventory import ClientInventory


class ClientPlayer:
    def __init__(self, snapshot, resource_manager, mods_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.id = snapshot["id"]
        self.inventory = ClientInventory(snapshot["inventory"])
        self.buildings: dict[int, ClientBuilding] = self._deserialize_buildings(snapshot["buildings"])

    def draw(self, camera):
        for building in list(self.buildings.values()):
            building.draw(camera)

    def is_owner(self, building: ClientBuilding):
        return self.id == building.owner_id

    def _handle_events(self, events):
        for event in events:
            if event.event_type == PlayerEvents.BUILD.value:
                data = event.data
                self.buildings[data["id"]] = ClientBuilding(data, self.resource_manager, self.mods_manager)

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
