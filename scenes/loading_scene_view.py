import threading

import arcade
from arcade.gui import UIManager, UIAnchorLayout

from GUI.ui_progress_bar import UIProgressBar
from resources.resource_packs.resource_manager.resource_manager import ResourceManager


class LoadingView(arcade.View):
    def __init__(self, resource_manager, return_callback, loading_progress_function, args=()):
        super().__init__()
        self.return_callback = return_callback
        self.resource_manager: ResourceManager = resource_manager
        self.loading_progress_function = loading_progress_function
        self.args = args
        self.ui_manager = UIManager()

    def setup_gui(self):
        self.ui_manager.clear()
        self.ui_manager.enable()

        anchor = UIAnchorLayout()
        background_widget = self.resource_manager.create_widget("main_menu_background")
        self.progress_bar = UIProgressBar(size_hint=(0.7, 0.1))
        anchor.add(background_widget, anchor_x="center", anchor_y="center")
        anchor.add(self.progress_bar, anchor_x="center", anchor_y="center")

        self.ui_manager.add(anchor)

    def on_show_view(self) -> None:
        self.setup_gui()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.trigger_render()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.progress_bar.set_state(self.loading_progress_function())
        self.ui_manager.on_update(delta_time)
