from threading import Thread
import arcade
from GUI.ui_scroll_view import UIScrollView
from GUI.ui_title_setter_layout import UITitleSetterLayout
from network.client.game_client import GameClient
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from arcade.gui import UIManager, UIBoxLayout, UIAnchorLayout, UILabel
from scenes.join_server_password_view import JoinServerPasswordView
from scenes.room_client_menu_view import RoomClientMenuView


class UIServerTabletWidget(UIAnchorLayout):
    def __init__(self, resource_manager, server_data, public_text, private_text, callback,
                 size=18):
        super().__init__(size_hint=(1, None), height=30)

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


class JoinByIpView(arcade.View):
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

    def _on_join_button_clicked_(self, event):
        self.error_label.text = ""

        ip = self.ip_input.text
        port = int(self.port_input.text)

        if not JoinByIpView.is_valid_ip(ip):
            self.error_label.text = "Ip is not valid"
            return
        self._join_server({
            "ip_address": ip,
            "port": port
        })

    def _join_server(self, server_data):
        client = GameClient(self.config_manager, self.resource_manager, self.mods_manager, self.keyboard_manager,
                            self.mouse_manager)
        callback = client.connect(server_data["ip_address"], server_data["port"], None)
        #print(callback)
        if callback.is_success():
            self.view_setter(
                RoomClientMenuView(self.view_setter, client, self.main_menu_view, self.resource_manager,
                                   self.mods_manager,
                                   self.config_manager, self.keyboard_manager, self.mouse_manager))

    @staticmethod
    def is_valid_ip(ip):
        return len(ip.split(".")) == 4

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        self.error_label = UILabel("", font_name=self.resource_manager.get_default_font(),
                                   font_size=16, text_color=arcade.color.Color(255, 0, 0),
                                   size_hint=(1, 0.2))

        self.ip_input = self.resource_manager.create_widget("ip_input")
        self.ip_input.text = "127.0.0.1"

        self.port_input = self.resource_manager.create_widget("port_input")
        self.port_input.text = "11111"

        back_button = self.resource_manager.create_widget("back_button")
        back_button.on_click = self._on_back_button_clicked_

        join_button = self.resource_manager.create_widget("join_button")
        join_button.on_click = self._on_join_button_clicked_

        background_widget = self.resource_manager.create_widget("main_menu_background")

        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.9, 0.7))
        layout = UIBoxLayout(vertical=True, align="center", space_between=10, size_hint=(0.7, 0.5))

        self.servers_scroll_list = UIScrollView(size_hint=(1, 1), vertical=True, scroll_speed=16)

        layout.add(self.error_label)
        layout.add(UITitleSetterLayout(self.resource_manager.create_widget("ip_input_helper_label"),
                                       self.ip_input, vertical=False, size_hint=(1, 0.2)))
        layout.add(UITitleSetterLayout(self.resource_manager.create_widget("port_input_helper_label"),
                                       self.port_input, vertical=False, size_hint=(1, 0.2)))
        layout2 = UIBoxLayout(vertical=False, space_between=10, size_hint=(1, 0.2))
        layout2.add(back_button)
        layout2.add(join_button)
        layout.add(layout2)

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
