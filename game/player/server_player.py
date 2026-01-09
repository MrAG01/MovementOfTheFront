from components.items import Items
from game.building.server_building import ServerBuilding


class ServerPlayer:
    def __init__(self, player_id, inventory, buildings):
        self.player_id = player_id
        self.inventory: Items = inventory
        self.buildings: dict[int, ServerBuilding] = buildings

    @classmethod
    def create_new(cls, player_id):
        return cls(player_id=player_id,
                   inventory=Items({}),
                   buildings={})

    def add_building(self, building: ServerBuilding):
        self.buildings[building.id] = building

    def serialize(self):
        return {
            "id": self.player_id,
            "inventory": self.inventory.serialize(),
            "buildings": {building_id: building.serialize() for building_id, building in self.buildings.items()}
        }