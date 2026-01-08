import arcade
from arcade.gui import UIManager, UIAnchorLayout

from GUI.ui_progress_bar import UIProgressBar
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class LoadingView(arcade.View):
    def __init__(self, resource_manager, view_setter, return_view, loading_progress_function, args=()):
        super().__init__()
        self.view_setter = view_setter
        self.return_view = return_view
        self.resource_manager: ResourceManager = resource_manager
        self.loading_progress_function = loading_progress_function
        self.args = args
        self.ui_manager = UIManager()
        self.check_progress()

    def check_progress(self):
        self.current_progress = self.loading_progress_function()
        if self.current_progress >= 1.0:
            self.view_setter(self.return_view(self.args))

    def setup_gui(self):
        self.ui_manager.clear()
        self.ui_manager.enable()

        self.progress_bar = UIProgressBar(size_hint=(1.0, 1.0))
        anchor = UIAnchorLayout(size_hint=(0.5, 0.1))
        anchor.add(self.progress_bar, anchor_x="center", anchor_y="center")

        self.ui_manager.add(anchor)

    def on_show_view(self) -> None:
        self.setup_gui()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
        self.check_progress()
        self.progress_bar.set_state(self.current_progress)
