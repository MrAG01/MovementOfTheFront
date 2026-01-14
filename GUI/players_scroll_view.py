import arcade
from arcade.gui import UIAnchorLayout, UILabel

from GUI.ui_color_rect import UIColorRect
from GUI.ui_scroll_view import UIScrollView


class PlayerInfoPlateWidget(UIAnchorLayout):
    def __init__(self, player, ping):
        super().__init__(size_hint=(1, None), height=30)
        self.player_name_label = UILabel(str(player), font_size=18)
        self.ping_label = UILabel(str(ping), font_size=18)

        self.add(UIColorRect(color=arcade.color.Color(30, 30, 30), size_hint=(1, 1)), anchor_x="center",
                 anchor_y="center")
        self.add(self.player_name_label, anchor_x="left", anchor_y="center")
        self.add(self.ping_label, anchor_x="right", anchor_y="center")

    @property
    def text(self):
        return self.player_name_label.text

    def update(self, ping):
        self.ping_label.text = str(ping)


class PlayersScrollView(UIScrollView):
    def __init__(self, start_players, **kwargs):
        super().__init__(**kwargs)
        self.players_info_widgets = {}
        for player_data, ping in start_players:
            player_data = tuple(player_data)
            widget = PlayerInfoPlateWidget(player_data[0], ping)
            self.players_info_widgets[player_data] = widget
            self.add(widget)

    def update(self, data):
        for player_data, ping in data:
            player_data = tuple(player_data)
            if player_data in self.players_info_widgets:
                self.players_info_widgets[player_data].update(ping)
            else:
                widget = PlayerInfoPlateWidget(player_data[0], ping)
                self.players_info_widgets[player_data] = widget
                self.add(widget)

