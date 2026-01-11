from components.item import Item


class Items:
    def __init__(self, items: dict[str, Item]):
        self.items: dict[str, Item] = items

    def __iter__(self):
        return iter(self.items.items())

    def __bool__(self):
        return bool(self.items)

    def __repr__(self):
        return f"Items(items={self.items})"

    def has_amount(self, cost: "Items"):
        for item_name, item_data in cost:
            value = item_data.amount
            if value == 0:
                continue
            if item_name in self.items:
                if not self.items[item_name].has_amount(value):
                    return False
            else:
                return False
        return True

    def subs(self, cost: "Items"):
        if self.has_amount(cost):
            for item_name, item_data in cost:
                value = item_data.amount
                if value == 0:
                    continue
                if item_name in self.items:
                    self.items[item_name] -= item_data
            return True
        else:
            return False

    def sub(self, item):
        item_type = item.item_type
        if item_type not in self.items:
            return False
        if not self.items[item_type].has_amount(item.amount):
            return False
        self.items[item_type].remove(item.amount)
        return True

    def adds(self, items):
        items: Items
        for item_name, item in items:
            if item_name in self.items:
                self.items[item_name].add(item.amount)
            else:
                self.items[item_name] = item.copy()

    def add(self, item: Item):
        item_type = item.item_type
        if item_type in self.items:
            self.items[item_type].add(item.amount)
        else:
            self.items[item_type] = item.copy()

    def __mul__(self, other: float):
        new_items = {}
        for item_name, item in self.items.items():
            item: Item
            new_items[item_name] = item * other
        return Items(items=new_items)

    def serialize_dynamic(self):
        return [item_data.serialize() for item_data in self.items.values()]

    def serialize_static(self):
        return [item_data.serialize() for item_data in self.items.values()]

    @classmethod
    def from_dict(cls, data: dict):
        items_converted = {item_data["type"]: Item.from_dict(item_data) for item_data in data}
        return cls(items=items_converted)
