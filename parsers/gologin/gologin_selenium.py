#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fragrantica Parser с официальным GoLogin SDK и Selenium
Основан на официальной документации: https://gologin.com/docs/api-reference/introduction/quickstart
"""

import os
import time
import json
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
import random
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# Официальный GoLogin SDK
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/gologin_selenium.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FragranticaGoLoginSeleniumParser:
    """Парсер Fragrantica с официальным GoLogin SDK и Selenium"""
    
    def __init__(self):
        self.base_url = "https://www.fragrantica.com"
        self.translator = GoogleTranslator(source='en', target='ru')
        
        # Инициализация GoLogin с токеном из переменных окружения
        self.gl = GoLogin({
            "token": os.environ.get('GL_API_TOKEN', 'your dev token'),
        })
        
        self.driver = None
        self.profile_id = None
        
        logger.info("GoLogin Selenium парсер инициализирован")
    
    def create_profile(self):
        """Создание профиля с случайным fingerprint"""
        try:
            # Создаем профиль с Windows OS
            profile = self.gl.createProfileRandomFingerprint({ "os": "win" })
            self.profile_id = profile.get('id')
            
            # Добавляем US прокси к профилю
            self.gl.addGologinProxyToProfile(self.profile_id, "us")
            
            logger.info(f"Создан профиль GoLogin: {self.profile_id}")
            return self.profile_id
            
        except Exception as e:
            logger.error(f"Ошибка при создании профиля: {e}")
            raise
    
    def start_browser(self):
        """Запуск браузера через GoLogin"""
        try:
            # Устанавливаем ID профиля
            self.gl.setProfileId(self.profile_id)
            
            # Запускаем браузер и получаем WebSocket URL
            debugger_address = self.gl.start()
            
            # Получаем версию Chromium для webdriver
            chromium_version = self.gl.get_chromium_version()
            
            # Устанавливаем webdriver
            service = Service(ChromeDriverManager(driver_version=chromium_version).install())
            
            # Настройки Chrome
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
            
            # Создаем драйвер
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Настройка таймаутов
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            logger.info("Браузер GoLogin запущен")
            return self.driver
            
        except Exception as e:
            logger.error(f"Ошибка при запуске браузера: {e}")
            raise
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Получение содержимого страницы"""
        try:
            logger.info(f"Загружаю страницу: {url}")
            
            # Переход на страницу
            self.driver.get(url)
            
            # Ждем загрузки страницы
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Дополнительная задержка для полной загрузки
            time.sleep(5)
            
            # Получаем HTML
            page_source = self.driver.page_source
            
            # Парсим HTML
            soup = BeautifulSoup(page_source, 'html.parser')
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
                    logger.info(f"Обрабатываю новость {i}: {news_item.get('title', 'Без заголовка')}")
                    
                    # Получаем полное содержание статьи
                    full_content = self._get_article_content_safely(news_item['link'])
                    if full_content:
                        news_item['full_content'] = full_content
                        news_item['full_content_ru'] = self.translate_text(full_content)
                    
                    news_items.append(news_item)
                    
                    # Умная задержка между запросами
                    time.sleep(random.uniform(2, 4))
                    
            except Exception as e:
                logger.error(f"Ошибка при обработке новости {i}: {e}")
                continue
        
        logger.info(f"Успешно обработано {len(news_items)} новостей")
        return news_items
    
    def _extract_news_data(self, news_box) -> Optional[Dict]:
        """Извлечение данных новости из блока"""
        try:
            # Заголовок
            title_elem = news_box.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else "Без заголовка"
            
            # Ссылка
            link_elem = news_box.find('a')
            link = link_elem.get('href') if link_elem else None
            if link and not link.startswith('http'):
                link = self.base_url + link
            
            # Краткое описание
            content_elem = news_box.find(['p', 'div'])
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Дата
            date_elem = news_box.find('time')
            date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                'title': title,
                'link': link,
                'content': content,
                'date': date
            }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных новости: {e}")
            return None
    
    def _get_article_content_safely(self, article_url: str) -> Optional[str]:
        """Безопасное получение содержания статьи"""
        try:
            logger.info(f"Получаю содержание статьи: {article_url}")
            
            soup = self.get_page_content(article_url)
            if not soup:
                return None
            
            return self._extract_article_content(soup)
            
        except Exception as e:
            logger.error(f"Ошибка при получении содержания статьи {article_url}: {e}")
            return None
    
    def _extract_article_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение текста статьи из HTML"""
        try:
            # Список селекторов для поиска контента
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
            
            # Поиск контента по селекторам
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Очищаем HTML от скриптов и стилей
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    
                    # Получаем текст
                    text = content_elem.get_text(separator='\n', strip=True)
                    
                    # Очищаем лишние пробелы
                    text = re.sub(r'\n\s*\n', '\n\n', text)
                    text = re.sub(r' +', ' ', text)
                    
                    if text.strip():
                        logger.info(f"Найден контент с селектором: {selector}")
                        return text.strip()
            
            # Если не найден контент, берем весь body
            body = soup.find('body')
            if body:
                # Удаляем навигацию, футер и другие элементы
                for elem in body(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                    elem.decompose()
                
                text = body.get_text(separator='\n', strip=True)
                text = re.sub(r'\n\s*\n', '\n\n', text)
                text = re.sub(r' +', ' ', text)
                
                return text.strip()
            
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
        """Сохранение результатов в JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/output/fragrantica_gologin_selenium_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Результаты сохранены в {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении в JSON: {e}")
            return None
    
    def print_news_summary(self, news_items: List[Dict]):
        """Вывод сводки новостей"""
        print(f"\n📰 Найдено новостей: {len(news_items)}")
        
        for i, item in enumerate(news_items, 1):
            print(f"\n{i}. {item.get('title', 'Без заголовка')}")
            print(f"   📅 {item.get('date', 'Без даты')}")
            print(f"   🔗 {item.get('link', 'Без ссылки')}")
            
            content = item.get('content', '')
            if content:
                print(f"   📝 {content[:100]}{'...' if len(content) > 100 else ''}")
            
            full_content = item.get('full_content', '')
            if full_content:
                print(f"   📄 Полный текст: {len(full_content)} символов")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Браузер закрыт")
            
            if self.profile_id:
                self.gl.delete(self.profile_id)
                logger.info(f"Профиль {self.profile_id} удален")
            
            self.gl.stop()
            logger.info("GoLogin остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке: {e}")
    
    def run(self, news_count: int = 3):
        """Основной метод запуска парсера"""
        try:
            logger.info("🚀 Запуск GoLogin Selenium парсера Fragrantica...")
            
            # Создаем профиль
            self.create_profile()
            
            # Запускаем браузер
            self.start_browser()
            
            # Парсим новости
            news_items = self.extract_news_from_main_page()
            
            # Ограничиваем количество новостей
            news_items = news_items[:news_count]
            
            # Переводим новости
            news_items = self.translate_news(news_items)
            
            # Сохраняем результаты
            filename = self.save_to_json(news_items)
            
            # Выводим сводку
            self.print_news_summary(news_items)
            
            logger.info("✅ Парсинг завершен успешно!")
            return news_items
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге: {e}")
            return []
        
        finally:
            self.cleanup()

def main():
    """Точка входа"""
    parser = FragranticaGoLoginSeleniumParser()
    
    try:
        news_items = parser.run(news_count=3)
        
        if news_items:
            print(f"\n✅ Успешно обработано {len(news_items)} новостей")
        else:
            print("\n❌ Не удалось получить новости")
            
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 