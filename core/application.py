import arcade
from configs.config_manager import ConfigManager
from core.main_window import MainWindow


class Application:
    def __init__(self):
        self.config_manager = ConfigManager("userdata")
        self.main_window = MainWindow(self.config_manager)

    def run(self):
        try:
            arcade.run()
        finally:
            self.main_window.on_shutdown()
            self.config_manager.save("userdata")
