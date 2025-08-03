# 🔥 GoLogin API - Официальная документация

## 📋 Обзор

Данная документация основана на официальной документации GoLogin:
- [Официальная документация](https://gologin.com/docs/api-reference/introduction/quickstart)
- [GitHub репозиторий](https://github.com/gologinapp/gologin)
- [Postman коллекция](https://documenter.getpostman.com/view/21126834/Uz5GnvaL)

## 🚀 Быстрый старт

### Установка зависимостей

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install gologin selenium webdriver-manager
```

### Получение API токена

1. Зайдите в [GoLogin Dashboard](https://app.gologin.com/)
2. Перейдите в Settings → API
3. Скопируйте ваш API токен

### Настройка переменных окружения

```bash
# Создайте файл .env
echo "GL_API_TOKEN=your_gologin_api_token_here" > .env
```

## 📚 Основные концепции

### 1. **Профили браузера**
- Каждый профиль представляет отдельный браузер
- Профили имеют уникальные fingerprint'ы
- Можно настраивать прокси, User-Agent, и другие параметры

### 2. **Запуск браузера**
- GoLogin запускает браузер через WebSocket
- Selenium подключается к запущенному браузеру
- Автоматическое управление профилями

### 3. **Очистка ресурсов**
- Профили автоматически удаляются после использования
- Браузеры корректно закрываются
- Освобождение памяти

## 🔧 API методы

### Инициализация

```python
from gologin import GoLogin

# Инициализация с токеном
gl = GoLogin({
    "token": os.environ.get('GL_API_TOKEN', 'your dev token'),
})
```

### Создание профиля

```python
# Создание профиля с случайным fingerprint
profile = gl.createProfileRandomFingerprint({ "os": "win" })
profile_id = profile.get('id')

# Добавление прокси к профилю
gl.addGologinProxyToProfile(profile_id, "us")
```

### Запуск браузера

```python
# Установка ID профиля
gl.setProfileId(profile_id)

# Запуск браузера
debugger_address = gl.start()

# Получение версии Chromium
chromium_version = gl.get_chromium_version()

# Установка webdriver
service = Service(ChromeDriverManager(driver_version=chromium_version).install())

# Настройки Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", debugger_address)

# Создание драйвера
driver = webdriver.Chrome(service=service, options=chrome_options)
```

### Очистка ресурсов

```python
# Закрытие браузера
driver.quit()

# Удаление профиля
gl.delete(profile_id)

# Остановка GoLogin
gl.stop()
```

## 🎯 Примеры использования

### Пример 1: Простой парсинг

```python
import os
import time
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Инициализация
gl = GoLogin({
    "token": os.environ.get('GL_API_TOKEN', 'your dev token'),
})

# Создание профиля
profile = gl.createProfileRandomFingerprint({ "os": "win" })
profile_id = profile.get('id')
gl.setProfileId(profile_id)

# Добавление прокси
gl.addGologinProxyToProfile(profile_id, "us")

# Запуск браузера
debugger_address = gl.start()
chromium_version = gl.get_chromium_version()
service = Service(ChromeDriverManager(driver_version=chromium_version).install())
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", debugger_address)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Использование браузера
driver.get("https://example.com")
time.sleep(5)

# Очистка
driver.quit()
gl.delete(profile_id)
gl.stop()
```

### Пример 2: Парсинг с обработкой ошибок

```python
class GoLoginParser:
    def __init__(self):
        self.gl = GoLogin({
            "token": os.environ.get('GL_API_TOKEN', 'your dev token'),
        })
        self.driver = None
        self.profile_id = None
    
    def create_profile(self):
        try:
            profile = self.gl.createProfileRandomFingerprint({ "os": "win" })
            self.profile_id = profile.get('id')
            self.gl.addGologinProxyToProfile(self.profile_id, "us")
            return self.profile_id
        except Exception as e:
            print(f"Ошибка создания профиля: {e}")
            raise
    
    def start_browser(self):
        try:
            self.gl.setProfileId(self.profile_id)
            debugger_address = self.gl.start()
            chromium_version = self.gl.get_chromium_version()
            service = Service(ChromeDriverManager(driver_version=chromium_version).install())
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver
        except Exception as e:
            print(f"Ошибка запуска браузера: {e}")
            raise
    
    def cleanup(self):
        try:
            if self.driver:
                self.driver.quit()
            if self.profile_id:
                self.gl.delete(self.profile_id)
            self.gl.stop()
        except Exception as e:
            print(f"Ошибка очистки: {e}")
```

## ⚙️ Конфигурация

### Настройки профиля

```python
profile_settings = {
    "os": "win",        # Операционная система
    "proxy": "us",      # Прокси (us, eu, asia)
    "fingerprint": "random"  # Тип fingerprint
}
```

### Настройки браузера

```python
browser_settings = {
    "headless": False,  # Показывать браузер
    "timeout": 30000,   # Таймаут в миллисекундах
    "viewport": {
        "width": 1920,
        "height": 1080
    }
}
```

### Настройки Selenium

```python
selenium_settings = {
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "script_timeout": 30
}
```

## 🚨 Обработка ошибок

### Типичные ошибки

1. **Неверный токен**
   ```
   Error: Invalid API token
   Solution: Проверьте правильность токена в переменных окружения
   ```

2. **Проблемы с профилем**
   ```
   Error: Profile not found
   Solution: Убедитесь, что профиль создан перед использованием
   ```

3. **Проблемы с браузером**
   ```
   Error: Browser connection failed
   Solution: Проверьте интернет соединение и доступность GoLogin серверов
   ```

### Рекомендации

1. **Всегда используйте try-finally для очистки**
2. **Проверяйте токен перед запуском**
3. **Используйте таймауты для операций**
4. **Логируйте ошибки для отладки**

## 📊 Производительность

### Временные характеристики

- **Создание профиля:** 2-5 секунд
- **Запуск браузера:** 10-20 секунд
- **Загрузка страницы:** 3-10 секунд
- **Очистка ресурсов:** 2-5 секунд

### Оптимизация

1. **Используйте headless режим** для ускорения
2. **Ограничивайте количество профилей** одновременно
3. **Используйте таймауты** для предотвращения зависаний
4. **Кэшируйте профили** для повторного использования

## 🔗 Полезные ссылки

- [Официальная документация](https://gologin.com/docs/api-reference/introduction/quickstart)
- [GitHub репозиторий](https://github.com/gologinapp/gologin)
- [Postman коллекция](https://documenter.getpostman.com/view/21126834/Uz5GnvaL)
- [MCP Server](https://github.com/gologinapp/gologin-mcp)

---

**Дата обновления:** 3 августа 2025  
**Версия:** 1.0  
**Основано на:** Официальной документации GoLogin 