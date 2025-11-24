from configs.config_manager import ConfigManager
from core.main_window import MainWindow


class Application:
    def __init__(self):
        self.config_manager = ConfigManager("userdata/")

        self.main_window = MainWindow()

    def setup(self):
        pass

    def run(self):
        pass