class BaseScene:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def update(self, delta_time, window):
        pass

    def draw(self, window):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_shutdown(self):
        pass
