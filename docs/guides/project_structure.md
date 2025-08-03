# Структура проекта Fragrantica Parser

## Обзор

```
Фрагрантика/
├── frontend/                    # Исходники фронтенда
│   ├── css/
│   │   └── style.css           # Основные стили
│   ├── js/
│   │   └── app.js              # JavaScript логика
│   ├── README.md               # Документация фронтенда
│   └── sync.sh                 # Скрипт синхронизации
├── static/                      # Статические файлы для Flask
│   ├── css/
│   │   └── style.css           # Копия из frontend/css/
│   └── js/
│       └── app.js              # Копия из frontend/js/
├── templates/                   # HTML шаблоны
│   └── index.html              # Главная страница
├── app.py                      # Flask приложение
├── fragrantica_gologin_fixed.py # Основной парсер
├── ai_translator.py            # ИИ переводчик
├── simple_parser.py            # Простой парсер
├── requirements.txt             # Python зависимости
├── runtime.txt                 # Версия Python для Render
├── render.yaml                 # Конфигурация Render
├── DEPLOY.md                   # Инструкции по деплою
├── IMPORTANT_NOTES.md          # Важные заметки
└── README.md                   # Основная документация
```

## Описание компонентов

### Frontend (Разработка)
- **`frontend/css/style.css`** - Все стили приложения
- **`frontend/js/app.js`** - JavaScript логика
- **`frontend/README.md`** - Документация фронтенда
- **`frontend/sync.sh`** - Скрипт для копирования в static/

### Static (Продакшн)
- **`static/css/style.css`** - Копия стилей для Flask
- **`static/js/app.js`** - Копия JavaScript для Flask

### Backend
- **`app.py`** - Flask веб-сервер с API
- **`fragrantica_gologin_fixed.py`** - Основной парсер с Playwright
- **`ai_translator.py`** - ИИ переводчик на OpenAI
- **`simple_parser.py`** - Простой парсер (запасной)

### Конфигурация
- **`requirements.txt`** - Python зависимости
- **`runtime.txt`** - Версия Python
- **`render.yaml`** - Конфигурация Render
- **`DEPLOY.md`** - Инструкции по деплою

## Рабочий процесс

### Разработка фронтенда

1. **Редактируйте файлы в `frontend/`**
2. **Синхронизируйте с `static/`:**
   ```bash
   ./frontend/sync.sh
   ```
3. **Перезапустите Flask приложение**

### Структура API

```
GET  /                    # Главная страница
GET  /api/status         # Статус парсера
POST /api/start-parser   # Запуск парсера
POST /api/stop-parser    # Остановка парсера
GET  /api/start-ai-translator # Запуск ИИ переводчика
GET  /api/files          # Список файлов
GET  /api/download/<file> # Скачивание файла
GET  /health             # Проверка здоровья
```

## Особенности архитектуры

### Разделение фронтенда и бэкенда
- **Frontend** - отдельная папка для разработки
- **Static** - копия для продакшна
- **Templates** - HTML шаблоны Flask

### Модульность
- **CSS** - отдельный файл стилей
- **JavaScript** - отдельный файл логики
- **Python** - модульная структура парсеров

### Масштабируемость
- Легко добавлять новые стили
- Простое расширение JavaScript функционала
- Модульная архитектура Python кода 