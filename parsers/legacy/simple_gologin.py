#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный GoLogin парсер с правильным API подходом
"""

import time
import json
from datetime import datetime
from deep_translator import GoogleTranslator
import logging
import requests
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGoLoginParser:
    def __init__(self):
        self.base_url = "https://www.fragrantica.com"
        self.translator = GoogleTranslator(source='en', target='ru')
        self.gologin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODhmMWM3ZDMwMmNjMjU3OGRmMDJkYzEiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2ODhmMWQxNTMwMmNjMjU3OGRmMGQ2M2IifQ.ZqTJqaxx5AFA5-mLWiAtBa0y5sat4lL1ttNFuq93kqM"
        self.api_url = "https://api.gologin.com"
    
    def _create_profile(self):
        """Создание профиля через GoLogin API"""
        try:
            profile_data = {
                "name": f"fragrantica_parser_{int(time.time())}",
                "notes": "Парсер Fragrantica",
                "navigator": {
                    "language": ["en-US", "en"],
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "resolution": "1920x1080",
                    "platform": "MacIntel"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.gologin_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/browser",
                json=profile_data,
                headers=headers
            )
            
            if response.status_code == 200:
                profile = response.json()
                logger.info(f"Создан профиль: {profile['id']}")
                return profile['id']
            else:
                logger.error(f"Ошибка создания профиля: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при создании профиля: {e}")
            return None
    
    def _get_page_content(self, url):
        """Получение содержимого страницы с правильными заголовками"""
        try:
            session = requests.Session()
            session.headers.update({
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
            
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {url}: {e}")
            return None
    
    def extract_news(self):
        """Извлечение новостей"""
        logger.info("Начинаю парсинг главной страницы...")
        
        # Создаем профиль
        profile_id = self._create_profile()
        
        try:
            # Получаем главную страницу
            page_content = self._get_page_content(self.base_url)
            if not page_content:
                logger.error("Не удалось получить главную страницу")
                return []
            
            soup = BeautifulSoup(page_content, 'html.parser')
            news_items = []
            
            # Поиск новостных блоков
            news_boxes = soup.find_all('div', class_='fr-news-box')
            logger.info(f"Найдено {len(news_boxes)} новостных блоков")
            
            for i, news_box in enumerate(news_boxes[:3], 1):
                try:
                    news_item = self._extract_news_data(news_box)
                    if news_item and news_item.get('link'):
                        # Получаем полное содержание статьи
                        full_content = self._get_article_content(news_item['link'])
                        if full_content:
                            news_item['full_content'] = full_content
                            news_item['full_content_ru'] = self.translate_text(full_content)
                        
                        news_items.append(news_item)
                        logger.info(f"Обработана новость {i}: {news_item.get('title', '')[:50]}...")
                        
                except Exception as e:
                    logger.error(f"Ошибка при обработке новости {i}: {e}")
                    continue
            
            return news_items
            
        finally:
            if profile_id:
                self._delete_profile(profile_id)
    
    def _extract_news_data(self, news_box):
        """Извлечение данных из новостного блока"""
        try:
            title_elem = news_box.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            link_elem = news_box.find('a')
            link = ""
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                link = self.base_url + href if href.startswith('/') else href
            
            content_elem = news_box.find(['p', 'div'], class_=re.compile(r'content|description|excerpt', re.I))
            if not content_elem:
                content_elem = news_box.find('p')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            if title:
                return {
                    'title': title,
                    'link': link,
                    'content': content,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'original_language': 'en'
                }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных новости: {e}")
        
        return None
    
    def _get_article_content(self, article_url):
        """Получение содержания статьи"""
        try:
            logger.info(f"Получаю содержание статьи: {article_url}")
            
            page_content = self._get_page_content(article_url)
            if not page_content:
                return None
            
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Поиск контента
            content_selectors = [
                'div.article-content',
                'div.post-content',
                'div.entry-content',
                'div.content',
                'article .content',
                '.main-content',
                '.article-body',
                '.post-body',
                '.news-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    for script in content_elem(["script", "style", "nav", "header", "footer"]):
                        script.decompose()
                    
                    text = content_elem.get_text(separator='\n', strip=True)
                    if text and len(text) > 200:
                        text = re.sub(r'\n\s*\n', '\n\n', text)
                        text = re.sub(r'\s+', ' ', text)
                        return text.strip()
            
            # Если не найдено, ищем параграфы
            paragraphs = soup.find_all('p')
            if paragraphs:
                texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and len(p.get_text(strip=True)) > 50]
                return '\n\n'.join(texts)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении содержания статьи: {e}")
            return None
    
    def translate_text(self, text):
        """Перевод текста на русский"""
        try:
            if not text or len(text.strip()) < 10:
                return ""
            
            return self.translator.translate(text)
                
        except Exception as e:
            logger.error(f"Ошибка при переводе текста: {e}")
            return ""
    
    def translate_news(self, news_items):
        """Перевод новостей"""
        logger.info("Начинаю перевод новостей...")
        
        for i, news_item in enumerate(news_items, 1):
            try:
                if news_item.get('title'):
                    news_item['title_ru'] = self.translate_text(news_item['title'])
                
                if news_item.get('content'):
                    news_item['content_ru'] = self.translate_text(news_item['content'])
                
                logger.info(f"Переведена новость {i}/{len(news_items)}")
                
            except Exception as e:
                logger.error(f"Ошибка при переводе новости {i}: {e}")
                continue
        
        return news_items
    
    def _delete_profile(self, profile_id):
        """Удаление профиля"""
        try:
            headers = {
                'Authorization': f'Bearer {self.gologin_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.delete(
                f"{self.api_url}/browser/{profile_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Профиль {profile_id} удален")
            else:
                logger.warning(f"Не удалось удалить профиль {profile_id}")
                
        except Exception as e:
            logger.error(f"Ошибка при удалении профиля: {e}")
    
    def save_to_json(self, news_items, filename=None):
        """Сохранение в JSON"""
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

def main():
    """Основная функция"""
    try:
        print("🚀 Запуск упрощенного GoLogin парсера...")
        
        parser = SimpleGoLoginParser()
        
        # Парсим новости
        news_items = parser.extract_news()
        
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

if __name__ == "__main__":
    main() 