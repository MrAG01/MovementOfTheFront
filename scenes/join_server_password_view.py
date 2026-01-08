import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout

from GUI.ui_title_setter_layout import UITitleSetterLayout
from scenes.game_view import GameView


class JoinServerPasswordView(arcade.View):
    def __init__(self, resource_manager, game_manager, view_setter, back_menu, server_data,
                 config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.resource_manager = resource_manager
        self.game_manager = game_manager
        self.view_setter = view_setter
        self.back_menu = back_menu
        self.server_data = server_data
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.back_menu)

    def _on_join_button_clicked_(self, event):
        password = self.password_input.text
        callback = self.game_manager.connect_to_room(self.server_data["ip_address"], self.server_data["port"], password)
        print(callback)
        if callback.is_success():
            self.view_setter(GameView(self.view_setter, self.game_manager, self.back_menu, self.resource_manager,
                                      self.config_manager, self.keyboard_manager, self.mouse_manager))


    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        join_button = self.resource_manager.create_widget("password_input_join_button")
        join_button.on_click = self._on_join_button_clicked_

        self.password_input = self.resource_manager.create_widget("password_input")
        self.password_input.text = ""

        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.5))

        layout2 = UIBoxLayout(vertical=False, align="center", space_between=10, size_hint=(1, 0.2))
        layout2.add(back_button)
        layout2.add(join_button)
        layout.add(
            UITitleSetterLayout(self.resource_manager.create_widget("password_input_helper_label"),
                                self.password_input,
                                vertical=False, size_hint=(1, 1)))
        layout.add(layout2)

        anchor = UIAnchorLayout()
        anchor.add(child=background_widget, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=layout, anchor_x="center_x", anchor_y="center_y")

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
