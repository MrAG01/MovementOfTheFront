import arcade
from arcade.gui import UIManager, UIAnchorLayout


class UISettingsMenu(arcade.View):
    def __init__(self, config_manager, resource_manager):
        super().__init__()
        self.config_manager = config_manager
        self.resource_manager = resource_manager
        self.ui_manager = UIManager()

    # def _set_width_button_pressed(self):

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        background = self.resource_manager.create_widget("main_menu_background")
        menu_background = self.resource_manager.create_widget("secondary_background")
        main_anchor = UIAnchorLayout()

        menu_anchor = UIAnchorLayout(size_hint=(0.8, 0.6))
        menu_anchor.add(menu_background)

        pass

        main_anchor.add(background)
        menu_anchor.add(menu_anchor)
        self.ui_manager.add(main_anchor)

    def on_show_view(self) -> None:
        self.setup_gui()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
