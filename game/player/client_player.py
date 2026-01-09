from components.items import Items
from game.building.client_building import ClientBuilding


class ClientPlayer:
    def __init__(self, snapshot, resource_manager, mods_manager):
        self.resource_manager = resource_manager
        self.mods_manager = mods_manager
        self.id = snapshot["id"]
        self.inventory = Items.from_dict(snapshot["inventory"])
        self.buildings: dict[int, ClientBuilding] = self._deserialize_buildings(snapshot["buildings"])

    def draw(self):
        for building in self.buildings.values():
            building.draw()

    def is_owner(self, building: ClientBuilding):
        return self.id == building.owner_id

    def update_from_snapshot(self, snapshot):
        pass

    def _deserialize_buildings(self, data):
        return {int(building_id): ClientBuilding(building_data, self.resource_manager, self.mods_manager) for
                building_id, building_data in data.items()}
