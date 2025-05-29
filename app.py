from flask import Flask, request, render_template, send_file, jsonify, url_for
import pandas as pd
import json
import os
from celery_worker import celery_app # Importa a instância do Celery

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Celery Configuration
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Cria as pastas de upload e processed se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@celery_app.task(bind=True)
def process_file_task(self, filepath, original_filename):
    """Tarefa Celery para processar o arquivo e converter para JSON."""
    try:
        app.logger.info(f"[Celery Task {self.request.id}] Iniciando processamento do arquivo: {original_filename}")
        start_time = pd.Timestamp.now()

        df = None
        if original_filename.endswith('.csv'):
            try:
                chunk_list = []
                # Estimar total de linhas para feedback de progresso (opcional, pode adicionar overhead)
                # total_rows = sum(1 for row in open(filepath, 'r', encoding='utf-8'))
                # current_rows = 0
                for chunk_index, chunk in enumerate(pd.read_csv(filepath, chunksize=10000)):
                    chunk_list.append(chunk)
                    # current_rows += len(chunk)
                    # self.update_state(state='PROGRESS', meta={'current': current_rows, 'total': total_rows, 'status': 'Processando CSV...'})
                    self.update_state(state='PROGRESS', meta={'current': (chunk_index + 1) * 10000, 'total': -1, 'status': f'Processando chunk {chunk_index + 1} do CSV...'})
                df = pd.concat(chunk_list, ignore_index=True)
            except Exception as e:
                app.logger.error(f"[Celery Task {self.request.id}] Erro ao ler CSV em chunks: {str(e)}")
                df = pd.read_csv(filepath) # Fallback
        elif original_filename.endswith(('.xlsx', '.xls')):
            self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Lendo arquivo Excel...'})
            df = pd.read_excel(filepath)
            self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Arquivo Excel lido.'})
        elif original_filename.endswith('.xml'):
            self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Lendo arquivo XML...'})
            df = pd.read_xml(filepath)
            self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Arquivo XML lido.'})
        else:
            raise ValueError(f"Formato de arquivo não suportado: {original_filename}")

        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': 'Convertendo para JSON...'})
        json_data = df.to_json(orient='records', indent=4, force_ascii=False)
        json_filename = os.path.splitext(original_filename)[0] + '.json'
        json_filepath = os.path.join(app.config['PROCESSED_FOLDER'], json_filename)
        with open(json_filepath, 'w', encoding='utf-8') as f:
            f.write(json_data)
        self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'JSON salvo.'})

        end_time = pd.Timestamp.now()
        processing_time = end_time - start_time
        app.logger.info(f"[Celery Task {self.request.id}] Arquivo {original_filename} processado em {processing_time}")
        return {'current': 100, 'total': 100, 'status': 'Concluído!', 'result': json_filename, 'filename': json_filename}

    except Exception as e:
        app.logger.error(f"[Celery Task {self.request.id}] Erro ao processar o arquivo {original_filename}: {str(e)}")
        # O estado FAILURE é automaticamente definido pelo Celery em caso de exceção não tratada
        # Mas podemos adicionar informações extras se quisermos
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'status': 'Falha no processamento'})
        raise # Re-lança a exceção para que o Celery a marque como falha


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    if file:
        original_filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(filepath)

        # Enfileira a tarefa Celery
        task = process_file_task.delay(filepath, original_filename)
        
        # Retorna o ID da tarefa para que o cliente possa verificar o status
        return jsonify({'message': 'Arquivo recebido e processamento iniciado.', 'task_id': task.id, 'status_url': url_for('task_status', task_id=task.id, _external=True)}), 202

@app.route('/task_status/<task_id>')
def task_status(task_id):
    task = process_file_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pendente...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 100),
            'total': task.info.get('total', 100),
            'status': task.info.get('status', 'Concluído!'),
            'result': task.result.get('filename') # ou task.result se o resultado for apenas o nome do arquivo
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0) if isinstance(task.info, dict) else 0,
            'total': task.info.get('total', 1) if isinstance(task.info, dict) else 1,
            'status': str(task.info),  # Informação genérica
        }
    else: # task.state == 'FAILURE'
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': 'Falha no processamento.',
            'error': str(task.info)  # task.info contém a exceção
        }
    return jsonify(response)

@app.route('/split', methods=['POST'])
def split_json():
    filename = request.form.get('filename')
    parts_str = request.form.get('parts')

    if not filename or not parts_str:
        return jsonify({'error': 'Nome do arquivo ou número de partes não fornecido'}), 400

    try:
        parts = int(parts_str)
        if parts <= 0:
            return jsonify({'error': 'Número de partes deve ser maior que zero'}), 400

        json_filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(json_filepath):
            return jsonify({'error': 'Arquivo JSON não encontrado'}), 404

        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            return jsonify({'error': 'O arquivo JSON não contém uma lista de objetos para divisão'}), 400

        total_items = len(data)
        if total_items == 0:
            return jsonify({'message': 'Arquivo JSON vazio, nenhuma divisão necessária'}), 200

        items_per_part = (total_items + parts - 1) // parts # Arredonda para cima
        
        split_files = []
        for i in range(parts):
            start_index = i * items_per_part
            end_index = min((i + 1) * items_per_part, total_items)
            
            if start_index >= total_items:
                break

            part_data = data[start_index:end_index]
            part_filename = f"{os.path.splitext(filename)[0]}_part{i+1}.json"
            part_filepath = os.path.join(app.config['PROCESSED_FOLDER'], part_filename)
            
            with open(part_filepath, 'w', encoding='utf-8') as f:
                json.dump(part_data, f, indent=4, ensure_ascii=False)
            
            split_files.append(part_filename)

        return jsonify({'message': f'Arquivo dividido em {len(split_files)} partes com sucesso!', 'split_files': split_files}), 200

    except ValueError:
        return jsonify({'error': 'Número de partes inválido'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao dividir o arquivo: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(filepath):
        if filename.endswith('.json'):
            return send_file(filepath, as_attachment=False, mimetype='application/json')
        else:
            return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'Arquivo não encontrado para download'}), 404

@app.route('/list_json_files')
def list_json_files():
    files = [f for f in os.listdir(app.config['PROCESSED_FOLDER']) if f.endswith('.json')]
    return jsonify({'files': files}), 200

if __name__ == '__main__':
    app.run(debug=True)