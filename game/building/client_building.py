from game.building.building_config import BuildingConfig
from game.building.building_state import BuildingState
from resources.handlers.texture_handle import TextureHandle
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from resources.mods.mods_manager.mods_manager import ModsManager
from arcade.math import lerp
from arcade import Vec2


class ClientBuilding:
    interpolation_speed = 1.0

    def __init__(self, server_snapshot: dict, resource_manager, mods_manager):
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager: ModsManager = mods_manager
        self.id = server_snapshot["id"]
        self.owner_id = server_snapshot["owner_id"]
        self.position = Vec2(*server_snapshot["position"])
        self._target_health = self.health = server_snapshot["health"]
        self.level = server_snapshot["level"]

        self.config: BuildingConfig = self.mods_manager.get_building(server_snapshot["config_name"])

        self.state = server_snapshot["state"]
        self.building_timer = server_snapshot["building_timer"]

        self.texture: TextureHandle = self.resource_manager.get_texture(self.config.texture_name)

        self._apply_events(server_snapshot["events"])

    def update_from_snapshot(self, snapshot):
        self._target_health = snapshot["health"]
        self.state = snapshot["state"]
        self.level = snapshot["level"]
        self.building_timer = snapshot["building_timer"]
        self._apply_events(snapshot["events"])

    def update_visual(self, delta_time):
        if self.health != self._target_health:
            self.health = lerp(self.health, self._target_health, min(self.interpolation_speed * delta_time, 1.0))

    def _apply_events(self, events: dict):
        pass

    def draw(self, camera):
        screen_pos, size = camera.world_to_screen(self.position)
        if self.state == BuildingState.IDLE:
            self.texture.draw(screen_pos.x, screen_pos.y)
        elif self.state == BuildingState.BUILDING:
            self.texture.draw(screen_pos.x, screen_pos.y,
                              alpha=255 * (1 - self.config.build_time / self.building_timer))
