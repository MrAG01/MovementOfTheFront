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

    def reset(self):
        if self.reset_on_replay:
            self.current_frame = 0


    def update(self, delta_time):
        frames_len = len(self.frames)
        self.flag_time_counter += delta_time
        if self.flag_time_counter >= self.frame_duration:
            self.current_frame += self.flag_time_counter // self.frame_duration
            if self.current_frame >= frames_len:
                if self.repeat:
                    self.current_frame %= frames_len
                else:
                    self.current_frame = frames_len - 1
