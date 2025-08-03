# 🚀 Fragrantica Parser - Обновленная версия

## 📋 Обзор

Fragrantica Parser - это веб-приложение для парсинга новостей с сайта Fragrantica.com с использованием официального GoLogin SDK для обхода Cloudflare защиты.

**Основано на официальной документации GoLogin:**
- [Официальная документация](https://gologin.com/docs/api-reference/introduction/quickstart)
- [GitHub репозиторий](https://github.com/gologinapp/gologin)
- [Postman коллекция](https://documenter.getpostman.com/view/21126834/Uz5GnvaL)

## 🎯 Ключевые особенности

### ✅ **Что работает:**
- **Официальный GoLogin SDK** - использует последнюю версию
- **Обход Cloudflare защиты** с помощью GoLogin токена
- **Парсинг реальных статей** с полным текстом
- **Перевод на русский** с помощью Google Translator
- **Веб-интерфейс** для удобного управления
- **Модульная архитектура** - легко расширяемый код

### 🔧 **Технические улучшения:**
- Использование официального GoLogin SDK
- Правильная структура проекта
- Конфигурационные файлы
- Улучшенная обработка ошибок
- Подробная документация

## 📁 Структура проекта

```
fragrantica/
├── 📁 parsers/                    # Парсеры
│   ├── 📁 gologin/               # GoLogin парсеры
│   │   ├── gologin_parser.py     # Основной GoLogin парсер
│   │   ├── gologin_selenium.py   # Selenium версия
│   │   └── gologin_puppeteer.py  # Puppeteer версия
│   ├── 📁 simple/                # Простые парсеры
│   │   ├── simple_parser.py      # Простой requests парсер
│   │   └── test_parser.py        # Тестовый парсер
│   └── 📁 legacy/                # Старые версии
├── 📁 web/                       # Веб-интерфейс
│   ├── 📁 static/               # Статические файлы
│   ├── 📁 templates/            # HTML шаблоны
│   └── app.py                   # Flask приложение
├── 📁 docs/                     # Документация
│   ├── 📁 api/                  # API документация
│   ├── 📁 deployment/           # Документация по развертыванию
│   └── 📁 guides/               # Руководства
├── 📁 config/                   # Конфигурация
│   ├── settings.py              # Настройки
│   └── gologin_config.py        # Конфигурация GoLogin
├── 📁 utils/                    # Утилиты
├── 📁 data/                     # Данные
│   ├── 📁 output/              # Результаты парсинга
│   └── 📁 logs/                # Логи
└── 📁 scripts/                  # Скрипты
```

## 🚀 Быстрый старт

### 1. **Клонирование репозитория**
```bash
git clone https://github.com/noreal001/fragrantica.git
cd fragrantica
```

### 2. **Установка зависимостей**
```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 3. **Настройка GoLogin токена**
```bash
# Создайте файл .env
echo "GL_API_TOKEN=your_gologin_api_token_here" > .env
```

### 4. **Запуск приложения**
```bash
python web/app.py
```

### 5. **Открытие в браузере**
```
http://localhost:5001
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# GoLogin API токен (обязательно)
GL_API_TOKEN=your_gologin_api_token_here

# Настройки Flask
FLASK_ENV=development
FLASK_DEBUG=1

# Настройки логирования
LOG_LEVEL=INFO
```

### Получение GoLogin токена

1. Зайдите в [GoLogin Dashboard](https://app.gologin.com/)
2. Перейдите в Settings → API
3. Скопируйте ваш API токен
4. Добавьте токен в файл `.env`

## 📚 Документация

### 📖 **Руководства**
- [API документация](docs/api/gologin_api.md) - Официальная документация GoLogin
- [Руководство по развертыванию](docs/deployment/) - Как развернуть проект
- [Руководство пользователя](docs/guides/) - Как использовать приложение

### 🔧 **Конфигурация**
- [Настройки GoLogin](config/gologin_config.py) - Конфигурация парсера
- [Настройки приложения](config/settings.py) - Общие настройки

## 🎯 Использование

### Веб-интерфейс

1. **Откройте** `http://localhost:5001`
2. **Выберите режим:**
   - **Тест парсера** - быстрая демонстрация
   - **Запустить** - реальный парсинг с GoLogin
3. **Настройте параметры:**
   - Количество новостей
   - Язык перевода
4. **Нажмите "Запустить"**

### Прямой запуск

```bash
# Запуск основного парсера
python parsers/gologin/gologin_parser.py

# Запуск тестового парсера
python parsers/simple/test_parser.py
```

### API использование

```python
from parsers.gologin.gologin_parser import FragranticaGoLoginParser

# Создание парсера
parser = FragranticaGoLoginParser()

# Запуск парсинга
news_items = parser.run(news_count=3)

# Результаты
for item in news_items:
    print(f"Заголовок: {item['title']}")
    print(f"Ссылка: {item['link']}")
    print(f"Контент: {item['content'][:100]}...")
```

## 🔧 Разработка

### Структура кода

```python
# parsers/gologin/gologin_parser.py
class FragranticaGoLoginParser:
    def __init__(self):
        # Инициализация с официальным SDK
        self.gl = GoLogin({
            "token": os.environ.get('GL_API_TOKEN'),
        })
    
    def create_profile(self):
        # Создание профиля с случайным fingerprint
        profile = self.gl.createProfileRandomFingerprint({ "os": "win" })
    
    def start_browser(self):
        # Запуск браузера через GoLogin
        debugger_address = self.gl.start()
    
    def cleanup(self):
        # Очистка ресурсов
        self.gl.delete(self.profile_id)
        self.gl.stop()
```

### Добавление новых парсеров

1. Создайте новый файл в `parsers/`
2. Наследуйтесь от базового класса
3. Реализуйте необходимые методы
4. Добавьте документацию

## 🚨 Важные заметки

### ⚠️ **Обязательные требования:**
- **GoLogin токен** - без него парсер не работает
- **Python 3.9+** - для совместимости с зависимостями
- **Интернет соединение** - для работы с GoLogin API

### 🐌 **Производительность:**
- **Создание профиля:** 2-5 секунд
- **Запуск браузера:** 10-20 секунд
- **Парсинг статьи:** 2-3 минуты
- **Общее время:** 5-10 минут на 2-3 статьи

### 🛡️ **Безопасность:**
- Токен хранится в переменных окружения
- Профили автоматически удаляются после использования
- Браузеры корректно закрываются

## 🔗 Полезные ссылки

- [Официальная документация GoLogin](https://gologin.com/docs/api-reference/introduction/quickstart)
- [GitHub репозиторий GoLogin](https://github.com/gologinapp/gologin)
- [Postman коллекция API](https://documenter.getpostman.com/view/21126834/Uz5GnvaL)
- [MCP Server для AI интеграции](https://github.com/gologinapp/gologin-mcp)

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 🤝 Поддержка

Если у вас есть вопросы или проблемы:

1. **Проверьте документацию** в папке `docs/`
2. **Посмотрите логи** в папке `data/logs/`
3. **Создайте issue** в GitHub репозитории

---

**Дата обновления:** 3 августа 2025  
**Версия:** 2.0  
**Основано на:** Официальной документации GoLogin 