#!/bin/bash

# Скрипт для синхронизации файлов фронтенда с папкой static

echo "Синхронизация файлов фронтенда..."

# Копируем файлы из frontend в static
cp -r css/* ../static/css/
cp -r js/* ../static/js/

echo "Файлы успешно скопированы в static/"
echo "Структура обновлена:"
echo "  - static/css/style.css"
echo "  - static/js/app.js" 