from typing import Iterable

import arcade
from arcade.gui import UIWidget, Surface
from arcade.types import AnchorPoint


class UIProgressBar(UIWidget):
    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: float = 100,
                 height: float = 100,
                 children: Iterable[UIWidget] = tuple(),
                 size_hint: tuple[float | None, float | None] | None = None,
                 size_hint_min: tuple[float | None, float | None] | None = None,
                 size_hint_max: tuple[float | None, float | None] | None = None,
                 bg_color=(100, 100, 100),
                 border_color=(0, 0, 0),
                 border_size=2,
                 bar_color=(255, 0, 0),
                 state=0):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            children=children,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_size = border_size
        self.bar_color = bar_color
        self.state = state

    def set_state(self, state):
        self.state = state

    def do_render(self, surface: Surface):
        x, y = self.position
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, self.width - x * 2, self.height - y * 2, AnchorPoint.BOTTOM_LEFT), self.border_color)
        #print(self.state)
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + self.border_size,
                             y + self.border_size,
                             self.width - x * 2 - self.border_size * 2,
                             self.height - y * 2 - self.border_size * 2,
                             AnchorPoint.BOTTOM_LEFT), self.bg_color)
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + self.border_size,
                             y + self.border_size,
                             (self.width - x * 2 - self.border_size * 2) * self.state,
                             self.height - y * 2 - self.border_size * 2,
                             AnchorPoint.BOTTOM_LEFT), self.bar_color)
        super().do_render(surface)