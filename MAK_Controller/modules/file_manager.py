from modules.xml_processor import get_production_order
from datetime import datetime
from config import FOLDERS
from pathlib import Path
from modules.logger import log
import shutil
import os

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
                log(f"Erro ao processar {existing_file.name}: {str(e)}")
                print(f"Erro ao processar {existing_file.name}: {str(e)}")
                continue

        # Validar se a nova versão é mais recente
        if latest_existing_date and new_creation_date <= latest_existing_date:
            log(f"Ordem {new_op} ignorada. Versão mais recente já existe ({latest_existing_date})")
            print(f"Ordem {new_op} ignorada. Versão mais recente já existe ({latest_existing_date})")
            source_file.unlink()  # Remove o arquivo da waiting
            return

        # Remover versões antigas se for mais recente
        if overwrite and files_to_remove:
            for file in files_to_remove:
                try:
                    file.unlink()
                    log(f"Arquivo antigo removido: {file.name}")
                    print(f"Arquivo antigo removido: {file.name}")
                except Exception as e:
                    log(f"Falha ao remover {file.name}: {str(e)}")
                    print(f"Falha ao remover {file.name}: {str(e)}")

        # Mover o novo arquivo
        target = target_dir / source_file.name
        shutil.move(str(source_file), str(target))
        log(f"Ordem {new_op} movida para input com sucesso!")
        print(f"Ordem {new_op} movida para input com sucesso!")

    except Exception as e:
        log(f"Falha crítica ao processar {source_file.name}: {str(e)}")
        print(f"Falha crítica ao processar {source_file.name}: {str(e)}")
        raise
    
def deduplicate_waiting_files():
    waiting_dir = Path(FOLDERS["waiting"])
    files_by_order = {}

    for file in waiting_dir.glob("MAK165*.xml"):
        try:
            op, creation_date_str, _, _ = get_production_order(file)
            
            # Converter para datetime object
            creation_date = datetime.fromisoformat(creation_date_str)
            
            if op not in files_by_order:
                files_by_order[op] = []
            files_by_order[op].append((file, creation_date))
            
        except Exception as e:
            log(f"Erro ao processar {file.name}: {str(e)}")
            print(f"Erro ao processar {file.name}: {str(e)}")
            continue

    for op, files in files_by_order.items():
        if len(files) > 1:
            try:
                # Ordenar por creation_date decrescente
                sorted_files = sorted(files, key=lambda x: x[1], reverse=True)
                latest_file = sorted_files[0][0]
                latest_date = sorted_files[0][1].isoformat()

                # Deletar todos exceto o mais recente
                for file, date in sorted_files[1:]:
                    file.unlink()
                    log(f"Removida versão antiga ({date.isoformat()}): {file.name}")
                    print(f"Removida versão antiga ({date.isoformat()}): {file.name}")

                log(f"Ordem {op} - Versão mais recente mantida: {latest_date}")
                print(f"Ordem {op} - Versão mais recente mantida: {latest_date}")

            except Exception as e:
                log(f"Falha crítica na deduplicação de {op}: {str(e)}")
                print(f"Falha crítica na deduplicação de {op}: {str(e)}")