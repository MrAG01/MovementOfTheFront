from resources.handlers.texture_handle import TextureHandle


class Animation:
    def __init__(self, frames: list[TextureHandle], animation_fps, repeat=False, reset_on_replay=True):
        self.frames = frames
        self.animation_fps = animation_fps
        self.repeat = repeat
        self.reset_on_replay = reset_on_replay

        self.current_frame = 0
        self.flag_time_counter = 0.0
        self.frame_duration = 1 / self.animation_fps

        self.on_finished_callback = None

    def set_on_finished_callback(self, on_finished_callback):
        self.on_finished_callback = on_finished_callback

    def reset(self):
        if self.reset_on_replay:
            self.current_frame = 0
            self.flag_time_counter = 0.0

    def is_finished(self):
        return not self.repeat and self.current_frame >= len(self.frames) - 1

    def set_fps(self, fps):
        self.animation_fps = fps
        self.frame_duration = 1 / self.animation_fps

    def _try_to_send_callback(self):
        if self.on_finished_callback is not None:
            self.on_finished_callback(self)

    def update(self, delta_time):
        frames_len = len(self.frames)
        if frames_len == 0:
            return

        self.flag_time_counter += delta_time

        if self.flag_time_counter >= self.frame_duration:
            self.current_frame += self.flag_time_counter // self.frame_duration
            if self.current_frame >= frames_len:
                if self.repeat:
                    self.current_frame %= frames_len
                else:
                    self.current_frame = frames_len - 1
            if self.is_finished():
                self._try_to_send_callback()

    def get(self):
        return self.frames[self.current_frame].get()
