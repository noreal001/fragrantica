# 🚀 Настройка Render с ChatGPT 3.5 API

## 📋 Шаги для деплоя на Render

### 1. Подключение репозитория
1. Зайдите на [render.com](https://render.com)
2. Нажмите "New +" → "Web Service"
3. Подключите GitHub репозиторий: `https://github.com/noreal001/fragrantica.git`

### 2. Настройка сервиса
- **Name:** `fragrantica-parser`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt && playwright install chromium`
- **Start Command:** `python3 app.py`
- **Health Check Path:** `/health`

### 3. Переменные окружения
В разделе "Environment Variables" добавьте:

| Key | Value | Описание |
|-----|-------|----------|
| `OPENAI_API_KEY` | `sk-your-api-key-here` | Ваш API ключ ChatGPT 3.5 |
| `SECRET_KEY` | `auto-generated` | Автоматически генерируется |

### 4. Получение API ключа ChatGPT 3.5
1. Зайдите на [platform.openai.com](https://platform.openai.com)
2. Войдите в аккаунт или создайте новый
3. Перейдите в "API Keys"
4. Нажмите "Create new secret key"
5. Скопируйте ключ (начинается с `sk-`)

### 5. Настройка в Render
1. В Render Dashboard найдите ваш сервис
2. Перейдите в "Environment"
3. Добавьте переменную:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-your-actual-api-key`

### 6. Деплой
1. Нажмите "Create Web Service"
2. Дождитесь завершения сборки (5-10 минут)
3. Получите URL вида: `https://your-app-name.onrender.com`

## 🌐 Использование веб-интерфейса

После деплоя у вас будет доступ к:

### Основные функции:
- ✅ **Запуск парсера** - кнопка "Запустить парсер"
- ✅ **ИИ перевод** - кнопка "Запустить ИИ переводчик"
- ✅ **Отслеживание прогресса** - реальное время
- ✅ **Скачивание файлов** - прямые ссылки на JSON
- ✅ **Мониторинг статуса** - автоматическое обновление

### API Endpoints:
- `GET /` - главная страница
- `GET /health` - проверка здоровья
- `GET /api/status` - статус парсера
- `POST /api/start-parser` - запуск парсера
- `POST /api/start-ai-translator` - запуск ИИ переводчика
- `GET /api/files` - список файлов
- `GET /api/download/<filename>` - скачивание файла

## ⚠️ Важные замечания

### Ограничения Render Free:
- **750 часов/месяц** - бесплатный план
- **512 MB RAM** - ограниченная память
- **0.1 CPU** - медленная обработка
- **1 GB Storage** - ограниченное хранилище

### Рекомендации:
- Используйте платный план для стабильной работы
- Мониторьте использование ресурсов
- API ключ ChatGPT стоит денег (около $0.002 за 1K токенов)

## 🔧 Устранение неполадок

### Ошибка "OpenAI API key not found"
- Проверьте переменную `OPENAI_API_KEY` в Render Dashboard
- Убедитесь, что ключ действителен и начинается с `sk-`

### Ошибка "Memory limit exceeded"
- Увеличьте план в Render
- Оптимизируйте код парсера

### Ошибка "Chrome not found"
- Build Command должен включать: `playwright install chromium`

## 📊 Мониторинг

### Логи в Render:
- Доступны в реальном времени
- Подробная информация об ошибках
- Метрики производительности

### Health Check:
- Endpoint: `/health`
- Проверка каждые 30 секунд
- Автоматический перезапуск при сбоях

---

**🎯 Готово к использованию!**

После настройки у вас будет полнофункциональный веб-интерфейс для парсера Fragrantica с ИИ переводом через ChatGPT 3.5. 