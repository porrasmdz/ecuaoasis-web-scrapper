from logging_instance import customLogger
import logging
from config import settings
import sys
sys.path.append(settings.ROOT_ABSOLUTE_PATH)
from gui import Application

logger = customLogger(logging.DEBUG, filename="logs/main.log")


if __name__ == "__main__":
    app = Application()
    app.mainloop() 
    