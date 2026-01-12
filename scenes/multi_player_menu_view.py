from threading import Thread
import arcade
from GUI.ui_scroll_view import UIScrollView
from network.client.game_client import GameClient
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout, UILabel

from scenes.game_view import GameView
from scenes.join_server_password_view import JoinServerPasswordView
from scenes.room_client_menu_view import RoomClientMenuView


class UIServerTabletWidget(UIAnchorLayout):
    def __init__(self, resource_manager, server_data, size_hint, public_text, private_text, callback,
                 size=18):
        super().__init__(size_hint=size_hint)

        button = resource_manager.create_widget("server_tablet_button")
        button.on_click = lambda event: callback(server_data)
        layout = UIBoxLayout(size_hint=(1, 1), vertical=False)

        layout.add(UILabel(server_data["server_name"], size_hint=(0.5, 1), font_size=size), align="left")
        layout.add(UILabel(f"{server_data["players"]}/{int(server_data["max_players"])}", size_hint=(0.2, 1),
                           font_size=size),
                   align="right")
        layout.add(UILabel(private_text if server_data["has_password"] else public_text, size_hint=(0.3, 1),
                           font_size=size),
                   align="right")
        self.add(button, anchor_x="center", anchor_y="top")
        self.add(layout, anchor_x="center", anchor_y="top")


class ViewRoomsView(arcade.View):
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

    def _join_server(self, server_data):
        if server_data["has_password"]:
            self.view_setter(
                JoinServerPasswordView(self.resource_manager, self.mods_manager, self.view_setter, self, server_data,
                                       self.config_manager, self.keyboard_manager, self.mouse_manager))
        else:
            client = GameClient(self.config_manager, self.resource_manager, self.mods_manager, self.keyboard_manager,
                                self.mouse_manager)
            callback = client.connect(server_data["ip_address"], server_data["port"], None)
            if callback.is_success():
                self.view_setter(
                    RoomClientMenuView(self.view_setter, client, self, self.resource_manager, self.mods_manager,
                                       self.config_manager, self.keyboard_manager, self.mouse_manager))

    def _update_servers_list(self):
        servers_data = self.server_logger_manager.get_servers_list()
        if servers_data["success"]:
            public_text = self.resource_manager.get_located_text("public_server_text", "gui")
            private_text = self.resource_manager.get_located_text("private_server_text", "gui")

            def update_ui(_dt):
                self.servers_scroll_list.clear()
                for server_ip, server_data in servers_data["data"].items():
                    self.servers_scroll_list.add(
                        UIServerTabletWidget(self.resource_manager, server_data, (1, 1), public_text,
                                             private_text, self._join_server),
                        align="top"
                    )

            arcade.schedule_once(update_ui, 0)

    def _on_refresh_button_clicked_(self, event):
        thread = Thread(target=self._update_servers_list)
        thread.start()

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        refresh_button = self.resource_manager.create_widget("refresh_button")
        refresh_button.on_click = self._on_refresh_button_clicked_

        background_widget = self.resource_manager.create_widget("main_menu_background")
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.5))

        self.servers_scroll_list = UIScrollView(size_hint=(1, 1), vertical=True, scroll_speed=5)

        layout2 = UIBoxLayout(vertical=False, align="center", space_between=10, size_hint=(1, 0.2))
        layout.add(self.servers_scroll_list)
        layout2.add(back_button)
        layout2.add(refresh_button)
        layout.add(layout2)

        anchor = UIAnchorLayout()
        anchor.add(child=background_widget, anchor_x="center_x", anchor_y="center_y")
        anchor.add(child=layout, anchor_x="center_x", anchor_y="center_y")

        self.ui_manager.add(anchor)
        self._update_servers_list()

    def on_show_view(self) -> None:
        self.setup_gui()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
