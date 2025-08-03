#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-интерфейс для парсера Fragrantica
Flask приложение для запуска парсера через веб-интерфейс
"""

import os
import json
import subprocess
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import threading
import time
import signal

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Создаем папку для загрузок если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Глобальные переменные для отслеживания статуса
parser_status = {
    'running': False,
    'progress': 0,
    'message': 'Готов к запуску',
    'result_file': None,
    'error': None
}

# Глобальная переменная для хранения процесса
current_process = None

def run_parser_with_settings(settings):
    """Запуск парсера с настройками в отдельном потоке"""
    global parser_status, current_process
    
    try:
        parser_status['running'] = True
        parser_status['progress'] = 0
        parser_status['message'] = 'Запуск парсера...'
        parser_status['error'] = None
        
        logger.info(f"Запуск парсера Fragrantica с настройками: {settings}")
        
        # Создаем команду с настройками
        cmd = ['python3', 'fragrantica_gologin_fixed.py']
        
        # Добавляем параметры если они есть
        if settings.get('newsCount'):
            cmd.extend(['--count', str(settings['newsCount'])])
        
        if settings.get('targetLanguage'):
            cmd.extend(['--language', settings['targetLanguage']])
        
        # Запускаем парсер
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Отслеживаем прогресс
        while current_process.poll() is None:
            parser_status['progress'] += 10
            if parser_status['progress'] > 90:
                parser_status['progress'] = 90
            parser_status['message'] = f'Парсинг... {parser_status["progress"]}%'
            time.sleep(2)
        
        # Получаем результат
        stdout, stderr = current_process.communicate()
        
        if current_process.returncode == 0:
            parser_status['progress'] = 100
            parser_status['message'] = 'Парсинг завершен успешно!'
            
            # Ищем созданный JSON файл
            for filename in os.listdir('.'):
                if filename.startswith('fragrantica_simple_news_') and filename.endswith('.json'):
                    parser_status['result_file'] = filename
                    break
            
            logger.info(f"Парсер завершен успешно. Файл: {parser_status['result_file']}")
        else:
            parser_status['error'] = stderr or 'Неизвестная ошибка'
            parser_status['message'] = 'Ошибка при парсинге'
            logger.error(f"Ошибка парсера: {stderr}")
    
    except Exception as e:
        parser_status['error'] = str(e)
        parser_status['message'] = 'Критическая ошибка'
        logger.error(f"Критическая ошибка: {e}")
    
    finally:
        parser_status['running'] = False
        current_process = None

def run_parser():
    """Запуск парсера в отдельном потоке (для обратной совместимости)"""
    run_parser_with_settings({})

def run_ai_translator():
    """Запуск ИИ переводчика в отдельном потоке"""
    global parser_status, current_process
    
    try:
        parser_status['running'] = True
        parser_status['progress'] = 0
        parser_status['message'] = 'Запуск ИИ переводчика...'
        parser_status['error'] = None
        
        logger.info("Запуск ИИ переводчика...")
        
        # Проверяем наличие API ключа
        if not os.environ.get('OPENAI_API_KEY'):
            parser_status['error'] = 'OpenAI API ключ не установлен'
            parser_status['message'] = 'Ошибка: нет API ключа'
            return
        
        # Запускаем ИИ переводчик
        current_process = subprocess.Popen(
            ['python3', 'ai_translator.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Отслеживаем прогресс
        while current_process.poll() is None:
            parser_status['progress'] += 5
            if parser_status['progress'] > 90:
                parser_status['progress'] = 90
            parser_status['message'] = f'ИИ перевод... {parser_status["progress"]}%'
            time.sleep(3)
        
        # Получаем результат
        stdout, stderr = current_process.communicate()
        
        if current_process.returncode == 0:
            parser_status['progress'] = 100
            parser_status['message'] = 'ИИ перевод завершен успешно!'
            
            # Ищем созданный JSON файл
            for filename in os.listdir('.'):
                if filename.startswith('fragrantica_ai_translated_news_') and filename.endswith('.json'):
                    parser_status['result_file'] = filename
                    break
            
            logger.info(f"ИИ переводчик завершен успешно. Файл: {parser_status['result_file']}")
        else:
            parser_status['error'] = stderr or 'Неизвестная ошибка'
            parser_status['message'] = 'Ошибка при ИИ переводе'
            logger.error(f"Ошибка ИИ переводчика: {stderr}")
    
    except Exception as e:
        parser_status['error'] = str(e)
        parser_status['message'] = 'Критическая ошибка'
        logger.error(f"Критическая ошибка: {e}")
    
    finally:
        parser_status['running'] = False
        current_process = None

def stop_parser():
    """Остановка парсера"""
    global current_process, parser_status
    
    if current_process and current_process.poll() is None:
        try:
            # Отправляем сигнал завершения
            current_process.terminate()
            
            # Ждем завершения
            try:
                current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Принудительно завершаем если не завершился
                current_process.kill()
                current_process.wait()
            
            parser_status['running'] = False
            parser_status['message'] = 'Парсер остановлен'
            current_process = None
            
            logger.info("Парсер успешно остановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при остановке парсера: {e}")
            return False
    
    return False

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Получение статуса парсера"""
    return jsonify(parser_status)

@app.route('/api/start-parser', methods=['GET', 'POST'])
def start_parser():
    """Запуск парсера"""
    if parser_status['running']:
        return jsonify({'error': 'Парсер уже запущен'})
    
    # Получаем настройки из POST запроса
    settings = {}
    if request.method == 'POST':
        try:
            settings = request.get_json() or {}
        except Exception as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
    
    thread = threading.Thread(target=run_parser_with_settings, args=(settings,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Парсер запущен'})

@app.route('/api/stop-parser', methods=['POST'])
def stop_parser_endpoint():
    """Остановка парсера"""
    if stop_parser():
        return jsonify({'message': 'Парсер остановлен'})
    else:
        return jsonify({'error': 'Парсер не был запущен или уже остановлен'})

@app.route('/api/start-ai-translator')
def start_ai_translator():
    """Запуск ИИ переводчика"""
    if parser_status['running']:
        return jsonify({'error': 'Процесс уже запущен'})
    
    # Проверяем наличие файла с результатами парсинга
    json_files = [f for f in os.listdir('.') if f.startswith('fragrantica_simple_news_') and f.endswith('.json')]
    if not json_files:
        return jsonify({'error': 'Сначала запустите парсер для получения данных'})
    
    thread = threading.Thread(target=run_ai_translator)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'ИИ переводчик запущен'})

@app.route('/api/download/<filename>')
def download_file(filename):
    """Скачивание файла"""
    try:
        # Читаем содержимое файла и возвращаем как JSON
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Файл не найден'}), 404
    except Exception as e:
        return jsonify({'error': f'Ошибка чтения файла: {str(e)}'}), 500

@app.route('/api/files')
def list_files():
    """Список доступных файлов"""
    files = []
    for filename in os.listdir('.'):
        if filename.endswith('.json') and 'fragrantica' in filename:
            stat = os.stat(filename)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Сортируем по дате изменения (новые сначала)
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify({'files': files})

@app.route('/health')
def health_check():
    """Проверка здоровья приложения"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 