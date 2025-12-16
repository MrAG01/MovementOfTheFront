import arcade
from arcade import Rect

from configs.base_config import BaseConfig
from resources.input.keyboard_manager import KeyboardManager


class CameraConfig(BaseConfig):
    width: int = 500
    min_zoom: float = 0.1
    max_zoom: float = 3.0
    zoom_speed: float = 0.1
    invert_x: bool = False
    invert_y: bool = False



class Camera:
    def __init__(self, config_manager, keyboard_manager, width, height):
        self.config_manager = config_manager
        self.keyboard_manager: KeyboardManager = keyboard_manager
        self.camera = arcade.Camera2D(
            viewport=arcade.rect.XYWH(0, 0, width, height),
            projection=arcade.rect.XYWH(0, 0, width, height)
        )

        self._position = arcade.Vec2(0, 0)

        self._zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 3.0
        self.zoom_speed = 0.1

        self.drag_start_point = None
        self.is_dragging = False
        self._setup_key_binds()

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("move_camera_left",
                                                on_holding_callback=self.move_left)
        self.keyboard_manager.register_callback("move_camera_right",
                                                on_holding_callback=self.move_right)
        self.keyboard_manager.register_callback("move_camera_up",
                                                on_holding_callback=self.move_up)
        self.keyboard_manager.register_callback("move_camera_down",
                                                on_holding_callback=self.move_down)

    def move_left(self):
        print("left")

    def move_right(self):
        print("right")

    def move_up(self):
        print("up")

    def move_down(self):
        print("down")

    def get_viewport_rect(self) -> Rect:
        return self.camera.viewport

    def _update_camera(self):
        width_ = self.camera.viewport_width / self._zoom
        height_ = self.camera.viewport_height / self._zoom
        l = self._position.x - width_ / 2
        r = self._position.x + width_ / 2
        b = self._position.y - height_ / 2
        t = self._position.y + height_ / 2
        self.camera.projection = arcade.rect.XYWH(l, r, b, t)

    def use(self):
        self.camera.use()

    def on_key_press(self):
        speed = 10.0 / self.camera.zoom
