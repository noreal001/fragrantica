# 🎯 Парсер новостей Fragrantica с ИИ переводом

Проект для парсинга новостей с сайта Fragrantica.com с обходом Cloudflare защиты и качественным переводом с помощью ИИ.

**🌐 GitHub:** [https://github.com/noreal001/fragrantica.git](https://github.com/noreal001/fragrantica.git)

## ✨ Возможности

- **Обход Cloudflare защиты** - использует Playwright с антидетект настройками
- **Полное извлечение контента** - получает полное содержание статей
- **Качественный перевод** - ИИ перевод с помощью OpenAI GPT
- **Структурированные данные** - JSON формат с метаданными
- **Веб-интерфейс** - удобное управление через браузер

## 📁 Структура проекта

```
Фрагрантика/
├── app.py                              # Flask веб-приложение
├── render.yaml                         # Конфигурация Render
├── requirements.txt                    # Зависимости Python
├── fragrantica_gologin_fixed.py       # Основной парсер
├── ai_translator.py                   # ИИ переводчик
├── templates/
│   └── index.html                     # Веб-интерфейс
├── DEPLOY.md                          # Инструкция по деплою
└── README.md                          # Документация
```

## 🚀 Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/noreal001/fragrantica.git
cd fragrantica
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Установите браузеры для Playwright:**
```bash
playwright install chromium
```

## 🔧 Использование

### 1. Локальный запуск

#### Парсинг новостей:
```bash
python3 fragrantica_gologin_fixed.py
```

#### Веб-интерфейс:
```bash
python3 app.py
```
Откройте http://localhost:5000

#### ИИ перевод (требует OpenAI API ключ):
```bash
export OPENAI_API_KEY='your-api-key-here'
python3 ai_translator.py
```

### 2. Деплой на Render

1. **Подключите репозиторий** в [Render Dashboard](https://render.com)
2. **Создайте Web Service** с настройками:
   - **Build Command:** `pip install -r requirements.txt && playwright install chromium`
   - **Start Command:** `python3 app.py`
   - **Health Check Path:** `/health`
3. **Добавьте переменные окружения:**
   - `OPENAI_API_KEY` - ваш ключ OpenAI API

## 📊 Результаты

### Структура JSON файла:

```json
{
  "title": "Заголовок на английском",
  "title_ru": "Перевод заголовка",
  "title_ru_ai": "ИИ перевод заголовка",
  "link": "Ссылка на статью",
  "image_url": "URL изображения",
  "content": "Краткое описание",
  "content_ru": "Перевод описания",
  "content_ru_ai": "ИИ перевод описания",
  "full_content": "Полное содержание статьи",
  "full_content_ru": "Перевод полного содержания",
  "full_content_ru_ai": "ИИ перевод полного содержания",
  "date": "Дата публикации",
  "original_language": "en"
}
```

### Примеры файлов:

- `fragrantica_gologin_fixed_news_*.json` - базовый парсинг
- `fragrantica_ai_translated_news_*.json` - с ИИ переводом

## 🛠️ Технические детали

### Парсер (`fragrantica_gologin_fixed.py`)

- **Технологии:** Playwright, BeautifulSoup, Deep Translator
- **Обход защиты:** Антидетект настройки браузера
- **Извлечение контента:** Множественные селекторы
- **Перевод:** Google Translator API

### ИИ переводчик (`ai_translator.py`)

- **API:** OpenAI GPT-3.5-turbo
- **Специализация:** Парфюмерия и ароматы
- **Качество:** Профессиональный перевод
- **Обработка:** Разбивка длинных текстов

### Веб-интерфейс (`app.py`)

- **Framework:** Flask
- **API Endpoints:** RESTful API
- **Отслеживание прогресса:** Real-time обновления
- **Скачивание файлов:** Прямые ссылки

## 🔍 Логирование

Все действия логируются в файлы:
- `fragrantica_gologin_fixed.log` - логи парсера
- `ai_translator.log` - логи ИИ переводчика

## ⚠️ Важные замечания

1. **API ключ OpenAI** - необходим для ИИ перевода
2. **Интернет соединение** - требуется для парсинга
3. **Задержки** - встроены для избежания блокировки
4. **Ограничения** - максимум 5 новостей за раз

## 🎯 Преимущества

- ✅ **Надежный обход защиты** - работает стабильно
- ✅ **Полное содержание** - не только заголовки
- ✅ **Качественный перевод** - ИИ для лучшего качества
- ✅ **Структурированные данные** - удобный JSON формат
- ✅ **Веб-интерфейс** - удобное управление
- ✅ **Логирование** - подробные логи для отладки

## 📝 Лицензия

Проект создан для образовательных целей. Соблюдайте правила сайта Fragrantica.com.

---

**Автор:** AI Assistant  
**Версия:** 2.0 (с ИИ переводом и веб-интерфейсом)  
**Дата:** Август 2025  
**GitHub:** [https://github.com/noreal001/fragrantica.git](https://github.com/noreal001/fragrantica.git) 