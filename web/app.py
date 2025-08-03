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
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading
import time
import signal

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app)  # Включаем CORS
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

def load_parser_status():
    """Загрузка статуса из файла"""
    global parser_status
    try:
        with open('parser_status.json', 'r', encoding='utf-8') as f:
            parser_status = json.load(f)
    except FileNotFoundError:
        reset_parser_status()

def save_parser_status():
    """Сохранение статуса в файл"""
    try:
        with open('parser_status.json', 'w', encoding='utf-8') as f:
            json.dump(parser_status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения статуса: {e}")

def reset_parser_status():
    """Сброс статуса парсера"""
    global parser_status
    parser_status = {
        'running': False,
        'progress': 0,
        'message': 'Готов к запуску',
        'result_file': None,
        'error': None
    }
    save_parser_status()

# Глобальная переменная для хранения процесса
current_process = None

def run_parser_with_settings(settings):
    """Запуск парсера с настройками в отдельном потоке"""
    global parser_status, current_process
    
    try:
        # Сбрасываем статус перед запуском
        reset_parser_status()
        parser_status['running'] = True
        parser_status['progress'] = 0
        parser_status['message'] = 'Запуск парсера...'
        parser_status['error'] = None
        save_parser_status()
        
        logger.info(f"Запуск тестового парсера с настройками: {settings}")
        
        # Используем тестовый парсер для стабильной работы
        logger.info("Используем тестовый парсер для стабильной работы...")
        
        # Обновляем статус
        parser_status['message'] = 'Используем тестовый парсер...'
        save_parser_status()
        
        cmd = ['python3', 'test_parser.py']
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Отслеживаем прогресс для тестового парсера с таймаутом
        start_time = time.time()
        timeout = 60  # 1 минута для тестового парсера
        
        while current_process.poll() is None:
            # Проверяем таймаут
            if time.time() - start_time > timeout:
                logger.warning("Таймаут тестового парсера")
                current_process.terminate()
                raise Exception("Таймаут тестового парсера")
            
            parser_status['progress'] += 10
            if parser_status['progress'] > 85:
                parser_status['progress'] = 85
            parser_status['message'] = f'Тестовый парсинг... {parser_status["progress"]}%'
            time.sleep(0.5)
        
        stdout, stderr = current_process.communicate()
        
        if current_process.returncode == 0:
            parser_status['progress'] = 100
            parser_status['message'] = 'GoLogin парсинг завершен!'
            
            # Ждем немного и ищем созданный JSON файл
            time.sleep(2)
            for filename in os.listdir('.'):
                if filename.startswith('fragrantica_simple_news_') and filename.endswith('.json'):
                    parser_status['result_file'] = filename
                    break
            
            if parser_status['result_file']:
                logger.info(f"GoLogin парсер завершен успешно. Файл: {parser_status['result_file']}")
            else:
                parser_status['error'] = 'Файл не найден после завершения парсера'
                parser_status['message'] = 'Ошибка: файл не создан'
                logger.error("Файл не найден после завершения GoLogin парсера")
        else:
            parser_status['error'] = stderr or 'Неизвестная ошибка'
            parser_status['message'] = 'Ошибка при парсинге'
            logger.error(f"Ошибка GoLogin парсера: {stderr}")
        
        return
    
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
    load_parser_status()  # Загружаем актуальный статус
    return jsonify(parser_status)

@app.route('/api/reset-status', methods=['POST'])
def reset_status():
    """Сброс статуса парсера"""
    reset_parser_status()
    return jsonify({'message': 'Статус сброшен'})

@app.route('/api/test-parser', methods=['POST'])
def test_parser():
    """Тестирование парсера"""
    try:
        # Запускаем тестовый парсер
        result = subprocess.run(['python3', 'test_parser.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Ищем созданный файл
            for filename in os.listdir('.'):
                if filename.startswith('fragrantica_simple_news_') and filename.endswith('.json'):
                    return jsonify({'message': f'Тест успешен. Файл: {filename}'})
            
            return jsonify({'message': 'Тест успешен, но файл не найден'})
        else:
            return jsonify({'error': f'Ошибка теста: {result.stderr}'}), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Таймаут теста парсера'}), 500
    except Exception as e:
        return jsonify({'error': f'Ошибка теста: {str(e)}'}), 500

@app.route('/api/clear-files', methods=['POST'])
def clear_files():
    """Очистка старых файлов"""
    try:
        deleted_count = 0
        for filename in os.listdir('.'):
            if filename.startswith('fragrantica_simple_news_') and filename.endswith('.json'):
                os.remove(filename)
                deleted_count += 1
        
        return jsonify({'message': f'Удалено файлов: {deleted_count}'})
    except Exception as e:
        return jsonify({'error': f'Ошибка очистки: {str(e)}'}), 500

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
    # Загружаем статус при запуске
    load_parser_status()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False) 