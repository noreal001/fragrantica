# Fragrantica Parser - Bahur Inc.

🚨 **ВАЖНО: Парсер работает ТОЛЬКО с playwright!**

## Описание

Веб-интерфейс для парсера новостей Fragrantica с автоматическим переводом с помощью ИИ. Проект разработан для **Bahur Inc.**.

## 🚨 КРИТИЧЕСКИ ВАЖНО

### Playwright ОБЯЗАТЕЛЕН
- **БЕЗ playwright парсер НЕ РАБОТАЕТ**
- Сайт имеет Cloudflare защиту от парсинга
- Только playwright может обойти защиту
- НИКОГДА не удалять playwright из зависимостей

### Зависимости
```txt
playwright==1.35.0  # ОБЯЗАТЕЛЬНО
greenlet==2.0.2     # Нужен для playwright
flask==2.3.3
beautifulsoup4==4.12.2
requests==2.31.0
deep-translator==1.11.4
openai==0.28.1
```

## 🚫 ЧТО НЕ ДЕЛАТЬ

- ❌ Удалять playwright из зависимостей
- ❌ Использовать Python 3.13+ без тестирования
- ❌ Убирать playwright install из buildCommand
- ❌ Пытаться парсить без браузера
- ❌ Игнорировать ошибки greenlet

## 🚀 Быстрый старт

### Локальная разработка

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

4. **Запустите приложение:**
```bash
python app.py
```

5. **Откройте браузер:**
```
http://localhost:5000
```

### Render Deployment

**Настройки Render:**

- **Build Command:** `pip install -r requirements.txt && playwright install chromium`
- **Start Command:** `python3 app.py`
- **Python Version:** 3.9.18

**Environment Variables:**
- `OPENAI_API_KEY` - ваш OpenAI API ключ
- `SECRET_KEY` - секретный ключ Flask (генерируется автоматически)

## 🎨 Интерфейс

- **Минималистичный дизайн** в стиле Vercel/Render
- **Черный фон** с белым текстом
- **Настройки парсера** - количество новостей, язык перевода
- **Кнопки управления** - Запустить/Остановить парсер
- **Прогресс-бар** с анимацией
- **Отображение новостей** с переводом

## 🔧 API Endpoints

- `GET /` - главная страница
- `GET /api/status` - статус парсера
- `POST /api/start-parser` - запуск парсера с настройками
- `POST /api/stop-parser` - остановка парсера
- `GET /api/start-ai-translator` - запуск ИИ переводчика
- `GET /api/files` - список доступных файлов
- `GET /api/download/<filename>` - скачивание файла
- `GET /health` - проверка здоровья приложения

## 📝 История проблем и решений

### Проблема 1: greenlet compilation
- **Ошибка:** `ModuleNotFoundError: No module named 'greenlet'`
- **Решение:** Python 3.9.18 + greenlet 2.0.2
- **Флаг:** `--only-binary=greenlet`

### Проблема 2: playwright install
- **Ошибка:** `bash: line 1: playwright: command not found`
- **Решение:** `playwright install chromium` в buildCommand

### Проблема 3: Content-Type
- **Ошибка:** `415 Unsupported Media Type`
- **Решение:** Правильные headers в JavaScript
- **Код:** `'Content-Type': 'application/json'`

## ✅ Чек-лист для деплоя

- [ ] requirements.txt содержит playwright
- [ ] requirements.txt содержит greenlet
- [ ] render.yaml имеет правильный buildCommand
- [ ] Python версия 3.9.18
- [ ] playwright install chromium в buildCommand
- [ ] Frontend отправляет правильные headers

## 🛠 Технологии

- **Backend:** Flask, Python 3.9.18
- **Парсинг:** Playwright (ОБЯЗАТЕЛЬНО), BeautifulSoup
- **Перевод:** OpenAI GPT, Deep Translator
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render

## 📞 Контакты

**Bahur Inc.** - AI Translation Technology

---

**Помните: Парсер работает ТОЛЬКО с playwright!** 