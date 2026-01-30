import arcade
from arcade.gui import UIWidget, Surface
from arcade.types import AnchorPoint


class UITexture(UIWidget):
    def __init__(self, *, texture, **kwargs):
        super().__init__(**kwargs)
        self._texture = texture

    def do_render(self, surface: Surface):
        arcade.draw_texture_rect(
            texture=self._texture,
            rect=arcade.rect.XYWH(0, 0, self.width, self.height, AnchorPoint.BOTTOM_LEFT)
        )
