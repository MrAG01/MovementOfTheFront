import arcade

from components.animation import Animation
from components.building.building_config import BuildingConfig
from resources.resource_manager import ResourceManager


class BuildingAnimation:
    def __init__(self, resource_manager, animation_name):
        self.base_animation: Animation = resource_manager.get_animation(animation_name)

    def update(self, delta_time):
        self.base_animation.update(delta_time)

    def get(self):
        return self.base_animation.get()


class Building:
    def __init__(self, resource_manager: ResourceManager, building_config):
        self.config: BuildingConfig = building_config
        self.building_animation = BuildingAnimation(resource_manager, self.config.building_animation_name)

    def update(self, delta_time):
        self.building_animation.update(delta_time)

    def draw(self):
        sp = arcade.Sprite(self.building_animation.get())
        sp.center_x = 100
        sp.center_y = 100
        arcade.draw_sprite(sp)
