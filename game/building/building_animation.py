class BuildingAnimation:
    def __init__(self, delay, frame):
        self.frame_texture = frame
        self.delay = delay
        self.progress_time = 0
        self.finished = False

    def update(self, delta_time):
        if not self.finished:
            self.progress_time += delta_time
            if self.progress_time >= delta_time:
                self.finished = True

    def draw(self, x, y, scale=2.0):
        self.frame_texture.draw(x, y, scale, scale, alpha=int(255 * max(self.progress_time / self.delay, 1)),
                                pixelated=True)