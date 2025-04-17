from pathlib import Path

# Caminhos absolutos para suas pastas EXISTENTES
BASE_DIR = Path(__file__).parent.parent  # Sobe um nível para a raiz

FOLDERS = {
    "waiting": BASE_DIR / "waiting",     # Pasta waiting na raiz
    "input": BASE_DIR / "input",         # Pasta input na raiz
    "logs": BASE_DIR / "MAK_Controller/logs",        # Logs dentro da pasta app
    "backup": BASE_DIR.parent / "makBackup"  # Pasta makBackup fora do projeto

}

# Cria apenas a pasta de logs (as demais já existem)
FOLDERS["logs"].mkdir(exist_ok=True, parents=True)