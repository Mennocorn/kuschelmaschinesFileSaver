import os
import datetime


class Logger:
    def __init__(self):
        if not os.path.exists(".\\logger"):
            os.mkdir(".\\logger")
        self.debug_path = ".\\logger\\debug.txt"
        self.error_path = ".\\logger\\error.txt"

    def debug(self, reason: str = "No Reason", check: str = "No Check"):
        with open(self.debug_path, "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%d.%M.%Y %H:%M:%S')}\n{reason}\n{check}\n")
            f.close()

    def error(self, exception: Exception):
        with open(self.error_path, "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%d.%M.%Y %H:%M:%S')}\n{exception.__traceback__}\n")
            f.close()