from components.items import Items


class ClientInventory:
    def __init__(self, snapshot):
        self.items: Items = Items.from_dict(snapshot["items"])
        self.productivity = snapshot["productivity"]

    def get_items(self):
        return self.items

    def update_from_snapshot(self, snapshot):
        self.items = Items.from_dict(snapshot["items"])
        self.productivity = snapshot["productivity"]
        #print(self.productivity)
