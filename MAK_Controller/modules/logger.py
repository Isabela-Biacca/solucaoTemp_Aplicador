import os
from datetime import datetime
from pathlib import Path
from config import FOLDERS

def setup_logger():
    today = datetime.date.today()
    log_dir = FOLDERS["logs"] / str(today.year) / f"{today.month:02d}"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{today.isoformat()}.log"
    
    # Se o arquivo de hoje já existe, usa-o. Senão, cria.
    return open(log_file, "a", encoding="utf-8")

def log(message: str):
    log_file = setup_logger()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"[{timestamp}] {message}\n")
    log_file.close()

def log(message):
    with open("application.log", "a") as log_file:
        log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def log_alert(message):
    with open("alerts.log", "a") as alert_file:
        alert_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")