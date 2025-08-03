#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сброса статуса парсера
"""

import requests
import json

def reset_parser_status():
    """Сброс статуса парсера через API"""
    try:
        response = requests.post('http://localhost:5001/api/reset-status')
        if response.status_code == 200:
            print("✅ Статус парсера сброшен")
        else:
            print(f"❌ Ошибка сброса статуса: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def get_status():
    """Получение текущего статуса"""
    try:
        response = requests.get('http://localhost:5001/api/status')
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Текущий статус:")
            print(f"   Запущен: {status.get('running', False)}")
            print(f"   Прогресс: {status.get('progress', 0)}%")
            print(f"   Сообщение: {status.get('message', 'Нет')}")
            print(f"   Файл: {status.get('result_file', 'Нет')}")
            print(f"   Ошибка: {status.get('error', 'Нет')}")
        else:
            print(f"❌ Ошибка получения статуса: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("🔄 Сброс статуса парсера...")
    get_status()
    print("\n" + "="*50)
    reset_parser_status()
    print("\n" + "="*50)
    get_status() 