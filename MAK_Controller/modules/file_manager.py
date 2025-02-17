import os
from pathlib import Path 
import shutil
from datetime import datetime
from config import FOLDERS

def move_to_input(source_file: Path, overwrite: bool = False) -> None:
    target = FOLDERS["input"] / source_file.name
    
    if overwrite and target.exists():
        os.remove(target)  # Remove o antigo sem backup
        
    shutil.move(str(source_file), str(target))