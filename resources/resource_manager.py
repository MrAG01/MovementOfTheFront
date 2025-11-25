import arcade


class ResourceManager:
    def __init__(self):
        self.available_resource_packs = set()

    def get_available_resource_packs(self):
        return self.available_resource_packs
