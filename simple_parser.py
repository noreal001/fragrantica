#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Максимально простой парсер для Render
Использует только базовые библиотеки
"""

import time
import json
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
import random
import requests
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_parser.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleFragranticaParser:
    """Простой парсер с requests"""
    
    def __init__(self):
        self.base_url = "https://www.fragrantica.com"
        self.session = requests.Session()
        
        # Настройка сессии
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        logger.info("Простой парсер инициализирован")
    
    def _smart_delay(self, base_delay: float = 2.0):
        """Умная задержка с вариацией"""
        delay = base_delay + random.uniform(1.0, 3.0)
        time.sleep(delay)
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Получение содержимого страницы"""
        try:
            logger.info(f"Загружаю страницу: {url}")
            
            # Умная задержка
            self._smart_delay(3.0)
            
            # Запрос страницы
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Проверяем на Cloudflare
            if 'cloudflare' in response.text.lower():
                logger.warning("Обнаружена Cloudflare защита")
                return None
            
            # Парсим HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {url}: {e}")
            return None
    
    def extract_news_from_main_page(self) -> List[Dict]:
        """Извлечение новостей с главной страницы"""
        logger.info("Начинаю парсинг главной страницы Fragrantica...")
        
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        news_items = []
        
        # Поиск новостных блоков
        news_boxes = soup.find_all('div', class_='fr-news-box')
        logger.info(f"Найдено {len(news_boxes)} новостных блоков")
        
        for i, news_box in enumerate(news_boxes[:5], 1):  # Ограничиваем 5 последними новостями
            try:
                news_item = self._extract_news_data(news_box)
                if news_item and news_item.get('link'):
                    # Пытаемся получить полное содержание статьи
                    full_content = self._get_article_content_safely(news_item['link'])
                    if full_content:
                        news_item['full_content'] = full_content
                    
                    news_items.append(news_item)
                    logger.info(f"Обработана новость {i}: {news_item.get('title', '')[:50]}...")
                    
            except Exception as e:
                logger.error(f"Ошибка при обработке новостного блока {i}: {e}")
                continue
        
        return news_items
    
    def _extract_news_data(self, news_box) -> Optional[Dict]:
        """Извлечение данных из новостного блока"""
        try:
            # Поиск заголовка
            title_elem = news_box.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Поиск ссылки
            link_elem = news_box.find('a')
            link = ""
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                link = self.base_url + href if href.startswith('/') else href
            
            # Поиск изображения
            img_elem = news_box.find('img')
            image_url = ""
            if img_elem and img_elem.get('src'):
                src = img_elem.get('src')
                image_url = self.base_url + src if src.startswith('/') else src
            
            # Поиск краткого описания
            content_elem = news_box.find(['p', 'div'], class_=re.compile(r'content|description|excerpt', re.I))
            if not content_elem:
                content_elem = news_box.find('p')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Поиск даты
            date_elem = news_box.find(['time', 'span', 'div'], class_=re.compile(r'date|time', re.I))
            date = date_elem.get_text(strip=True) if date_elem else ""
            
            if title:  # Добавляем только если есть заголовок
                return {
                    'title': title,
                    'link': link,
                    'image_url': image_url,
                    'content': content,
                    'date': date,
                    'original_language': 'en'
                }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных новости: {e}")
        
        return None
    
    def _get_article_content_safely(self, article_url: str) -> Optional[str]:
        """Безопасное получение содержания статьи"""
        try:
            logger.info(f"Пытаюсь получить содержание статьи: {article_url}")
            
            # Получаем страницу статьи
            soup = self.get_page_content(article_url)
            if not soup:
                return None
            
            return self._extract_article_content(soup)
            
        except Exception as e:
            logger.error(f"Ошибка при получении содержания статьи: {e}")
            return None
    
    def _extract_article_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение содержания из HTML статьи"""
        try:
            # Поиск основного контента статьи
            content_selectors = [
                'div.article-content',
                'div.post-content',
                'div.entry-content',
                'div.content',
                'article .content',
                '.main-content',
                '.article-body',
                '.post-body',
                '.news-content',
                '.article-text',
                '.post-text',
                '.entry-content',
                '.content-area',
                '.article',
                '.post',
                '.entry'
            ]
            
            full_content = ""
            
            # Пробуем найти контент по селекторам
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Удаляем скрипты и стили
                    for script in content_elem(["script", "style", "nav", "header", "footer", "aside"]):
                        script.decompose()
                    
                    # Получаем текст
                    text = content_elem.get_text(separator='\n', strip=True)
                    if text and len(text) > 200:  # Минимальная длина для полноценного контента
                        full_content = text
                        logger.info(f"Найден контент с селектором: {selector}")
                        break
            
            # Если не найдено по селекторам, ищем параграфы
            if not full_content:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and len(p.get_text(strip=True)) > 50]
                    full_content = '\n\n'.join(texts)
                    logger.info(f"Найден контент из параграфов: {len(paragraphs)} параграфов")
            
            # Если все еще нет, ищем любой текст в статье
            if not full_content:
                article_elem = soup.find('article') or soup.find('div', class_=re.compile(r'article|post|content', re.I))
                if article_elem:
                    # Удаляем скрипты и стили
                    for script in article_elem(["script", "style", "nav", "header", "footer", "aside"]):
                        script.decompose()
                    
                    text = article_elem.get_text(separator='\n', strip=True)
                    if text and len(text) > 200:
                        full_content = text
                        logger.info("Найден контент из основного элемента статьи")
            
            # Очищаем контент
            if full_content:
                # Удаляем лишние пробелы и переносы строк
                full_content = re.sub(r'\n\s*\n', '\n\n', full_content)
                full_content = re.sub(r'\s+', ' ', full_content)
                full_content = full_content.strip()
                
                # Ограничиваем длину для перевода
                if len(full_content) > 4000:
                    full_content = full_content[:4000] + "..."
                
                return full_content
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении содержания статьи: {e}")
        
        return None
    
    def save_to_json(self, news_items: List[Dict], filename: str = None):
        """Сохранение новостей в JSON файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fragrantica_simple_news_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            logger.info(f"Новости сохранены в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
    
    def print_news_summary(self, news_items: List[Dict]):
        """Вывод краткой сводки новостей"""
        print(f"\n{'='*60}")
        print(f"НАЙДЕНО НОВОСТЕЙ: {len(news_items)}")
        print(f"{'='*60}")
        
        for i, news in enumerate(news_items, 1):
            print(f"\n{i}. {news.get('title', 'Без заголовка')}")
            if news.get('date'):
                print(f"   📅 {news.get('date')}")
            if news.get('link'):
                print(f"   🔗 {news.get('link')}")
            if news.get('content'):
                content_preview = news.get('content', '')[:100] + "..." if len(news.get('content', '')) > 100 else news.get('content', '')
                print(f"   📝 {content_preview}")
            if news.get('full_content'):
                full_content_preview = news.get('full_content', '')[:300] + "..." if len(news.get('full_content', '')) > 300 else news.get('full_content', '')
                print(f"   📄 Полное содержание: {full_content_preview}")
            print("-" * 60)

def main():
    """Основная функция"""
    parser = None
    
    try:
        print("\n" + "="*60)
        print("🎯 ПРОСТОЙ ПАРСЕР FRAGRANTICA ДЛЯ RENDER")
        print("="*60)
        print("Этот парсер использует только базовые библиотеки")
        print("="*60)
        
        parser = SimpleFragranticaParser()
        
        # Получение новостей с полным содержанием
        logger.info("Запуск простого парсера...")
        news_items = parser.extract_news_from_main_page()
        
        if not news_items:
            logger.warning("Новости не найдены. Возможно, изменилась структура сайта.")
            print("\n⚠️ Новости не найдены. Попробуйте:")
            print("1. Проверить интернет-соединение")
            print("2. Убедиться, что сайт Fragrantica доступен")
            return
        
        # Сохранение результатов
        parser.save_to_json(news_items)
        
        # Вывод сводки
        parser.print_news_summary(news_items)
        
        logger.info("Парсинг завершен успешно!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Произошла ошибка: {e}")
        print("💡 Проверьте логи в файле simple_parser.log")

if __name__ == "__main__":
    main() 