import arcade
import pyglet.window.mouse

from configs.base_config import BaseConfig


class CameraConfig(BaseConfig):
    def __init__(self, width_k=1.0, height_k=1.0, camera_speed=300, drag_sensitivity=0.2, min_zoom=0.1, max_zoom=3.0,
                 zoom_speed=0.1, invert_x=False, invert_y=False):
        self.width_k: float = width_k
        self.height_k: float = height_k
        self.camera_speed: float = camera_speed
        self.drag_sensitivity: float = drag_sensitivity
        self.zoom_speed: float = zoom_speed
        self.invert_x: bool = invert_x
        self.invert_y: bool = invert_y

    def serialize(self):
        return {
            "width_k": self.width_k,
            "height_k": self.height_k,
            "camera_speed": self.camera_speed,
            "drag_sensitivity": self.drag_sensitivity,
            "zoom_speed": self.zoom_speed,
            "invert_x": self.invert_x,
            "invert_y": self.invert_y
        }


class Camera(arcade.Camera2D):
    def __init__(self, config_manager, keyboard_manager, mouse_manager):
        self.config = config_manager.register_config("camera_config", CameraConfig)
        window_config = config_manager.get_config("window_config")
        if window_config is not None:
            width, height = window_config.resolution
        else:
            width, height = 1920, 1080

        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager

        super().__init__(viewport=arcade.rect.LBWH(0, 0, width, height))

        self._zoom = 1.0
        self.position = arcade.Vec2(0, 0)
        self.delta_time = 0

        window_config.add_listener(self.on_window_config_changed, notify_immediately=False)
        self._setup_key_binds()
        self._update_projection()

    def _update_projection(self):
        width = self.viewport.width / self._zoom
        height = self.viewport.height / self._zoom
        self.projection = arcade.rect.LBWH(0, 0, width, height)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = max(0.1, value)
        self._update_projection()

    def on_window_config_changed(self, window_config):
        width, height = window_config.resolution
        self.viewport = arcade.rect.LBWH(0, 0, width, height)
        self._update_projection()
        self._clamp_to_borders()

    def _setup_key_binds(self):
        self.keyboard_manager.register_callback("move_camera_left",
                                                on_holding_callback=self.move_left)
        self.keyboard_manager.register_callback("move_camera_right",
                                                on_holding_callback=self.move_right)
        self.keyboard_manager.register_callback("move_camera_up",
                                                on_holding_callback=self.move_up)
        self.keyboard_manager.register_callback("move_camera_down",
                                                on_holding_callback=self.move_down)
        self.mouse_manager.register_on_scroll_callback(self._handle_mouse_scroll)
        self.mouse_manager.register_on_dragging_callback(self._handle_mouse_drag)

    def define_borders(self, width, height):
        self.border_width = width
        self.border_height = height
        self._clamp_to_borders()

    def _get_speed(self):
        return self.config.camera_speed / self._zoom

    def _move(self, arg: arcade.Vec2):
        self.position = self.position + arg
        self._clamp_to_borders()

    def move_left(self):
        direction = -1 * (-1 if self.config.invert_x else 1)
        self._move(arcade.Vec2(direction * self._get_speed() * self.delta_time, 0))

    def move_right(self):
        direction = 1 * (-1 if self.config.invert_x else 1)
        self._move(arcade.Vec2(direction * self._get_speed() * self.delta_time, 0))

    def move_up(self):
        direction = 1 * (-1 if self.config.invert_y else 1)
        self._move(arcade.Vec2(0, direction * self._get_speed() * self.delta_time))

    def move_down(self):
        direction = -1 * (-1 if self.config.invert_y else 1)
        self._move(arcade.Vec2(0, direction * self._get_speed() * self.delta_time))

    def _handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y == 0:
            return
        old_zoom = self._zoom
        new_zoom = self._zoom + scroll_y * self.config.zoom_speed
        if old_zoom == new_zoom:
            return
        old_mp = self.unproject(arcade.Vec2(x, y))
        self.zoom = new_zoom
        new_mp = self.unproject(arcade.Vec2(x, y))
        offset = new_mp - old_mp
        self._move(-arcade.Vec2(offset.x, offset.y))

    def _handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        direction_x = -1 * (-1 if self.config.invert_x else 1)
        direction_y = -1 * (-1 if self.config.invert_y else 1)
        if buttons & pyglet.window.mouse.LEFT:
            self._move(arcade.Vec2(
                x=direction_x * self._get_speed() * dx * self.delta_time * self.config.drag_sensitivity,
                y=direction_y * self._get_speed() * dy * self.delta_time * self.config.drag_sensitivity
            ))
        self._clamp_to_borders()

    def update(self, delta_time):
        self.delta_time = delta_time

    def _clamp_to_borders(self):
        if not (hasattr(self, 'border_width') and hasattr(self, 'border_height')):
            return

        min_zoom_x = self.viewport.width / self.border_width
        min_zoom_y = self.viewport.height / self.border_height
        min_zoom = max(min_zoom_x, min_zoom_y)

        if self._zoom < min_zoom:
            self.zoom = min_zoom

        min_x, min_y = 0, 0
        max_x, max_y = self.border_width, self.border_height

        cur_x, cur_y = self.position
        cur_w, cur_h = self.projection.width / self._zoom, self.projection.height / self._zoom

        if cur_x < min_x:
            new_x = min_x
        elif cur_x + cur_w > max_x:
            new_x = max_x - cur_w
        else:
            new_x = self.position.x

        if cur_y < min_y:
            new_y = min_y
        elif cur_y + cur_h > max_y:
            new_y = max_y - cur_h
        else:
            new_y = self.position.y

        self.position = (new_x, new_y)
