from GUI.ui_progress_bar import draw_progress_bar


class UIObjectsProgressBar:
    def __init__(self, center_x, top_y, width, height, offset_height, bg_color, border_color, bar_color, **kwargs):
        super().__init__(**kwargs)
        self.current_time = 0
        self.finish_time = 0
        self.working = False
        self.offset_height = offset_height

        self.center_x = center_x
        self.top_y = top_y

        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.border_color = border_color
        self.bar_color = bar_color

    def set_state(self, time):
        self.current_time = time
        self.working = True

    def start(self, finish_time):
        self.working = True
        self.finish_time = finish_time
        self.current_time = 0

    def continue_(self):
        self.working = True

    def stop(self):
        self.working = False

    def on_update(self, dt):
        if self.working:
            self.current_time += dt
            if self.current_time >= self.finish_time:
                self.working = False

    def on_draw(self, camera, offset_y, alpha=255):
        if self.working:
            zoom_k = 1

            offset_height = self.offset_height - offset_y

            w, h = self.width * zoom_k, self.height * zoom_k
            x, y = self.center_x - w / 2, self.top_y - h + offset_height * zoom_k

            draw_progress_bar(x, y, w, h, self.current_time / self.finish_time, 2 * (1 / camera.zoom),
                              self.border_color,
                              self.bg_color, self.bar_color, alpha=alpha)
