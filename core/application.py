import arcade
from utils.constants import RESOURCE_PACKS_PATH, DEFAULT_MODE_PATH, MODS_PATH
from configs.config_manager import ConfigManager
from core.main_window import MainWindow
from resources.resource_manager import ResourceManager
from resources.mods_manager import ModsManager


class Application:
    def __init__(self):
        self.config_manager = ConfigManager("userdata")
        self.resource_manager = ResourceManager(self.config_manager, RESOURCE_PACKS_PATH)
        self.mods_manager = ModsManager(self.config_manager, DEFAULT_MODE_PATH, MODS_PATH)
        self.resource_manager.use_resource_pack("Movement of the front default pack")
        self.main_window = MainWindow(self.resource_manager, self.config_manager)

    def run(self):
        try:

            arcade.run()
        finally:
            self.main_window.on_shutdown()
            self.config_manager.save("userdata")
