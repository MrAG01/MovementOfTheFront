from core.application import Application
from lines_counter import count_lines

if __name__ == "__main__":
    count_lines()
    application = Application()
    application.run()


