from coordinators.base_coordinator import BaseCoordinator


class MenuCoordinator(BaseCoordinator):
    def __init__(self, scene_manager, game_coordinator):
        super().__init__(scene_manager)
        self.game_coordinator = game_coordinator

    def _setup(self):
        pass

    def update(self, delta_time, window):
        pass
