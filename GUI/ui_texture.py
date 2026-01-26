import arcade
from arcade.gui import UIWidget, Surface


class UITexture(UIWidget):
    def __init__(self, *, texture, **kwargs):
        super().__init__(**kwargs)
        self._texture = texture

    def do_render(self, surface: Surface):
        super().do_render(surface)

        arcade.draw_texture_rect(
            texture=self._texture,
            rect=self.content_rect
        )
