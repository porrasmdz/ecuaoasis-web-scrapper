from logging_instance import customLogger
import logging
from config import settings
import sys
sys.path.append(settings.ROOT_ABSOLUTE_PATH)
from gui import Application
from auto_update import repo_has_changes, update

logger = customLogger(logging.DEBUG, filename="logs/main.log")

APP_VERSION="1.0.2"

if __name__ == "__main__":
    has_changes = repo_has_changes()
    app = Application(version=APP_VERSION)
    if has_changes:
        update()
        app.mostrar_alerta_actualizacion()
    else:
        app.mostrar_alerta_generica(message="Usted tiene la última versión de esta aplicación.")
    app.mainloop() 
    
    

    