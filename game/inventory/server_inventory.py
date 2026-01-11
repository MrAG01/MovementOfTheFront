from components.item import Item
from components.items import Items
from game.building.server_building import ServerBuilding


class ServerInventory:
    def __init__(self, items, buildings=()):
        self.items: Items = items
        self.productivity = {} #ServerInventory.calculate_productivity_full(buildings)

        self.dirty = True

    @staticmethod
    def calculate_productivity_full(buildings):
        productivity = {}
        for building in buildings:
            ServerInventory.add_building_in_productivity_container(building, productivity)
        return productivity

    def make_dirty(self):
        self.dirty = True

    def is_dirty(self):
        return self.dirty

    @staticmethod
    def add_building_in_productivity_container(building, productivity_container):
        building: ServerBuilding

        production_ex: "ProductionExecutor" = building.production_executor
        consumption_ex: "ConsumptionExecutor" = building.consumption_executor

        if production_ex is not None:
            production_rule: "ProductionRule" = production_ex.current_rule
            _input = production_rule.input
            _output = production_rule.output
            _time = production_rule.time
            for item_name, item in _input:
                if item_name in productivity_container:
                    productivity_container[item_name] -= item.amount / _time
                else:
                    productivity_container[item_name] = -(item.amount / _time)
            for item_name, item in _output:
                if item_name in productivity_container:
                    productivity_container[item_name] += item.amount / _time
                else:
                    productivity_container[item_name] = item.amount / _time

        if consumption_ex is not None:
            consumption_rule: "ConsumptionRule" = consumption_ex.consumption_rule
            _consumption = consumption_rule.production
            _time = consumption_rule.time
            for item_name, item in _consumption:
                if item_name in productivity_container:
                    productivity_container[item_name] -= item.amount / _time
                else:
                    productivity_container[item_name] = -(item.amount / _time)

    def add_building(self, building):
        ServerInventory.add_building_in_productivity_container(building, self.productivity)

    def has_amount(self, items: Items):
        return self.items.has_amount(items)

    def add(self, item: Item):
        self.items.add(item)

    def adds(self, items: Items):
        self.items.adds(items)

    def sub(self, item: Item):
        self.items.sub(item)

    def subs(self, items: Items):
        return self.items.subs(items)

    def serialize_static(self):
        self.dirty = False
        return {
            "items": self.items.serialize_static(),
            "productivity": self.productivity
        }

    def serialize_dynamic(self):
        self.dirty = False
        return {
            "items": self.items.serialize_static(),
            "productivity": self.productivity
        }
