import inspect


def function_observer(func):
    def wrapper(*args, **kwargs):
        stack = inspect.stack()
        caller_frame = stack[1]

        print(f"{func.__name__} вызвана из:")
        print(f"  Файл: {caller_frame.filename}")
        print(f"  Строка: {caller_frame.lineno}")
        print(f"  Функция: {caller_frame.function}")

        return func(*args, **kwargs)

    return wrapper
