from logging_instance import customLogger
import logging
from config import settings
import sys
sys.path.append(settings.ROOT_ABSOLUTE_PATH)
from gui import Application
from auto_update import check_for_changes

logger = customLogger(logging.DEBUG, filename="logs/main.log")


if __name__ == "__main__":
    check_for_changes()
    app = Application()
    app.mostrar_alerta_actualizacion()
    app.mainloop() 
    