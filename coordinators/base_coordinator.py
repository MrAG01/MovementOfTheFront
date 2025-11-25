class BaseCoordinator:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self._setup()

    def _setup(self):
        pass

    def update(self, delta_time, window):
        pass