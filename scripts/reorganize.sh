#!/bin/bash

# Скрипт реорганизации проекта Fragrantica Parser
# Перемещает файлы в новую структуру на основе официальной документации GoLogin

echo "🚀 Начинаю реорганизацию проекта..."

# Создание папок если не существуют
mkdir -p parsers/gologin parsers/simple parsers/legacy
mkdir -p web/static/css web/static/js web/templates
mkdir -p docs/api docs/deployment docs/guides
mkdir -p config utils data/output data/logs
mkdir -p scripts

echo "📁 Папки созданы"

# Перемещение парсеров
echo "📦 Перемещаю парсеры..."

# GoLogin парсеры
if [ -f "fragrantica_gologin_parser.py" ]; then
    mv fragrantica_gologin_parser.py parsers/gologin/gologin_parser.py
    echo "✅ Перемещен: fragrantica_gologin_parser.py → parsers/gologin/gologin_parser.py"
fi

if [ -f "fragrantica_gologin_correct.py" ]; then
    mv fragrantica_gologin_correct.py parsers/legacy/gologin_correct.py
    echo "✅ Перемещен: fragrantica_gologin_correct.py → parsers/legacy/gologin_correct.py"
fi

if [ -f "fragrantica_gologin_fixed.py" ]; then
    mv fragrantica_gologin_fixed.py parsers/legacy/gologin_fixed.py
    echo "✅ Перемещен: fragrantica_gologin_fixed.py → parsers/legacy/gologin_fixed.py"
fi

if [ -f "fragrantica_simple_gologin.py" ]; then
    mv fragrantica_simple_gologin.py parsers/legacy/simple_gologin.py
    echo "✅ Перемещен: fragrantica_simple_gologin.py → parsers/legacy/simple_gologin.py"
fi

# Простые парсеры
if [ -f "simple_parser.py" ]; then
    mv simple_parser.py parsers/simple/simple_parser.py
    echo "✅ Перемещен: simple_parser.py → parsers/simple/simple_parser.py"
fi

if [ -f "test_parser.py" ]; then
    mv test_parser.py parsers/simple/test_parser.py
    echo "✅ Перемещен: test_parser.py → parsers/simple/test_parser.py"
fi

# Веб-интерфейс
echo "🌐 Перемещаю веб-файлы..."

if [ -f "app.py" ]; then
    mv app.py web/app.py
    echo "✅ Перемещен: app.py → web/app.py"
fi

