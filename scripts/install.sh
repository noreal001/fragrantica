#!/bin/bash

echo "🚀 Установка Fragrantica Parser..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.9+"
    exit 1
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активация окружения
echo "🔧 Активация окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

# Создание .env если не существует
if [ ! -f ".env" ]; then
    echo "🔐 Создание .env файла..."
    cp .env.example .env
    echo "⚠️  Не забудьте добавить ваш GoLogin токен в .env файл!"
fi

echo "✅ Установка завершена!"
echo "🚀 Запустите: python web/app.py"
