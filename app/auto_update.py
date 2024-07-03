from config import settings
import requests
import git
import os
import subprocess
from logging_instance import customLogger

GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/commits"
REPO_URL = "https://github.com/{owner}/{repo}.git"
LOCAL_REPO_PATH = "./"
GH_OWNER=settings.GH_OWNER
REPO=settings.REPO
BRANCH=settings.BRANCH

logger =customLogger()
def get_latest_commit():
    response = requests.get(GITHUB_API_URL.format(owner=GH_OWNER, repo=REPO))
    response.raise_for_status()  # Verifica si la solicitud tuvo éxito
    latest_commit = response.json()[0]['sha']
    return latest_commit

# Función para obtener el último commit del repositorio local
def get_local_commit(repo_path):
    repo = git.Repo(repo_path)
    return repo.head.commit.hexsha

# Función para clonar o actualizar el repositorio
def update_repo(repo_url=REPO_URL.format(owner=GH_OWNER, repo=REPO), repo_path=LOCAL_REPO_PATH):
    try:
        if os.path.exists(repo_path):
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            
            logger.info("Repositorio actualizado exitosamente")
        else:
            git.Repo.clone_from(repo_url, repo_path)
    except git.exc.GitCommandError as e:
        logger.info(f"Error al actualizar el repositorio: {e}")
    except Exception as e:
        logger.info(f"Error desconocido al actualizar el repositorio: {e}")

def repo_has_changes():
    try:
        latest_remote_commit = get_latest_commit()
        local_commit = get_local_commit(LOCAL_REPO_PATH)

        if latest_remote_commit != local_commit:
            logger.info("Se ha detectado una nueva versión del proyecto")
            return True
        else:
            return False
    except Exception as e:
        logger.info(f"Error al VERIFICAR la version: {e}")
        return False

def build_application():
    try:
        logger.info("Reconstruyendo la aplicación...")
        # Ejecutar el comando de PyInstaller
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--add-data", "favicon.ico;.",
            "--icon=assets/favicon.ico",
            "app/main.py",
            "--collect-data", "sv_ttk",
            "--hidden-import=sv_ttk"
        ], check=True)
        logger.info("Aplicación descargada e instalada exitosamente.")
    except subprocess.CalledProcessError as e:
        logger.info(f"Error al reconstruir la aplicación: {e}")
    except Exception as e:
        logger.info(f"Error desconocido al reconstruir la aplicación: {e}")


def update():
    try:
        logger.info("Actualizando a la última versión...")
        update_repo(REPO_URL.format(owner=GH_OWNER, repo=REPO), LOCAL_REPO_PATH)
        logger.info("Proyecto descargado")
        build_application()
    except Exception as e:
        logger.info(f"Error al ACTUALIZAR el proyecto: {e}")