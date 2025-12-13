import arcade
from arcade import Rect


class Camera:
    def __init__(self, width, height):
        self.camera = arcade.Camera2D(
            viewport=(0, 0, width, height),
            projection=(0, width, 0, height)
        )

        self._position = arcade.Vec2(0, 0)

        self._zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 3.0
        self.zoom_speed = 0.1

        self.drag_start_point = None
        self.is_dragging = False

    def get_viewport_rect(self) -> Rect:
        return self.camera.projection

    def _update_camera(self):
        width_ = self.camera.viewport_width / self._zoom
        height_ = self.camera.viewport_height / self._zoom
        l = self._position.x - width_ / 2
        r = self._position.x + width_ / 2
        b = self._position.y - height_ / 2
        t = self._position.y + height_ / 2
        self.camera.projection = (l, r, b, t)

    def use(self):
        self.camera.use()

    def on_key_press(self, key, modifiers):
        speed = 10.0 / self.camera.zoom
