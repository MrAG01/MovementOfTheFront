from arcade.gui import UIFlatButton, UIMouseReleaseEvent


class UISoundButton(UIFlatButton):
    def __init__(self, sound=None, **kwargs):
        super().__init__(**kwargs)
        self._sound = sound

        self._on_click_callback = None

    def on_click(self, event):
        if self._on_click_callback:
            self._sound.play()
            self._on_click_callback(event)

    def set_callback(self, callback):
        self._on_click_callback = callback
