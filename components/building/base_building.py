from multiprocessing.dummy import current_process

import arcade
from components.animation import Animation
from components.building.building_config import BuildingConfig
from resources.resource_manager import ResourceManager


class BuildingAnimation(Animation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_very_first_appearance = True
        self.first_frame_start_time = 0.0

    def reset(self):
        super().reset()
        self.is_very_first_appearance = True
        self.first_frame_start_time = 0.0

    def update(self, delta_time):
        old_frame = int(self.current_frame)
        super().update(delta_time)
        if self.is_very_first_appearance and old_frame == 0 and int(self.current_frame) != 0:
            self.is_very_first_appearance = False
            self.current_frame = 0

    def draw(self, x, y, scale=2.0):
        current_index = int(self.current_frame)
        next_index = (current_index + 1) % len(self.frames)
        progress = self.flag_time_counter / self.frame_duration
        current_texture = self.frames[current_index]
        next_texture = self.frames[next_index]

        if self.is_very_first_appearance and current_index == 0:
            current_texture.draw(x, y, scale, scale, alpha=int(255 * progress), pixelated=True)
            return
        if progress >= 0:
            current_texture.draw(x, y, scale, scale, pixelated=True)
        if progress <= 1:
            next_texture.draw(x, y, scale, scale, alpha=int(255 * progress), pixelated=True)


class Building:
    def __init__(self, resource_manager: ResourceManager, building_config):
        self.config: BuildingConfig = building_config
        self.building_base_texture = resource_manager.get_texture(self.config.base_texture_name)
        self.building_texture = resource_manager.get_texture(self.config.texture_name)

        self.building_animation = resource_manager.get_animation(self.config.building_animation_name,
                                                                 _class=BuildingAnimation,
                                                                 animation_fps=5,
                                                                 repeat=False)

        self.building = True

    def on_building_end(self):
        pass

    def update(self, delta_time):
        self.building_animation.update(delta_time)

    def draw(self):
        self.building_base_texture.draw(300, 300, 2, 2)
        self.building_animation.draw(300, 300)
