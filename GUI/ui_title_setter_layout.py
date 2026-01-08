from arcade.gui import UIBoxLayout, UIWidget, UILabel


class UITitleSetterLayout(UIBoxLayout):
    def __init__(self, title: UIWidget, setter: UIWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().add(title)
        super().add(setter)

    def add(self, *args, **kwargs):
        raise TypeError("Adding elements to UITitleSetterLayout is not allowed")

    @classmethod
    def label_as_title(cls, title: str, setter: UIWidget, *args, **kwargs):
        return cls(UILabel(title), setter, *args, **kwargs)
