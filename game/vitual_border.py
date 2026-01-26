import arcade
from arcade.gui import Surface


class VirtualBorder:
    def __init__(self, width, height, x=0, y=0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.surface = None
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return

        window = arcade.get_window()
        if not window:
            raise RuntimeError("Arcade window not available")

        self.surface = Surface(
            size=(self.width, self.height),
            position=(self.x, self.y),
            pixel_ratio=1.0
        )

        self._initialized = True

    def clear(self, color=arcade.color.Color(0, 0, 0, 0)):
        if not self._initialized:
            self._initialize()

        with self.surface.activate():
            self.surface.clear(color)

    def draw_unit_field_of_view(self, field_of_view, x, y, color):
        if not self._initialized:
            self._initialize()

        with self.surface.activate():
            arcade.draw_circle_filled(x, y, field_of_view, color)

    def draw(self):
        if not self._initialized:
            self._initialize()

        if self.surface:
            self.surface.draw()