import time


def time_counter(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        dt = end_time - start_time
        if dt:
            print(f"TIME: {dt:.4f}, MAX FPS: {1 / dt:.1f}")
        else:
            print("TIME: 0.0000, MAX FPS: 1000+")
        return ret
    return wrapper