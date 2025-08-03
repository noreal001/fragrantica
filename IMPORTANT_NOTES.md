# ВАЖНЫЕ ПОМЕТКИ - Fragrantica Parser

## 🚨 КРИТИЧЕСКИ ВАЖНО

### Playwright ОБЯЗАТЕЛЕН
- **БЕЗ playwright парсер НЕ РАБОТАЕТ**
- Сайт имеет защиту от парсинга
- Только playwright может обойти Cloudflare защиту
- НИКОГДА не удалять playwright из зависимостей

### Зависимости
```txt
playwright==1.35.0  # ОБЯЗАТЕЛЬНО
greenlet==2.0.2     # Нужен для playwright
```

### Проблемы с greenlet
- greenlet может не компилироваться на Python 3.13+
- Использовать Python 3.9.18 или 3.10.12
- Если ошибки - попробовать более старые версии greenlet

### Render Deployment
- Build Command: `pip install -r requirements.txt && playwright install chromium`
- Python Version: 3.9.18 (стабильная)
- Обязательно устанавливать Chromium браузер

### Альтернативы playwright НЕТ
- requests + beautifulsoup4 НЕ РАБОТАЮТ
- selenium может работать, но сложнее
- playwright - единственное решение для обхода защиты

## 🔧 Технические детали

### Почему нужен playwright
1. Cloudflare защита блокирует обычные requests
2. Сайт требует JavaScript рендеринг
3. Нужна эмуляция реального браузера
4. Антидетект настройки для обхода блокировок

### Настройки playwright в коде
```python
# Антидетект настройки
args=[
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-blink-features=AutomationControlled',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-images',
    '--disable-javascript',
    '--user-agent=Mozilla/5.0...'
]
```

## 📝 История проблем

### Проблема 1: greenlet compilation
- Решение: Python 3.9.18 + greenlet 2.0.2
- Флаг: `--only-binary=greenlet`

### Проблема 2: playwright install
- Решение: `playwright install chromium`
- Обязательно в build command

### Проблема 3: Content-Type
- Решение: Правильные headers в JavaScript
- `'Content-Type': 'application/json'`

## ✅ Чек-лист для деплоя

- [ ] requirements.txt содержит playwright
- [ ] requirements.txt содержит greenlet
- [ ] render.yaml имеет правильный buildCommand
- [ ] Python версия 3.9.18
- [ ] playwright install chromium в buildCommand
- [ ] Frontend отправляет правильные headers

## 🚫 ЧТО НЕ ДЕЛАТЬ

- ❌ Удалять playwright из зависимостей
- ❌ Использовать Python 3.13+ без тестирования
- ❌ Убирать playwright install из buildCommand
- ❌ Пытаться парсить без браузера
- ❌ Игнорировать ошибки greenlet

## 📞 Контакты

**Bahur Inc.** - AI Translation Technology
Парсер работает ТОЛЬКО с playwright! 