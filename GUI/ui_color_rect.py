import arcade
from arcade.gui import UIWidget, Surface
from arcade.types import AnchorPoint


class UIColorRect(UIWidget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.color = color

    def do_render(self, surface: Surface):
        x, y = self.position
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, self.width - x * 2, self.height - y * 2, AnchorPoint.BOTTOM_LEFT), self.color)
        super().do_render(surface)