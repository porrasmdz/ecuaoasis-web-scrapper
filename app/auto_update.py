from config import settings
import requests
import git
import os

GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/commits"
REPO_URL = "https://github.com/{owner}/{repo}.git"
LOCAL_REPO_PATH = "./"
GH_OWNER=settings.GH_OWNER
REPO=settings.REPO
BRANCH=settings.BRANCH

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
def update_repo(repo_url, repo_path):
    if os.path.exists(repo_path):
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin
        origin.pull()
    else:
        git.Repo.clone_from(repo_url, repo_path)

def check_for_changes():
    try:
        latest_remote_commit = get_latest_commit()
        local_commit = get_local_commit(LOCAL_REPO_PATH)

        if latest_remote_commit != local_commit:
            print("El repositorio ha cambiado. Actualizando...")
            update_repo(REPO_URL.format(owner=GH_OWNER, repo=REPO), LOCAL_REPO_PATH)
        else:
            print("El repositorio está actualizado.")
    except Exception as e:
        print(f"Error al verificar o actualizar el repositorio: {e}")