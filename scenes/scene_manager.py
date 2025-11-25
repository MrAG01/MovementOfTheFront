from scenes.base_scene import BaseScene


class SceneManager:
    def __init__(self):
        self.scenes = {}

        self.active_scene: BaseScene = None
        self.active_overlay_scene: BaseScene = None

    def add_scene(self, scene: BaseScene):
        if not isinstance(scene, BaseScene):
            raise ValueError(f"The BaseScene class was expected, and {type(scene).__name__} was met")

        name = scene.get_name()
        if name in self.scenes:
            raise ValueError("The scenes can't have the same names.")

        self.scenes[name] = scene

    def remove_scene(self, scene_name) -> bool:
        if not self.has_scene(scene_name):
            return False

        if self.active_scene and self.active_scene.get_name() == scene_name:
            self.active_scene = None
        elif self.active_overlay_scene and self.active_overlay_scene.get_name() == scene_name:
            self.active_overlay_scene = None

        if scene_name in self.scenes:
            del self.scenes[scene_name]

        return True

    def has_scene(self, scene_name) -> bool:
        return scene_name in self.scenes

    def use_scene(self, scene_name, overlay_mode=False):
        if scene_name in self.scenes:
            if overlay_mode:
                if self.active_overlay_scene and self.active_overlay_scene.get_name() != scene_name:
                    self.active_overlay_scene.on_exit()
                self.active_overlay_scene = self.scenes[scene_name]
                self.active_overlay_scene.on_enter()
            else:
                if self.active_scene and self.active_scene.get_name() != scene_name:
                    self.active_scene.on_exit()
                self.active_scene = self.scenes[scene_name]
                self.active_scene.on_enter()

    def use_scene_as_main(self, scene_name):
        self.use_scene(scene_name, overlay_mode=False)

    def use_scene_as_overlay(self, scene_name):
        self.use_scene(scene_name, overlay_mode=True)

    def draw_active_scene(self, window):
        if self.active_scene is not None:
            self.active_scene.draw(window)

    def draw_overlay_scene(self, window):
        if self.active_overlay_scene is not None:
            self.active_overlay_scene.draw(window)

    def update_active_scene(self, delta_time, window):
        if self.active_scene is not None:
            self.active_scene.update(delta_time, window)

    def update_overlay_scene(self, delta_time, window):
        if self.active_overlay_scene is not None:
            self.active_overlay_scene.update(delta_time, window)

    def on_update(self, delta_time, window):
        self.update_active_scene(delta_time, window)
        self.update_overlay_scene(delta_time, window)

    def draw(self, window):
        self.draw_active_scene(window)
        self.draw_overlay_scene(window)

    def on_shutdown(self):
        for scene in self.scenes.values():
            scene.on_shutdown()
