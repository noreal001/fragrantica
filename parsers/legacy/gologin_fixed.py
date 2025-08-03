#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный парсер новостей Fragrantica для Render
Без GoLogin для стабильной работы на облачной платформе
"""

import time
import json
from datetime import datetime
from deep_translator import GoogleTranslator
import logging
from typing import List, Dict, Optional
import re
import random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fragrantica_simple_parser.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FragranticaSimpleParser:
    """Упрощенный парсер для Render"""
    
    def __init__(self):
        self.base_url = "https://www.fragrantica.com"
        self.translator = GoogleTranslator(source='en', target='ru')
        self.playwright = None
        self.browser = None
        
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
        """Создание контекста браузера с антидетект настройками"""
        try:
            # Используем стандартный браузер с антидетект настройками
            self.browser = self.playwright.chromium.launch(
                headless=True,  # Безголовый режим для Render
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Ускоряем загрузку
                    '--disable-javascript',  # Отключаем JS для ускорения
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            logger.info("Браузер запущен в стандартном режиме")
            
            # Создаем контекст с дополнительными настройками
            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                extra_http_headers={
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
                }
            )
            
            # Скрываем признаки автоматизации
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            return context
            
        except Exception as e:
            logger.error(f"Ошибка при создании контекста браузера: {e}")
            raise
    
    def _smart_delay(self, base_delay: float = 2.0):
        """Умная задержка с вариацией"""
        delay = base_delay + random.uniform(1.0, 3.0)
        time.sleep(delay)
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Получение содержимого страницы"""
        try:
            logger.info(f"Загружаю страницу: {url}")
            
            # Создаем новый контекст для каждого запроса
            context = self._create_browser_context()
            page = context.new_page()
            
            # Умная задержка
            self._smart_delay(3.0)
            
            # Переход на страницу
            page.goto(url, wait_until='networkidle')
            
            # Ждем загрузки страницы
            page.wait_for_load_state('domcontentloaded')
            
            # Обрабатываем Cloudflare проверку
            if self._handle_cloudflare_check(page):
                logger.info("Cloudflare проверка пройдена")
            else:
                logger.warning("Не удалось пройти Cloudflare проверку автоматически")
            
            # Дополнительная задержка для полной загрузки
            time.sleep(3)
            
            # Получаем HTML
            page_source = page.content()
            
            # Закрываем контекст
            context.close()
            
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {url}: {e}")
            return None
    
    def _handle_cloudflare_check(self, page) -> bool:
        """Обработка проверки Cloudflare"""
        try:
            logger.info("Проверяю наличие Cloudflare проверки...")
            
            # Ждем появления Cloudflare элементов
            time.sleep(3)
            
            # Проверяем наличие Cloudflare элементов
            cloudflare_selectors = [
                "iframe[src*='cloudflare']",
                "iframe[src*='challenge']",
                ".cf-browser-verification",
                "#cf-please-wait",
                "#challenge-form",
                ".cf-checkbox",
                "input[type='checkbox']"
            ]
            
            # Проверяем наличие Cloudflare
            for selector in cloudflare_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        logger.info(f"Найдены Cloudflare элементы с селектором: {selector}")
                        return self._try_cloudflare_bypass(page)
                except:
                    continue
            
            logger.info("Cloudflare проверка не обнаружена")
            return True
                
        except Exception as e:
            logger.error(f"Ошибка при обработке Cloudflare проверки: {e}")
            return False
    
    def _try_cloudflare_bypass(self, page) -> bool:
        """Попытка обхода Cloudflare"""
        try:
            # Метод 1: Поиск чекбокса на основной странице
            checkbox_selectors = [
                "input[type='checkbox']",
                ".cf-checkbox",
                "#cf-checkbox",
                "[data-testid='challenge-stage'] input",
                ".cf-button",
                "button[type='submit']"
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = page.query_selector(selector)
                    if checkbox and checkbox.is_visible():
                        logger.info(f"Найден чекбокс с селектором: {selector}")
                        checkbox.click()
                        
                        # Ждем завершения проверки
                        time.sleep(5)
                        return True
                        
                except Exception:
                    continue
            
            # Метод 2: Поиск в iframe
            iframes = page.query_selector_all("iframe")
            for iframe in iframes:
                try:
                    # Переключаемся на iframe
                    frame = iframe.content_frame()
                    
                    for selector in checkbox_selectors:
                        try:
                            checkbox = frame.query_selector(selector)
                            if checkbox and checkbox.is_visible():
                                logger.info(f"Найден чекбокс в iframe с селектором: {selector}")
                                checkbox.click()
                                
                                # Ждем завершения проверки
                                time.sleep(5)
                                return True
                                
                        except Exception:
                            continue
                            
                except Exception:
                    continue
            
            # Метод 3: Ждем автоматического прохождения
            logger.info("Жду автоматического прохождения Cloudflare проверки...")
            time.sleep(10)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обходе Cloudflare: {e}")
            return False
    
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
            
            # Создаем новый контекст для статьи
            context = self._create_browser_context()
            page = context.new_page()
            
            # Переход на страницу статьи
            page.goto(article_url, wait_until='networkidle')
            
            # Ждем загрузки контента
            page.wait_for_load_state('domcontentloaded')
            
            # Обрабатываем Cloudflare проверку
            if self._handle_cloudflare_check(page):
                logger.info("Cloudflare проверка пройдена для статьи")
            else:
                logger.warning("Не удалось пройти Cloudflare проверку для статьи")
            
            # Получаем HTML страницы
            page_source = page.content()
            
            # Закрываем контекст
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
    
    def translate_text(self, text: str) -> str:
        """Перевод текста на русский язык"""
        if not text or len(text.strip()) < 3:
            return text
        
        try:
            # Увеличенная задержка для перевода
            time.sleep(3 + random.uniform(1, 2))
            result = self.translator.translate(text)
            return result
        except Exception as e:
            logger.error(f"Ошибка при переводе текста: {e}")
            return text
    
    def translate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Перевод всех новостей на русский язык"""
        logger.info("Начинаю перевод новостей на русский язык...")
        
        translated_news = []
        for i, news in enumerate(news_items, 1):
            logger.info(f"Перевожу новость {i}/{len(news_items)}: {news.get('title', '')[:50]}...")
            
            translated_news_item = news.copy()
            
            # Перевод заголовка
            if news.get('title'):
                translated_news_item['title_ru'] = self.translate_text(news['title'])
            
            # Перевод краткого описания
            if news.get('content'):
                translated_news_item['content_ru'] = self.translate_text(news['content'])
            
            translated_news.append(translated_news_item)
        
        return translated_news
    
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
            if news.get('title_ru'):
                print(f"   🇷🇺 {news.get('title_ru')}")
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
    
    def close(self):
        """Закрытие браузера и Playwright"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Браузер и Playwright закрыты")
        except Exception as e:
            logger.error(f"Ошибка при закрытии: {e}")

