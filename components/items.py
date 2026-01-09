from components.item import Item


class Items:
    def __init__(self, items: dict[str, Item]):
        self.items: dict[str, Item] = items

    def __iter__(self):
        return iter(self.items.items())

    def can_buy(self, cost: dict[str, Item]):
        for item_name, item_data in cost.items():
            value = item_data.amount
            if value == 0:
                continue
            if item_name in self.items:
                if not self.items[item_name].has_amount(value):
                    return False
        return True

    def try_buy(self, cost: dict[str, Item]):
        if self.can_buy(cost):
            for item_name, item_data in cost.items():
                value = item_data.amount
                if value == 0:
                    continue
                if item_name in self.items:
                    self.items[item_name] -= item_data
            return True
        else:
            return False

    def add(self, item: Item):
        item_type = item.item_type
        if item_type in self.items:
            self.items[item_type] += item
        else:
            self.items[item_type] = item

    def __mul__(self, other: float):
        new_items = {}
        for item_name, item in self.items.values():
            item: Item
            new_items[item_name] = item * other
        return Items(items=new_items)

    def serialize_for_save(self):
        return self.serialize()

    def serialize(self):
        return {
            "items": {item_type: item_data.serialize() for item_type, item_data in self.items.items()}
        }

    @classmethod
    def from_dict(cls, data: dict):
        items_converted = {item_data["type"]: Item.from_dict(item_data) for item_data in data["items"]}
        return cls(items=items_converted)
