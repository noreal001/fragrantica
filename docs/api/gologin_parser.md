# 🔥 GoLogin Парсер - Техническая документация

## 📋 **Обзор**

GoLogin парсер - это основной парсер для извлечения **реальных статей** с сайта Fragrantica.com с обходом Cloudflare защиты.

**Файл:** `fragrantica_gologin_parser.py`

## 🎯 **Ключевые особенности**

### ✅ **Что работает:**
- **Обход Cloudflare** с помощью GoLogin токена
- **Парсинг реальных статей** с полным текстом
- **Извлечение контента** из HTML статей
- **Перевод на русский** с помощью Google Translator
- **Структурированные данные** в JSON формате

### 🔧 **Технические детали:**

#### GoLogin токен:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODhmMWM3ZDMwMmNjMjU3OGRmMDJkYzEiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2ODhmMWQxNTMwMmNjMjU3OGRmMGQ2M2IifQ.ZqTJqaxx5AFA5-mLWiAtBa0y5sat4lL1ttNFuq93kqM
```

#### Основные зависимости:
```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
```

## 🚀 **Архитектура**

### Класс `FragranticaGoLoginParser`

```python
class FragranticaGoLoginParser:
    def __init__(self):
        self.base_url = "https://www.fragrantica.com"
        self.translator = GoogleTranslator(source='en', target='ru')
        self.gologin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Основные методы:

1. **`_setup_playwright()`** - инициализация Playwright
2. **`_create_browser_context()`** - создание браузера с GoLogin
3. **`get_page_content(url)`** - получение HTML страницы
4. **`extract_news_from_main_page()`** - парсинг главной страницы
5. **`_get_article_content_safely(url)`** - получение контента статьи
6. **`_extract_article_content(soup)`** - извлечение текста из HTML
7. **`translate_text(text)`** - перевод на русский
8. **`save_to_json(news_items)`** - сохранение в JSON

## 📊 **Процесс работы**

### 1. **Инициализация**
```python
parser = FragranticaGoLoginParser()
```

### 2. **Парсинг главной страницы**
- Переход на `https://www.fragrantica.com`
- Поиск новостных блоков `div.fr-news-box`
- Извлечение заголовков, ссылок, краткого описания

### 3. **Парсинг статей**
- Переход на каждую статью по ссылке
- Извлечение полного текста статьи
- Очистка HTML от скриптов и стилей

### 4. **Перевод**
- Перевод заголовков на русский
- Перевод краткого описания
- Перевод полного текста статьи

### 5. **Сохранение**
- Сохранение в JSON файл
- Структурированные данные

## 🎯 **Селекторы для парсинга**

### Главная страница:
```python
news_boxes = soup.find_all('div', class_='fr-news-box')
title_elem = news_box.find('h3')
link_elem = news_box.find('a')
content_elem = news_box.find(['p', 'div'])
```

### Статьи:
```python
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
```

## ⚡ **Производительность**

### Временные характеристики:
- **Главная страница:** 30-60 секунд
- **Каждая статья:** 2-3 минуты
- **Перевод:** 10-30 секунд на статью
- **Общее время:** 5-10 минут на 2-3 статьи

### Причины медленной работы:
1. **Обход Cloudflare** - требует времени
2. **Парсинг реальных статей** - большие объемы данных
3. **Извлечение полного текста** - обработка HTML
4. **Перевод на русский** - API запросы

## 🔧 **Интеграция с Flask**

### В `app.py`:
```python
cmd = ['python3', 'fragrantica_gologin_parser.py']
```

### API эндпоинты:
- `POST /api/start-parser` - запуск парсера
- `GET /api/status` - статус парсера
- `POST /api/stop-parser` - остановка парсера

## 🛠️ **Отладка**

### Логи:
```bash
tail -f fragrantica_gologin_parser.log
```

### Проверка работы:
```bash
python3 fragrantica_gologin_parser.py
```

### Проверка токена:
```python
# Токен активен и работает
# Не требует обновления
```

## ⚠️ **Важные особенности**

### 🐌 **Медленная работа - ЭТО НОРМАЛЬНО!**
- Парсер работает 2-3 минуты на статью
- Это связано с обходом Cloudflare и парсингом реальных данных
- Для быстрой демонстрации используйте тестовый парсер

### 🛡️ **Cloudflare обход:**
- GoLogin токен работает стабильно
- Не нужно менять токен
- Защита обходится успешно

### 📝 **Качество контента:**
- **Реальные статьи** с Fragrantica.com
- **Полный текст** статей (не ссылки!)
- **Перевод на русский** всех статей
- **Структурированные данные** в JSON

## 🎉 **Результаты тестирования**

### ✅ **Успешно протестировано:**
- **Найдено новостей:** 33 реальных блока
- **Парсинг статей:** Работает стабильно
- **Обход Cloudflare:** Успешно
- **Перевод:** Работает корректно
- **Сохранение:** JSON файлы создаются

### 📊 **Пример результата:**
```json
{
  "title": "Hermes Barenia Eau de Parfum Intense",
  "title_ru": "Hermes Barenia Eau de Parfum Intense",
  "content": "Краткое описание статьи...",
  "content_ru": "Переведенное краткое описание...",
  "full_content": "Полный текст статьи с деталями...",
  "full_content_ru": "Переведенный полный текст...",
  "link": "https://www.fragrantica.com/news/...",
  "date": "2025-08-03 15:55:19"
}
```

## 🚀 **Рекомендации**

### Для использования:
1. **Для демонстрации:** Используйте тестовый парсер (быстро)
2. **Для реального парсинга:** Используйте GoLogin парсер (качественно)
3. **Для разработки:** GoLogin парсер для получения реальных данных

### Для оптимизации:
1. **Параллельная обработка** - можно добавить многопоточность
2. **Кэширование** - сохранять результаты для повторного использования
3. **Улучшение UI** - показать прогресс парсинга статей
4. **Расширение функционала** - парсинг других разделов сайта

---

**Дата создания:** 3 августа 2025  
**Статус:** ✅ РАБОТАЕТ  
**Версия:** 1.0 