if [ -d "templates" ]; then
    mv templates/* web/templates/ 2>/dev/null || true
    echo "✅ Перемещены: templates → web/templates"
fi

if [ -d "static" ]; then
    mv static/* web/static/ 2>/dev/null || true
    echo "✅ Перемещены: static → web/static"
fi

# Документация
echo "📚 Перемещаю документацию..."

if [ -f "GOLOGIN_PARSER.md" ]; then
    mv GOLOGIN_PARSER.md docs/api/gologin_parser.md
    echo "✅ Перемещен: GOLOGIN_PARSER.md → docs/api/gologin_parser.md"
fi

if [ -f "DEPLOY.md" ]; then
    mv DEPLOY.md docs/deployment/deploy.md
    echo "✅ Перемещен: DEPLOY.md → docs/deployment/deploy.md"
fi

if [ -f "TESTING.md" ]; then
    mv TESTING.md docs/guides/testing.md
    echo "✅ Перемещен: TESTING.md → docs/guides/testing.md"
fi

if [ -f "IMPORTANT_NOTES.md" ]; then
    mv IMPORTANT_NOTES.md docs/guides/important_notes.md
    echo "✅ Перемещен: IMPORTANT_NOTES.md → docs/guides/important_notes.md"
fi

if [ -f "PROJECT_STRUCTURE.md" ]; then
    mv PROJECT_STRUCTURE.md docs/guides/project_structure.md
    echo "✅ Перемещен: PROJECT_STRUCTURE.md → docs/guides/project_structure.md"
fi

# Утилиты
echo "🔧 Перемещаю утилиты..."

if [ -f "ai_translator.py" ]; then
    mv ai_translator.py utils/translator.py
    echo "✅ Перемещен: ai_translator.py → utils/translator.py"
fi

if [ -f "fix_status.py" ]; then
    mv fix_status.py utils/fix_status.py
    echo "✅ Перемещен: fix_status.py → utils/fix_status.py"
fi

if [ -f "reset_status.py" ]; then
    mv reset_status.py utils/reset_status.py
    echo "✅ Перемещен: reset_status.py → utils/reset_status.py"
fi

# Данные
echo "📊 Перемещаю данные..."

# Перемещение JSON файлов
for file in fragrantica_simple_news_*.json; do
    if [ -f "$file" ]; then
        mv "$file" data/output/
        echo "✅ Перемещен: $file → data/output/"
    fi
done

# Перемещение логов
if [ -f "fragrantica_simple_parser.log" ]; then
    mv fragrantica_simple_parser.log data/logs/
    echo "✅ Перемещен: fragrantica_simple_parser.log → data/logs/"
fi

if [ -f "parser_status.json" ]; then
    mv parser_status.json data/
    echo "✅ Перемещен: parser_status.json → data/"
fi

# Конфигурация
echo "⚙️ Перемещаю конфигурацию..."

if [ -f "render.yaml" ]; then
    mv render.yaml config/
    echo "✅ Перемещен: render.yaml → config/"
fi

if [ -f ".render.yaml" ]; then
    mv .render.yaml config/
    echo "✅ Перемещен: .render.yaml → config/"
fi

if [ -f "runtime.txt" ]; then
    mv runtime.txt config/
    echo "✅ Перемещен: runtime.txt → config/"
fi

# Создание .env.example
echo "🔐 Создаю .env.example..."
cat > .env.example << EOF
# GoLogin API токен (обязательно)
GL_API_TOKEN=your_gologin_api_token_here

# Настройки Flask
FLASK_ENV=development
FLASK_DEBUG=1

# Настройки логирования
LOG_LEVEL=INFO
EOF

echo "✅ Создан: .env.example"

# Обновление README
echo "📝 Обновляю README..."
if [ -f "README_NEW.md" ]; then
    mv README_NEW.md README.md
    echo "✅ Обновлен: README.md"
fi

# Создание .gitignore для новой структуры
echo "🚫 Обновляю .gitignore..."
cat >> .gitignore << EOF

# Данные
data/output/*.json
data/logs/*.log

# Конфигурация
.env

# Виртуальное окружение
venv/
env/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# IDE
.vscode/
.idea/
*.swp
*.swo

# Системные файлы
.DS_Store
Thumbs.db
EOF

echo "✅ Обновлен: .gitignore"

# Создание скрипта установки
echo "📦 Создаю скрипт установки..."
cat > scripts/install.sh << 'EOF'
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
EOF

chmod +x scripts/install.sh
echo "✅ Создан: scripts/install.sh"

# Создание скрипта запуска
echo "▶️ Создаю скрипт запуска..."
cat > scripts/run.sh << 'EOF'
#!/bin/bash

echo "🚀 Запуск Fragrantica Parser..."

# Активация виртуального окружения
source venv/bin/activate

# Запуск приложения
python web/app.py
EOF

chmod +x scripts/run.sh
echo "✅ Создан: scripts/run.sh"

echo ""
echo "🎉 Реорганизация завершена!"
echo ""
echo "📁 Новая структура проекта:"
echo "├── parsers/          # Парсеры"
echo "├── web/             # Веб-интерфейс"
echo "├── docs/            # Документация"
echo "├── config/          # Конфигурация"
echo "├── utils/           # Утилиты"
echo "├── data/            # Данные"
echo "└── scripts/         # Скрипты"
echo ""
echo "🚀 Для запуска:"
echo "1. ./scripts/install.sh  # Установка"
echo "2. ./scripts/run.sh      # Запуск"
echo ""
echo "📚 Документация: docs/"
echo "🔧 Конфигурация: config/" 