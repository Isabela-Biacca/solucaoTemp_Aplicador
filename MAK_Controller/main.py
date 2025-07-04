from modules.logger import log
from flask import Flask, render_template, jsonify, request
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modules.xml_processor import get_production_order, get_lpn_values
from modules.file_manager import move_to_input
from config import FOLDERS, APLICADORES_FOLDERS
from datetime import datetime
from pathlib import Path
from waitress import serve
from apscheduler.schedulers.background import BackgroundScheduler
import shutil
import threading
import os
import msvcrt
import time

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
    
    # Para arquivos em waiting
    for file in Path(FOLDERS["waiting"]).glob("*.xml"):
        try:
            op, creation_date, sku, linha = get_production_order(file)
            waiting_orders.append({"op": op, "data": creation_date, "sku": sku, "linha": linha})
        except Exception as e:
            log(f"Erro ao processar {file}: {e}")

    # Para arquivos em input
    for file in Path(FOLDERS["input"]).glob("*.xml"):
        try:
            op, _, sku, linha = get_production_order(file)
            # Procurar meta correspondente no backup
            backup_dir = Path(FOLDERS["input"]) / "backup"
            meta_file = backup_dir / f"OP_{op}.meta"
            
            move_time = "N/A"
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    move_time = content.split('|')[-1]  # Extrair apenas a data
                    
            input_orders.append({
                "op": op,
                "data": move_time,
                "sku": sku,
                "linha": linha
            })
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
            return jsonify({"message": f"Ordem {order_id} nao encontrada"}), 404, {'charset': 'utf-8'}
                
        
        
         # Criar pasta backup se não existir
        backup_dir = Path(FOLDERS["input"]) / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        # Registrar timestamp exato
        move_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Criar/atualizar meta no backup
        meta_content = f"{order_id}|{move_time}"
        meta_file = backup_dir / f"OP_{order_id}.meta"
        
        with open(meta_file, 'w', encoding='utf-8') as f:
            f.write(meta_content)

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Ordem iniciada:")
        move_to_input(file_to_move, overwrite=True)
        log(f"Ordem {order_id} movida manualmente")
        return jsonify({
            "message": f"Ordem {order_id} movida!",
            "timestamp": move_time  # Enviar para o frontend
        }), 200, {'charset': 'utf-8'}

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500, {'charset': 'utf-8'}

