from arcade.gui import UIWidget, UILabel


class UIResourcePackWidget(UIWidget):
    def __init__(self, username, **kwargs):
        super().__init__(**kwargs)
        label = UILabel(username)
        self.add(label)
