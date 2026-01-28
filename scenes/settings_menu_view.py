import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UIInputText

from GUI.ui_scroll_view import UIScrollView
from GUI.ui_title_setter_layout import UITitleSetterLayout
from configs.config_manager import ConfigManager
from configs.window_config import WindowConfig
from network.userdata import UserData
from utils.os_utils import restart_self


class UISettingsMenu(arcade.View):
    def __init__(self, view_setter, back_menu, config_manager, resource_manager):
        super().__init__()
        self.view_setter = view_setter
        self.config_manager: ConfigManager = config_manager

        self.back_menu = back_menu

        self.window_config: WindowConfig = self.config_manager.register_config("window_config", WindowConfig)

        self.userdata_config: UserData = self.config_manager.register_config("userdata", UserData)

        self.resource_manager = resource_manager
        self.ui_manager = UIManager()

        self.temp_width = self.window_config.window_width
        self.temp_height = self.window_config.window_height
        self.temp_username = self.userdata_config.username
        self.temp_static_port = self.userdata_config.static_port

    def _on_back_button_pressed_(self, event):
        self.view_setter(self.back_menu)

    def _on_apply_button_pressed_(self, event):
        if self.temp_username != self.userdata_config.username:
            self.userdata_config.username = self.temp_username
        self.window_config.disable_notifications()
        if self.temp_width != self.window_config.window_width:
            self.window_config.set_width(int(self.temp_width))
        if self.temp_height != self.window_config.window_width:
            self.window_config.set_height(int(self.temp_height))
        self.window_config.enable_notifications()

        if self.temp_static_port != self.userdata_config.static_port:
            self.userdata_config.static_port = self.temp_static_port

    def on_window_config_changed(self, config: WindowConfig):
        self.temp_width = str(config.window_width)
        self.width_input.text = self.temp_width

        self.temp_height = str(config.window_height)
        self.height_input.text = self.temp_height

    def _on_username_input_change_(self, event):
        self.temp_username = self.username_input.text

    def _on_width_input_change(self, event):
        self.temp_width = str(self.width_input.text)

    def _on_height_input_change(self, event):
        self.temp_height = str(self.height_input.text)

    def _on_static_port_input_change_(self, event):
        text = str(self.static_port_input.text)
        self.temp_static_port = int(text) if text else None

    def setup_gui(self):
        self.ui_manager.enable()
        self.ui_manager.clear()

        background = self.resource_manager.create_widget("main_menu_background")
        menu_background = self.resource_manager.create_widget("menus_background", size_hint=(0.75, 0.75))
        main_anchor = UIAnchorLayout()

        menu_layout = UIBoxLayout(vertical=True, size_hint=(0.7, 0.7), space_between=10)
        secondary_background = self.resource_manager.create_widget("secondary_background")
        # menu_layout.add(secondary_background, anchor_x="center", anchor_y="bottom")

        main_scroll_layout = UIScrollView(size_hint=(1, 0.9), space_between=10)
        self.username_input: UIInputText = self.resource_manager.create_widget("username_input")
        self.username_input.text = self.userdata_config.username
        self.username_input.on_change = self._on_username_input_change_

        self.width_input = self.resource_manager.create_widget("screen_width_input")
        self.width_input.text = str(self.window_config.window_width)
        self.width_input.on_change = self._on_width_input_change

        self.height_input = self.resource_manager.create_widget("screen_height_input")
        self.height_input.text = str(self.window_config.window_height)
        self.height_input.on_change = self._on_height_input_change

        self.static_port_input = self.resource_manager.create_widget("static_port_input")
        cur = self.userdata_config.static_port
        self.static_port_input.text = str(cur) if cur else ""
        self.static_port_input.on_change = self._on_static_port_input_change_

        main_scroll_layout.add(UITitleSetterLayout(
            self.resource_manager.create_widget("username_input_helper_label"),
            self.username_input, vertical=False,
            size_hint=(0.95, None), height=50
        ))

        main_scroll_layout.add(UITitleSetterLayout(
            self.resource_manager.create_widget("screen_width_input_helper_label"),
            self.width_input, vertical=False,
            size_hint=(0.95, None), height=50
        ))

        main_scroll_layout.add(UITitleSetterLayout(
            self.resource_manager.create_widget("screen_height_input_helper_label"),
            self.height_input, vertical=False,
            size_hint=(0.95, None), height=50
        ))

        main_scroll_layout.add(UITitleSetterLayout(
            self.resource_manager.create_widget("static_port_input_helper_label"),
            self.static_port_input, vertical=False,
            size_hint=(0.95, None), height=50
        ))

        bottom_buttons = UIBoxLayout(vertical=False, space_between=10, size_hint=(1, 0.1))
        self.back_button = self.resource_manager.create_widget("back_button")
        self.back_button.set_callback(self._on_back_button_pressed_)

        self.apply_button = self.resource_manager.create_widget("apply_button")
        self.apply_button.set_callback(self._on_apply_button_pressed_)

        bottom_buttons.add(self.back_button)
        bottom_buttons.add(self.apply_button)

        menu_layout.add(main_scroll_layout)
        menu_layout.add(bottom_buttons)

        main_anchor.add(background)
        main_anchor.add(menu_background)
        main_anchor.add(menu_layout)

        self.ui_manager.add(main_anchor)

    def on_show_view(self) -> None:
        self.setup_gui()
        self.window_config.add_listener(self.on_window_config_changed, notify_immediately=False)

    def on_hide_view(self):
        self.ui_manager.disable()
        self.window_config.remove_listener(self.on_window_config_changed)

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_update(self, delta_time):
        self.ui_manager.on_update(delta_time)
