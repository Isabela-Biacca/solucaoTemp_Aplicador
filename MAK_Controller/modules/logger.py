from datetime import datetime
from pathlib import Path
from config import FOLDERS

def log(message: str):
    """Log principal com arquivos diários"""
    try:
        today = datetime.today()
        log_dir = FOLDERS["logs"] / str(today.year) / f"{today.month:02d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{today.date().isoformat()}.log"
        
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Falha crítica no logging: {str(e)}")

def log_alert(message: str):
    """Log de alertas críticos"""
    try:
        Path("alerts.log").touch(exist_ok=True)
        with open("alerts.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] ALERTA: {message}\n")
    except Exception as e:
        print(f"Falha no log de alertas: {str(e)}")