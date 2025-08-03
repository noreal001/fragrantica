#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИИ переводчик для улучшения качества переводов
Использует OpenAI API для качественного перевода текстов
"""

import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import openai
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_translator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AITranslator:
    """ИИ переводчик для улучшения качества переводов"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            logger.info("OpenAI API ключ установлен")
        else:
            logger.warning("OpenAI API ключ не найден. Используйте переменную окружения OPENAI_API_KEY")
    
    def translate_with_ai(self, text: str, context: str = "") -> str:
        """Перевод текста с помощью ИИ"""
        if not self.api_key:
            logger.error("OpenAI API ключ не установлен")
            return text
        
        try:
            # Формируем промпт для качественного перевода
            prompt = f"""
Переведи следующий текст с английского на русский язык. 
Текст относится к парфюмерии и ароматам. 
Сохрани все технические термины и названия брендов.
Сделай перевод естественным и понятным для русскоязычной аудитории.

Контекст: {context}

Текст для перевода:
{text}

Перевод:
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты профессиональный переводчик с английского на русский язык, специализирующийся на текстах о парфюмерии и ароматах."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            logger.info(f"ИИ перевод завершен, длина: {len(translated_text)} символов")
            return translated_text
            
        except Exception as e:
            logger.error(f"Ошибка при ИИ переводе: {e}")
            return text
    
    def translate_news_with_ai(self, news_items: List[Dict]) -> List[Dict]:
        """Перевод новостей с помощью ИИ"""
        logger.info("Начинаю ИИ перевод новостей...")
        
        translated_news = []
        for i, news in enumerate(news_items, 1):
            logger.info(f"Перевожу новость {i}/{len(news_items)}: {news.get('title', '')[:50]}...")
            
            translated_news_item = news.copy()
            
            # Перевод заголовка
            if news.get('title'):
                translated_news_item['title_ru_ai'] = self.translate_with_ai(
                    news['title'], 
                    "Заголовок статьи о парфюмерии"
                )
            
            # Перевод краткого описания
            if news.get('content'):
                translated_news_item['content_ru_ai'] = self.translate_with_ai(
                    news['content'], 
                    "Краткое описание статьи о парфюмерии"
                )
            
            # Перевод полного содержания
            if news.get('full_content'):
                # Разбиваем длинный текст на части для лучшего перевода
                full_content = news['full_content']
                if len(full_content) > 3000:
                    # Разбиваем на части по 3000 символов
                    parts = [full_content[j:j+3000] for j in range(0, len(full_content), 3000)]
                    translated_parts = []
                    
                    for part_num, part in enumerate(parts, 1):
                        logger.info(f"Перевожу часть {part_num}/{len(parts)} полного содержания...")
                        translated_part = self.translate_with_ai(
                            part, 
                            f"Часть {part_num} полного содержания статьи о парфюмерии"
                        )
                        translated_parts.append(translated_part)
                        time.sleep(2)  # Пауза между запросами
                    
                    translated_news_item['full_content_ru_ai'] = ' '.join(translated_parts)
                else:
                    translated_news_item['full_content_ru_ai'] = self.translate_with_ai(
                        full_content, 
                        "Полное содержание статьи о парфюмерии"
                    )
            
            translated_news.append(translated_news_item)
            time.sleep(3)  # Пауза между новостями
        
        return translated_news
    
    def save_to_json(self, news_items: List[Dict], filename: str = None):
        """Сохранение новостей в JSON файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fragrantica_ai_translated_news_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            logger.info(f"Новости с ИИ переводом сохранены в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
    
    def print_comparison(self, news_items: List[Dict]):
        """Вывод сравнения переводов"""
        print(f"\n{'='*80}")
        print(f"СРАВНЕНИЕ ПЕРЕВОДОВ: {len(news_items)} НОВОСТЕЙ")
        print(f"{'='*80}")
        
        for i, news in enumerate(news_items, 1):
            print(f"\n{i}. {news.get('title', 'Без заголовка')}")
            
            if news.get('title_ru') and news.get('title_ru_ai'):
                print(f"   🇷🇺 Обычный: {news.get('title_ru')}")
                print(f"   🤖 ИИ: {news.get('title_ru_ai')}")
            
            if news.get('content_ru') and news.get('content_ru_ai'):
                print(f"   📝 Обычный: {news.get('content_ru')[:100]}...")
                print(f"   🤖 ИИ: {news.get('content_ru_ai')[:100]}...")
            
            if news.get('full_content_ru') and news.get('full_content_ru_ai'):
                print(f"   📄 Полное содержание (ИИ): {news.get('full_content_ru_ai')[:200]}...")
            
            print("-" * 80)

def main():
    """Основная функция"""
    print("\n" + "="*60)
    print("🤖 ИИ ПЕРЕВОДЧИК ДЛЯ FRAGRANTICA")
    print("="*60)
    
    # Проверяем наличие API ключа
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ OpenAI API ключ не найден!")
        print("Установите переменную окружения OPENAI_API_KEY")
        print("Пример: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Загружаем данные из JSON файла
    input_file = "fragrantica_gologin_fixed_news_20250803_113644.json"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            news_items = json.load(f)
        
        print(f"✅ Загружено {len(news_items)} новостей из файла {input_file}")
        
        # Создаем ИИ переводчик
        translator = AITranslator(api_key)
        
        # Переводим новости с помощью ИИ
        ai_translated_news = translator.translate_news_with_ai(news_items)
        
        # Сохраняем результаты
        translator.save_to_json(ai_translated_news)
        
        # Выводим сравнение
        translator.print_comparison(ai_translated_news)
        
        logger.info("ИИ перевод завершен успешно!")
        
    except FileNotFoundError:
        print(f"❌ Файл {input_file} не найден!")
        print("Сначала запустите парсер для получения новостей")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    main() 