import arcade

from configs.game_config import GameConfig
from game.game_manager import GameManager
from network.server_logger.server_logger_manager import ServerLoggerManager
from utils.constants import DEFAULT_RESOURCE_PACK, USER_DATA_PATH
from configs.config_manager import ConfigManager
from core.main_window import MainWindow
from resources.resource_packs.resource_manager.resource_manager import ResourceManager
from resources.mods.mods_manager.mods_manager import ModsManager


class Application:
    def __init__(self):
        self.config_manager = ConfigManager(USER_DATA_PATH)
        self.config_manager.register_config("game_config", GameConfig)

        self.resource_manager = ResourceManager(self.config_manager)
        self.mods_manager = ModsManager(self.config_manager)
        self.resource_manager.use_resource_pack(DEFAULT_RESOURCE_PACK)

        self.game_manager = GameManager(self.config_manager, self.resource_manager)
        self.server_logger_manager = ServerLoggerManager()
        self.main_window = MainWindow(self.resource_manager, self.mods_manager, self.game_manager, self.config_manager,
                                      self.server_logger_manager)

    def run(self):
        try:
            arcade.run()
        finally:
            self.config_manager.save_all()
