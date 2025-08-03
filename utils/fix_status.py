#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сброса статуса парсера напрямую
"""

import json

def reset_status():
    """Сброс статуса парсера"""
    status = {
        'running': False,
        'progress': 0,
        'message': 'Готов к запуску',
        'result_file': None,
        'error': None
    }
    
    # Записываем в файл для Flask
    with open('parser_status.json', 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print("✅ Статус парсера сброшен")
    print("📊 Новый статус:")
    for key, value in status.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    reset_status() 