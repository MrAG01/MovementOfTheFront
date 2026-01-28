from typing import Iterable

import arcade
from arcade.gui import UIWidget, Surface
from arcade.types import AnchorPoint


def draw_progress_bar(x, y, width, height, progress, border_size, border_color: arcade.color.Color, bg_color, bar_color,
                      alpha=255):
    border_color = border_color.rgb + (alpha,)
    bg_color = bg_color.rgb + (alpha,)
    bar_color = bar_color.rgb + (alpha,)

    arcade.draw_rect_filled(
        arcade.rect.XYWH(x, y, width, height, AnchorPoint.BOTTOM_LEFT), border_color)
    arcade.draw_rect_filled(
        arcade.rect.XYWH(x + border_size,
                         y + border_size,
                         width - border_size * 2,
                         height - border_size * 2,
                         AnchorPoint.BOTTOM_LEFT), bg_color)
    arcade.draw_rect_filled(
        arcade.rect.XYWH(x + border_size,
                         y + border_size,
                         (width - border_size * 2) * progress,
                         height - border_size * 2,
                         AnchorPoint.BOTTOM_LEFT), bar_color)


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
                 bg_color=arcade.color.Color(100, 100, 100),
                 border_color=arcade.color.Color(0, 0, 0),
                 border_size=2,
                 bar_color=arcade.color.Color(255, 0, 0),
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
        x = 0
        y = 0

        draw_progress_bar(
            x=x,
            y=y,
            width=self.width,
            height=self.height,
            progress=self.state,
            border_size=self.border_size,
            border_color=self.border_color,
            bg_color=self.bg_color,
            bar_color=self.bar_color
        )
