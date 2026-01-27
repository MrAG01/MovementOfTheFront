import arcade
from arcade.gui import UIWidget, Surface
from arcade.types import AnchorPoint


class UIColorRect(UIWidget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.color = color

    def do_render(self, surface: Surface):
        arcade.draw_rect_filled(
            arcade.rect.XYWH(0, 0, self.width, self.height, AnchorPoint.BOTTOM_LEFT), self.color)
        super().do_render(surface)
