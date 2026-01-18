from components.items import Items
from game.actions.events import Event, PlayerEvents
from game.building.server_building import ServerBuilding
from game.inventory.server_inventory import ServerInventory
from game.unit.server_unit import ServerUnit


class ServerPlayer:
    def __init__(self, player_id, inventory, buildings, units, team):
        self.player_id = player_id

        self.buildings: dict[int, ServerBuilding] = buildings
        self.units: dict[int, ServerUnit] = units

        self.inventory: ServerInventory = ServerInventory(inventory, buildings)
        self.events = []

        self.team = team
        self.attached_game_state = None

        self.dirty = True

    def attach_game_state(self, game_state):
        self.attached_game_state = game_state

    def _add_unit(self, unit_config, position):
        unit = ServerUnit(self, self.player_id, unit_config, position)
        self.units[unit.id] = unit
        self.add_event(Event(event_type=PlayerEvents.SPAWN_UNIT, data=unit.serialize_static()))
        if self.attached_game_state:
            self.attached_game_state.register_unit(unit)

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
        for building in self.buildings.values():
            building.update(delta_time)
            if building.is_dirty():
                self.make_dirty()
        for unit in self.units.values():
            unit.update(delta_time)
            if unit.is_dirty():
                self.make_dirty()

    @classmethod
    def create_new(cls, player_id, team):
        return cls(player_id=player_id,
                   inventory=Items({}),
                   buildings={},
                   units={},
                   team=team)

    def add_building(self, building: ServerBuilding):
        self.buildings[building.id] = building
        # self.inventory.add_building(building)
        self.add_event(Event(event_type=PlayerEvents.BUILD,
                             data=building.serialize_static()))

    def remove_building(self, building_id):
        if building_id not in self.buildings:
            return
        building = self.buildings[building_id]
        building.detach_deposit()
        self.add_event(Event(event_type=PlayerEvents.DESTROY,
                             data=building_id))
        del self.buildings[building_id]

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
            "units": {unit_id: unit.serialize_static() for unit_id, unit in self.units.items() if unit.is_dirty()}
        }

    def serialize_static(self):
        return {
            "id": self.player_id,
            "inventory": self.inventory.serialize_static(),
            "buildings": {building_id: building.serialize_static() for building_id, building in self.buildings.items()},
            "units": {unit_id: unit.serialize_static() for unit_id, unit in self.units.items()},
            "team": self.team
        }
