import arcade
from utils.constants import RESOURCE_PACKS_PATH
from configs.config_manager import ConfigManager
from core.main_window import MainWindow
from resources.resource_manager import ResourceManager


class Application:
    def __init__(self):
        self.config_manager = ConfigManager("userdata")
        self.resource_manager = ResourceManager(self.config_manager, RESOURCE_PACKS_PATH)
        self.main_window = MainWindow(self.config_manager)

    def run(self):
        try:
            self.resource_manager.reload()
            arcade.run()
        finally:
            self.main_window.on_shutdown()
            self.config_manager.save("userdata")