def main():
    """Основная функция"""
    parser = None
    
    try:
        print("\n" + "="*60)
        print("🎯 УПРОЩЕННЫЙ ПАРСЕР FRAGRANTICA ДЛЯ RENDER")
        print("="*60)
        print("Этот парсер оптимизирован для работы на Render")
        print("="*60)
        
        parser = FragranticaSimpleParser()
        
        # Получение новостей с полным содержанием
        logger.info("Запуск упрощенного парсера...")
        news_items = parser.extract_news_from_main_page()
        
        if not news_items:
            logger.warning("Новости не найдены. Возможно, изменилась структура сайта.")
            print("\n⚠️ Новости не найдены. Попробуйте:")
            print("1. Проверить интернет-соединение")
            print("2. Убедиться, что сайт Fragrantica доступен")
            return
        
        # Перевод новостей
        translated_news = parser.translate_news(news_items)
        
        # Сохранение результатов
        parser.save_to_json(translated_news)
        
        # Вывод сводки
        parser.print_news_summary(translated_news)
        
        logger.info("Парсинг завершен успешно!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Произошла ошибка: {e}")
        print("💡 Проверьте логи в файле fragrantica_simple_parser.log")
    
    finally:
        # Закрываем браузер
        if parser:
            parser.close()

if __name__ == "__main__":
    main() 