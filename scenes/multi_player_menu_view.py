import arcade
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout

from scenes.join_by_ip_view import JoinByIpView
from scenes.view_rooms_view import ViewRoomsView


class MultiplayerMenuView(arcade.View):
    def __init__(self, view_setter, main_menu_view, resource_manager, mods_manager,
                 server_logger_manager, config_manager, keyboard_manager, mouse_manager):
        super().__init__()
        self.view_setter = view_setter
        self.main_menu_view = main_menu_view
        self.resource_manager: ResourceManager = resource_manager
        self.mods_manager = mods_manager
        self.server_logger_manager = server_logger_manager
        self.config_manager = config_manager
        self.keyboard_manager = keyboard_manager
        self.mouse_manager = mouse_manager
        self.ui_manager = UIManager()

    def _on_back_button_clicked_(self, event):
        self.view_setter(self.main_menu_view)

    def _join_by_ip_button_clicked_(self, event):
        self.view_setter(JoinByIpView(self.view_setter, self, self.resource_manager, self.mods_manager,
                                      self.server_logger_manager, self.config_manager, self.keyboard_manager,
                                      self.mouse_manager))

    def _on_view_rooms_list_button_clicked_(self, event):
        self.view_setter(ViewRoomsView(self.view_setter, self, self.resource_manager, self.mods_manager,
                                       self.server_logger_manager, self.config_manager, self.keyboard_manager,
                                       self.mouse_manager))

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        join_by_ip_button = self.resource_manager.create_widget("join_by_ip_button")
        join_by_ip_button.on_click = self._join_by_ip_button_clicked_

        view_rooms_list_button = self.resource_manager.create_widget("view_server_list")
        view_rooms_list_button.on_click = self._on_view_rooms_list_button_clicked_

        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.9, 0.7))
        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.3))

        layout.add(join_by_ip_button)
        layout.add(view_rooms_list_button)
        layout.add(back_button)

        anchor = UIAnchorLayout()
        anchor.add(child=background_widget, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=menu_background, anchor_x="center_x", anchor_y="center_y")
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
