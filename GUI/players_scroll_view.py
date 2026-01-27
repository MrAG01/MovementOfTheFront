import arcade
from arcade.gui import UIAnchorLayout, UILabel, UIBoxLayout

from GUI.ui_color_rect import UIColorRect
from GUI.ui_scroll_view import UIScrollView


class PlayerInfoPlateWidget(UIAnchorLayout):
    def __init__(self, resource_manager, on_kick_callback, on_ban_callback, do_buttons, player, ping):
        super().__init__(size_hint=(1, None), height=40)
        font = resource_manager.get_default_font()
        add_control_buttons = bool(on_kick_callback) and bool(on_ban_callback) and do_buttons
        player_name_label_size_x = 0.5 if add_control_buttons else 0.9
        self.player_name_label = UILabel(str(player), font_size=24, font_name=font, align="left",
                                         size_hint=(player_name_label_size_x, 1))
        self.ping_label = UILabel(str(ping), size_hint=(0.1, 1.0), font_size=24, font_name=font, align="right")

        self.add(UIColorRect(color=arcade.color.Color(30, 30, 30), size_hint=(1, 1)), anchor_x="center",
                 anchor_y="center")

        main_layout = UIBoxLayout(vertical=False, size_hint=(0.95, 0.95), space_between=40)

        main_layout.add(self.player_name_label, size_hint=(1, 1))

        if add_control_buttons:
            layout = UIBoxLayout(vertical=False, size_hint=(0.4, 0.9), space_between=10)
            kick_button = resource_manager.create_widget("kick_button")
            kick_button.set_callback(on_kick_callback)
            layout.add(kick_button)
            ban_button = resource_manager.create_widget("ban_button")
            ban_button.set_callback(on_ban_callback)
            layout.add(ban_button)
            main_layout.add(layout)

        main_layout.add(self.ping_label)

        self.add(main_layout, anchor_x="center",
                 anchor_y="center")

    @property
    def text(self):
        return self.player_name_label.text

    def update(self, ping):
        self.ping_label.text = str(ping)


class PlayersScrollView(UIScrollView):
    def __init__(self, resource_manager, start_players, on_kick_callback, on_ban_callback, save_id, **kwargs):
        super().__init__(**kwargs)
        self.on_kick_callback = on_kick_callback
        self.on_ban_callback = on_ban_callback
        self.resource_manager = resource_manager
        self.players_info_widgets = {}
        self.save_id = save_id
        for player_data, ping in start_players:
            player_data = tuple(player_data)
            on_kick_cb = (lambda _, dta=player_data: on_kick_callback(dta)) if on_kick_callback else None
            on_ban_cb = (lambda _, dta=player_data: on_ban_callback(dta)) if on_ban_callback else None
            do_buttons = player_data[1] != save_id

            widget = PlayerInfoPlateWidget(resource_manager, on_kick_cb, on_ban_cb, do_buttons, player_data[0], ping)
            self.players_info_widgets[player_data] = widget
            self.add(widget)

    def update(self, data, save_id):
        self.save_id = save_id
        for player_data, ping in data:
            player_data = tuple(player_data)
            if player_data in self.players_info_widgets:
                self.players_info_widgets[player_data].update(ping)
            else:
                on_kick_cb = (lambda _, dta=player_data: self.on_kick_callback(dta)) if self.on_kick_callback else None
                on_ban_cb = (lambda _, dta=player_data: self.on_ban_callback(dta)) if self.on_kick_callback else None
                do_buttons = player_data[1] != self.save_id
                widget = PlayerInfoPlateWidget(self.resource_manager, on_kick_cb, on_ban_cb, do_buttons,
                                               player_data[0], ping)
                self.players_info_widgets[player_data] = widget
                self.add(widget)
