from modules.logger import log
from flask import Flask, render_template, jsonify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modules.xml_processor import get_production_order
from modules.file_manager import move_to_input
from config import FOLDERS
import threading
import os
import msvcrt
from pathlib import Path  # Importe Path aqui também

app = Flask(__name__)

# Front-End
@app.route('/')
def index():
    return render_template('index.html')

# API para listar ordens
@app.route('/api/orders')
def api_orders():
    waiting_orders = []
    input_orders = []
    
    for file in Path(FOLDERS["waiting"]).glob("*.xml"):
        try:
            op, creation_date, sku, linha = get_production_order(file)
            waiting_orders.append({"op": op, "data": creation_date, "sku": sku, "linha": linha})
        except Exception as e:
            log(f"Erro ao processar {file}: {e}")

    for file in Path(FOLDERS["input"]).glob("*.xml"):
        try:
            op, creation_date, sku, linha = get_production_order(file)
            input_orders.append({"op": op, "data": creation_date, "sku": sku, "linha": linha})
        except Exception as e:
            log(f"Erro ao processar {file}: {e}")
            
    return jsonify({"waiting": waiting_orders, "input": input_orders})

# Rota para movimentação manual (main.py)
@app.route('/move/<order_id>')
def move_order(order_id):
    try:
        # Procura o arquivo em waiting
        files = []
        for file in Path(FOLDERS["waiting"]).glob("*.xml"):
            try:
                current_id, creation_date, sku, linha = get_production_order(file)
                if current_id == order_id:
                    files.append((file, creation_date))
            except Exception as e:
                log(f"Erro ao processar {file}: {e}")

        # Se houver mais de um arquivo com a mesma ordem de produção, seleciona o com data mais recente
        if len(files) > 1:
            latest_file = max(files, key=lambda x: x[1])
            file_to_move = latest_file[0]
        elif len(files) == 1:
            file_to_move = files[0][0]
        else:
            return jsonify({"status": "error", "message": "Ordem não encontrada"}), 404

        move_to_input(file_to_move, overwrite=True)
        log(f"Ordem {order_id} movida manualmente")
        return jsonify({"status": "success", "message": f"Ordem {order_id} movida!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Monitor de Arquivos
class MakHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".xml"):
            try:
                with open(event.src_path, "r+") as f:
                    # Bloqueia o arquivo para evitar race conditions
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    
                    threading.Thread(target=self.process_file, args=(event.src_path,)).start()
            except (BlockingIOError, PermissionError):  # Captura erro de arquivo travado
                print(f"Arquivo {event.src_path} já está em processamento. Ignorando...")
    
    def process_file(self, file_path):
        try:
            new_order_id, new_creation_date = get_production_order(file_path)
            log(f"Ordem detectada: {new_order_id}")

            # Verifica se já existe em input
            existing_files = []
            for existing_file in Path(FOLDERS["input"]).glob("*.xml"):
                existing_id, existing_date, _ = get_production_order(existing_file)
                if existing_id == new_order_id:
                    existing_files.append((existing_file, existing_date))

            if existing_files:  # Só substitui se já existir na input
                # Encontra o arquivo mais recente
                latest_file = max(existing_files, key=lambda x: x[1])
                
                if new_creation_date > latest_file[1]:
                    # Substitui todos os arquivos antigos
                    for file, _ in existing_files:
                        os.remove(file)
                        log(f"Arquivo antigo removido: {file.name}")
                    
                    move_to_input(Path(file_path))
                    log(f"Ordem {new_order_id} atualizada automaticamente")
                else:
                    os.remove(file_path)  # Descarta o novo arquivo
                    log(f"Ordem {new_order_id} ignorada (versão antiga)")
                    
            else:  # Mantém em waiting para ação manual
                log(f"Ordem {new_order_id} aguardando ação manual")

        except Exception as e:
            log(f"Erro crítico: {str(e)}")

if __name__ == '__main__':
    observer = Observer()
    observer.schedule(MakHandler(),  path=str(FOLDERS["waiting"]), recursive=False)
    observer.start()
    
    app.run(host='localhost', port=5000, debug=True, threaded=True)