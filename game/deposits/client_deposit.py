import arcade
from game.deposits.deposit_config import DepositConfig
from resources.mods.mods_manager.mods_manager import ModsManager
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class ClientDeposit(arcade.Sprite):
    def __init__(self, resource_manager, mods_manager, snapshot):
        super().__init__()

        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager: ModsManager = mods_manager
        self.deposit_id = snapshot["deposit_id"]

        self.config: DepositConfig = self.mods_manager.get_deposit(snapshot["deposit_config"])
        self.texture = self.resource_manager.get_texture(self.config.name).get()
        self.size = (7, 7)

        self.position = arcade.Vec2(*snapshot["position"])
        # self.deposit_capacity = snapshot["deposit_capacity"]
        self.deposit_max_capacity = snapshot["deposit_max_capacity"]

        self.owned_mine_id = snapshot["owned_mine_id"]

        self.on_move_callbacks = set()

    def _notify_on_move_callback_listeners(self):
        for callback in self.on_move_callbacks:
            callback(self)

    def append_on_move_callback(self, callback):
        self.on_move_callbacks.add(callback)

    def remove_on_move_callback(self, callback):
        if callback in self.on_move_callbacks:
            self.on_move_callbacks.remove(callback)

    def can_place_building_on(self, building_name):
        return building_name in self.config.product_buildings

    def has_owner(self):
        return self.owned_mine_id is not None

    def update_from_snapshot(self, snapshot):
        # self.deposit_capacity = snapshot["deposit_capacity"]
        self.owned_mine_id = snapshot["owned_mine_id"]

    # def draw(self, camera):
    #    zoom_k = 0.2
    #    # print(self.position.x, self.position.y)
    #    self.texture.draw(self.position.x, self.position.y, zoom_k, zoom_k)