@app.route('/encerrar/<order_id>')
def encerrar_ordem(order_id):
    try:
        # Encontrar o arquivo na pasta input
        input_folder = Path(FOLDERS["input"])
        backup_dir = input_folder / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        # Procurar e mover o XML
        for file in input_folder.glob("*.xml"):
            current_id, _, _, _ = get_production_order(file)
            if current_id == order_id:
                target_file = file
                break

        if not target_file:
            return jsonify(f"Ordem {order_id} nao encontrada"), 404, {'charset': 'utf-8'}

        # Deletar meta correspondente no backup
        meta_file = backup_dir / f"OP_{order_id}.meta"
        if meta_file.exists():
            try:
                meta_file.unlink()
                log(f"Meta removido: {meta_file.name}")
            except Exception as e:
                log(f"Erro ao remover meta: {str(e)}")
        
        # Mover arquivo
        shutil.move(str(target_file), str(backup_dir / target_file.name))
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Ordem {order_id} encerrada e movida para backup")
        log(f"Ordem {order_id} encerrada e movida para backup")
        return jsonify({
            "message": f"Ordem {order_id} encerrada com sucesso!",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200, {'charset': 'utf-8'}

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500, {'charset': 'utf-8'}

@app.route('/recuperar/<order_id>')
def recuperar_ordem(order_id):
    try:
        backup_dir = Path(FOLDERS["input"]) / "backup"
        files = []
        
        # 1. Buscar XMLs no backup
        for file in backup_dir.glob("*.xml"):
            try:
                current_id, creation_date, _, _ = get_production_order(file)
                if current_id == order_id:
                    files.append((file, creation_date))
            except Exception as e:
                log(f"Erro ao processar {file}: {e}")

        if not files:
            return jsonify({"message": f"Ordem {order_id} não encontrada no backup"}), 404

        # 2. Selecionar versão mais recente
        latest_file = max(files, key=lambda x: x[1])
        file_to_move = latest_file[0]

        # 3. Mover diretamente para input (usando a lógica de substituição existente)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Ordem recuperada:")
        move_to_input(file_to_move, overwrite=True)

        # 4. Atualizar/criar novo meta com status de reinício
        new_meta_content = f"{order_id}|REINICIADA/ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        new_meta_file = backup_dir / f"OP_{order_id}.meta"
        
        with open(new_meta_file, 'w') as f:
            f.write(new_meta_content)

        log(f"Ordem {order_id} reiniciada do backup")
        return jsonify({
            "message": f"Ordem {order_id} reiniciada com sucesso!",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/logs')
def logs():
    return render_template('log.html')

@app.route('/get_log')
def get_log():
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    try:
        year, month, day = date.split('-')
        log_path = os.path.join('logs', year, month, f"{date}.log")
        
        with open(log_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return jsonify({"content": content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 404, {'charset': 'utf-8'}
    
@app.route('/rastreadorLPN')
def lpns():
    return render_template('LPNTracker.html')

@app.route('/api/lpn')
def load_lpn():
    allLpn = []

    # Para arquivos em input
    for aplicador, output_path in APLICADORES_FOLDERS.items():
        folder_path = Path(output_path)
        
        for file in folder_path.glob("*.xml"):
            try:
                op, creation_date, sku, numLpn = get_lpn_values(file)
                
                data = datetime.fromisoformat(creation_date).strftime("%d/%m/%Y %H:%M:%S")
                
                allLpn.append({
                    "aplicador": aplicador,
                    "op": op,
                    "numLpn": numLpn,
                    "data": data,
                    "sku": sku
                })
            except Exception as e: 
                print(f"Erro ao processar {file}: {e}")
    
        allLpn = sorted(allLpn, key=lambda x: x['data'], reverse=True)
                
    return jsonify(allLpn)

@app.route('/api/search')
def search_lpn():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Informe um número de OP ou LPN"}), 400

    resultado = []
    
    # Para arquivos em input
    for aplicador, output_path in APLICADORES_FOLDERS.items():
        pastas_dir = [output_path, output_path / "backup"]
        
        for pasta in pastas_dir:
            if not pasta.exists():
                continue  # ignora se a pasta não existir
            
            for file in pasta.glob("*.xml"):
                try:
                    op, creation_date, sku, numLpn = get_lpn_values(file)
                    # moveTime = get_file_creation_time(file)
                    
                    data = datetime.fromisoformat(creation_date).strftime("%d/%m/%Y %H:%M:%S")

                    
                    if query in op or query in numLpn:
                        resultado.append({
                            "aplicador": aplicador,
                            "op": op,
                            "sku": sku,
                            "data": data,
                            "numLpn": numLpn,
                            "origem": "Enviado" if "backup" in file.parts else "Aguardando",
                            # "moveTime": moveTime
                        })
                except Exception as e: 
                    print(f"Erro ao processar {file}: {e}")
                               
            print(f"Arquivos do Aplicador {aplicador} processados")
            
    return jsonify(resultado)

def clean_old_mak_files():
    waiting_path = Path(FOLDERS["waiting"])
    backup_path = Path(FOLDERS["backup"])
    
    # Garantir que a pasta de backup existe
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Calcular o timestamp de 7 dias atrás (1 semana)
    cutoff_time = time.time() - (14 * 86400)  # 7 dias em segundos
    
    # Processar arquivos MAK165
    for file in waiting_path.glob("MAK165*.xml"):
        try:
            file_mtime = file.stat().st_mtime  # Data da última modificação
            if file_mtime < cutoff_time:
                # Mover para backup
                shutil.move(str(file), str(backup_path / file.name))
                log(f"Arquivo movido para backup: {file.name}")
        except Exception as e:
            log(f"Falha ao mover {file.name}: {str(e)}")

# Monitor de Arquivos
class MakHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".xml"):
            threading.Thread(target=self.handle_file, args=(event.src_path,)).start()

    def handle_file(self, file_path):
        max_retries = 5
        retry_delay = 1
        success = False
        new_order_id = None  # Declaração necessária

        for attempt in range(max_retries):
            try:
                with open(file_path, "r") as file:
                    try:
                        msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
                        # Mova a leitura do order_id para dentro do bloco bem-sucedido
                        new_order_id, new_creation_date, _, _ = get_production_order(file)
                        success = True
                        break
                    except (BlockingIOError, PermissionError):
                        if attempt == max_retries - 1:
                            error_msg = f"Falha ao processar MAK165 - {new_order_id} após {max_retries} tentativas"
                            log(error_msg)
                        time.sleep(retry_delay)
            except IOError as e:
                log(f"Erro de I/O: {str(e)}")

        if not success or not new_order_id:
            alert_msg = f"ATENÇÃO: Nao foi possível realizar atualização automática do arquivo MAK165 - {new_order_id}. Realizar ação manual!"
            log(alert_msg)
            return

        # Processar após fechar o arquivo
        try:
            existing_files = []
            input_folder = Path(FOLDERS["input"])
            for existing_file in input_folder.glob("*.xml"):
                try:
                    existing_id, existing_date, _, _ = get_production_order(existing_file)
                    if existing_id == new_order_id:
                        existing_files.append((existing_file, existing_date))
                except Exception as e:
                    log(f"Erro ao processar {existing_id}: {e}")

            if existing_files:
                latest_file = max(existing_files, key=lambda x: x[1])
                if new_creation_date > latest_file[1]:
                    for f in [file for file, _ in existing_files]:
                        os.remove(f)
                        log(f"Arquivo antigo removido: {f.name}")
                    move_to_input(Path(file_path))
                    log(f"Ordem {new_order_id} atualizada automaticamente")
                else:
                    os.remove(file_path)
                    log(f"Ordem {new_order_id} ignorada (versão antiga)")
            else:
                log(f"Ordem {new_order_id} aguardando ação manual")
        except Exception as e:
            log(f"Erro ao processar {file_path}: {e}")

if __name__ == '__main__':
    app.config['DEBUG'] = False 
    app.config['ENV'] = 'production'
    
    print("🟢 Iniciando monitoramento de arquivos...")
    observer = Observer()
    observer.schedule(MakHandler(), path=str(FOLDERS["waiting"]), recursive=False)
    observer.start()
    print(f"✅ Monitor ativo na pasta: {FOLDERS['waiting']}")

    from waitress import serve
    print("\n🚀 Inicializando servidor...")
    print(f"🔗 Acesso disponível em: http://172.16.16.70:8085")
    print("📡 Aguardando conexões...\n")
    
    # Agendamento para toda primeira quinta do mês
    print("🧼 Agendando limpeza semanal de arquivos MAK165...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        clean_old_mak_files,
        'cron',
        day_of_week='thu',
        hour=0,
        minute=0
    )
    
    scheduler.start()
    print(f"✅ Limpeza agendada: toda quinta-feira às 00:00")
    
    # serve(
    #     app,
    #     host='172.16.0.0',
    #     port=8085,
    #     threads=6,
    #     ident="Sistema LPN"  # Nome personalizado nos logs
    # )
    app.run(host='localhost', port=5000, debug=True, threaded=True)