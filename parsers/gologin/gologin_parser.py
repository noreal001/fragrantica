#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер новостей Fragrantica с GoLogin для обхода Cloudflare
"""

import time
import json
from datetime import datetime
from deep_translator import GoogleTranslator
import logging
from typing import List, Dict, Optional
import re
import random
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FragranticaGoLoginParser:
    """Парсер с GoLogin для обхода Cloudflare"""
    
    def __init__(self):
        self.base_url = "https://www.fragrantica.com"
        self.translator = GoogleTranslator(source='en', target='ru')
        self.playwright = None
        
        # GoLogin токен
        self.gologin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODhmMWM3ZDMwMmNjMjU3OGRmMDJkYzEiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2ODhmMWQxNTMwMmNjMjU3OGRmMGQ2M2IifQ.ZqTJqaxx5AFA5-mLWiAtBa0y5sat4lL1ttNFuq93kqM"
        
        # Инициализация Playwright
        self._setup_playwright()
    
    def _setup_playwright(self):
        """Настройка Playwright"""
        try:
            self.playwright = sync_playwright().start()
            logger.info("Playwright инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Playwright: {e}")
            raise
    
    def _create_browser_context(self):
        """Создание контекста браузера с GoLogin"""
        try:
            # Запускаем браузер с GoLogin
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir="/tmp/gologin_profile",
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ],
                viewport={'width': 1920, 'height': 1080}
            )
            
            logger.info("Браузер запущен с GoLogin")
            return self.browser
            
        except Exception as e:
            logger.error(f"Ошибка при создании контекста браузера: {e}")
            raise
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Получение содержимого страницы с GoLogin"""
        try:
            logger.info(f"Загружаю страницу с GoLogin: {url}")
            
            # Создаем контекст браузера
            context = self._create_browser_context()
            page = context.new_page()
            
            # Переход на страницу
            page.goto(url, wait_until='networkidle', timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(3)
            
            # Получаем HTML
            page_source = page.content()
            context.close()
            
            # Парсим HTML
            soup = BeautifulSoup(page_source, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {url}: {e}")
            return None
    
    def extract_news_from_main_page(self) -> List[Dict]:
        """Извлечение новостей с главной страницы"""
        logger.info("Начинаю парсинг главной страницы Fragrantica с GoLogin...")
        
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        news_items = []
        
        # Поиск новостных блоков
        news_boxes = soup.find_all('div', class_='fr-news-box')
        logger.info(f"Найдено {len(news_boxes)} новостных блоков")
        
        for i, news_box in enumerate(news_boxes[:5], 1):
            try:
                news_item = self._extract_news_data(news_box)
                if news_item and news_item.get('link'):
                    # Пытаемся получить полное содержание статьи
                    full_content = self._get_article_content_safely(news_item['link'])
                    if full_content:
                        news_item['full_content'] = full_content
                        news_item['full_content_ru'] = self.translate_text(full_content)
                    
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
            
            # Поиск краткого описания
            content_elem = news_box.find(['p', 'div'], class_=re.compile(r'content|description|excerpt', re.I))
            if not content_elem:
                content_elem = news_box.find('p')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Поиск даты
            date_elem = news_box.find(['time', 'span', 'div'], class_=re.compile(r'date|time', re.I))
            date = date_elem.get_text(strip=True) if date_elem else ""
            
            if title:
                return {
                    'title': title,
                    'link': link,
                    'content': content,
                    'date': date,
                    'original_language': 'en'
                }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных новости: {e}")
        
        return None
    
    def _get_article_content_safely(self, article_url: str) -> Optional[str]:
        """Безопасное получение содержания статьи с GoLogin"""
        try:
            logger.info(f"Пытаюсь получить содержание статьи с GoLogin: {article_url}")
            
            # Создаем новый контекст для статьи
            context = self._create_browser_context()
            page = context.new_page()
            
            # Переход на страницу статьи
            page.goto(article_url, wait_until='networkidle', timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(3)
            
            # Получаем HTML страницы
            page_source = page.content()
            context.close()
            
            soup = BeautifulSoup(page_source, 'html.parser')
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
                    if text and len(text) > 200:
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
            
            # Очищаем контент
            if full_content:
                full_content = re.sub(r'\n\s*\n', '\n\n', full_content)
                full_content = re.sub(r'\s+', ' ', full_content)
                full_content = full_content.strip()
                
                logger.info(f"Извлечено {len(full_content)} символов контента")
                return full_content
            
            logger.warning("Контент статьи не найден")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении контента статьи: {e}")
            return None
    
    def translate_text(self, text: str) -> str:
        """Перевод текста на русский"""
        try:
            if not text or len(text.strip()) < 10:
                return ""
            
            return self.translator.translate(text)
                
        except Exception as e:
            logger.error(f"Ошибка при переводе текста: {e}")
            return ""
    
    def translate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Перевод новостей на русский"""
        logger.info("Начинаю перевод новостей...")
        
        for i, news_item in enumerate(news_items, 1):
            try:
                # Переводим заголовок
                if news_item.get('title'):
                    news_item['title_ru'] = self.translate_text(news_item['title'])
                
                # Переводим краткое содержание
                if news_item.get('content'):
                    news_item['content_ru'] = self.translate_text(news_item['content'])
                
                logger.info(f"Переведена новость {i}/{len(news_items)}")
                
            except Exception as e:
                logger.error(f"Ошибка при переводе новости {i}: {e}")
                continue
        
        return news_items
    
    def save_to_json(self, news_items: List[Dict], filename: str = None):
        """Сохранение новостей в JSON файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fragrantica_simple_news_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Новости сохранены в файл: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
            return None
    
    def close(self):
        """Закрытие парсера"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Парсер закрыт")
        except Exception as e:
            logger.error(f"Ошибка при закрытии парсера: {e}")

def main():
    """Основная функция"""
    parser = None
    try:
        print("🚀 Запуск парсера Fragrantica с GoLogin...")
        
        # Создаем парсер
        parser = FragranticaGoLoginParser()
        
        # Парсим новости
        news_items = parser.extract_news_from_main_page()
        
        if not news_items:
            print("❌ Новости не найдены")
            return
        
        # Переводим новости
        news_items = parser.translate_news(news_items)
        
        # Сохраняем в файл
        filename = parser.save_to_json(news_items)
        
        print(f"\n✅ Парсинг завершен! Файл: {filename}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}")
    finally:
        if parser:
            parser.close()

if __name__ == "__main__":
    main() 