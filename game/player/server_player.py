from components.items import Items
from game.actions.events import Event, PlayerEvents
from game.building.server_building import ServerBuilding
from game.inventory.server_inventory import ServerInventory


class ServerPlayer:
    def __init__(self, player_id, inventory, buildings):
        self.player_id = player_id

        self.buildings: dict[int, ServerBuilding] = buildings
        self.inventory: ServerInventory = ServerInventory(inventory, buildings)
        self.events = []

    def add_event(self, event):
        self.events.append(event)

    def update(self, delta_time):
        for building in self.buildings.values():
            building.update(delta_time)

    @classmethod
    def create_new(cls, player_id):
        return cls(player_id=player_id,
                   inventory=Items({}),
                   buildings={})

    def add_building(self, building: ServerBuilding):
        self.buildings[building.id] = building
        #self.inventory.add_building(building)
        self.add_event(Event(event_type=PlayerEvents.BUILD,
                             data=building.serialize_static()))


    def get_events(self):
        if not self.events:
            return []
        events = self.events.copy()
        self.events.clear()
        return list(map(lambda event: event.serialize(), events))

    def serialize_dynamic(self):
        return {
            "events": self.get_events(),
            "id": self.player_id,
            "inventory": self.inventory.serialize_dynamic(),
            "buildings": {building_id: building.serialize_dynamic() for building_id, building in self.buildings.items()
                          if building.is_dirty()}
        }

    def serialize_static(self):
        return {
            "id": self.player_id,
            "inventory": self.inventory.serialize_static(),
            "buildings": {building_id: building.serialize_static() for building_id, building in self.buildings.items()}
        }
