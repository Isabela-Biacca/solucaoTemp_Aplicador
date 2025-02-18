import os
from pathlib import Path 
import shutil
from config import FOLDERS
from modules.xml_processor import get_production_order

def move_to_input(source_file: Path, overwrite: bool = False) -> None:
    try:
        # Obter dados da nova ordem
        new_op, new_creation_date, _, _ = get_production_order(source_file)
        
        target_dir = FOLDERS["input"]
        files_to_remove = []
        latest_existing_date = None

        # Procurar arquivos da mesma ordem no input
        for existing_file in target_dir.glob("MAK165*.xml"):
            try:
                existing_op, existing_date, _, _ = get_production_order(existing_file)
                
                if existing_op == new_op:
                    # Manter registro do arquivo mais recente
                    if not latest_existing_date or existing_date > latest_existing_date:
                        latest_existing_date = existing_date
                    
                    files_to_remove.append(existing_file)
                    
            except Exception as e:
                print(f"Erro ao processar {existing_file.name}: {str(e)}")
                continue

        # Validar se a nova versão é mais recente
        if latest_existing_date and new_creation_date <= latest_existing_date:
            print(f"Ordem {new_op} ignorada. Versão mais recente já existe ({latest_existing_date})")
            source_file.unlink()  # Remove o arquivo da waiting
            return

        # Remover versões antigas se for mais recente
        if overwrite and files_to_remove:
            for file in files_to_remove:
                try:
                    file.unlink()
                    print(f"Arquivo antigo removido: {file.name}")
                except Exception as e:
                    print(f"Falha ao remover {file.name}: {str(e)}")

        # Mover o novo arquivo
        target = target_dir / source_file.name
        shutil.move(str(source_file), str(target))
        print(f"Arquivo {source_file.name} movido com sucesso!")

    except Exception as e:
        print(f"Falha crítica ao processar {source_file.name}: {str(e)}")
        raise