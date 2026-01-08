from arcade.gui import UIBoxLayout
from arcade.gui.experimental import UIScrollArea
from arcade.gui.experimental.scroll_area import UIScrollBar


class UIScrollView(UIScrollArea):
    def __init__(
            self,
            x: float = 0,
            y: float = 0,
            width: float = 300,
            height: float = 300,
            overscroll_x: bool = False,
            overscroll_y: bool = False,
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            invert_scroll: bool = True,
            scroll_speed: float = 3.8,
            vertical=True,
            **kwargs
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            children=[],
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            overscroll_x=overscroll_x,
            overscroll_y=overscroll_y,
            **kwargs)
        self.scroll_speed = scroll_speed
        self.invert_scroll = invert_scroll

        self.main_layout = UIBoxLayout(vertical=False, size_hint=(1, 1))
        self.content_layout = UIBoxLayout(vertical=True, size_hint=(1, 1))

        self.main_layout.add(self.content_layout)
        self.main_layout.add(UIScrollBar(self, vertical))

        super().add(self.main_layout)

    def clear(self):
        self.content_layout.clear()

    def add(self, child, **kwargs):
        self.content_layout.add(child)
