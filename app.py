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

def run_parser():
    """Запуск парсера в отдельном потоке"""
    global parser_status
    
    try:
        parser_status['running'] = True
        parser_status['progress'] = 0
        parser_status['message'] = 'Запуск парсера...'
        parser_status['error'] = None
        
        logger.info("Запуск парсера Fragrantica...")
        
        # Запускаем парсер
        process = subprocess.Popen(
            ['python3', 'fragrantica_gologin_fixed.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Отслеживаем прогресс
        while process.poll() is None:
            parser_status['progress'] += 10
            if parser_status['progress'] > 90:
                parser_status['progress'] = 90
            parser_status['message'] = f'Парсинг... {parser_status["progress"]}%'
            time.sleep(2)
        
        # Получаем результат
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
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

def run_ai_translator():
    """Запуск ИИ переводчика в отдельном потоке"""
    global parser_status
    
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
        process = subprocess.Popen(
            ['python3', 'ai_translator.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Отслеживаем прогресс
        while process.poll() is None:
            parser_status['progress'] += 5
            if parser_status['progress'] > 90:
                parser_status['progress'] = 90
            parser_status['message'] = f'ИИ перевод... {parser_status["progress"]}%'
            time.sleep(3)
        
        # Получаем результат
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
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

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Получение статуса парсера"""
    return jsonify(parser_status)

@app.route('/api/start-parser')
def start_parser():
    """Запуск парсера"""
    if parser_status['running']:
        return jsonify({'error': 'Парсер уже запущен'})
    
    thread = threading.Thread(target=run_parser)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Парсер запущен'})

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
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Файл не найден'}), 404

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
    
    return jsonify({'files': files})

@app.route('/health')
def health_check():
    """Проверка здоровья приложения"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 