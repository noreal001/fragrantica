let isProcessing = false;

async function startParser() {
    if (isProcessing) return;
    isProcessing = true;
    
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const loading = document.getElementById('loading');
    const progressContainer = document.getElementById('progressContainer');
    const status = document.getElementById('status');
    const newsCard = document.getElementById('newsCard');
    
    startBtn.disabled = true;
    stopBtn.disabled = false;
    loading.style.display = 'block';
    progressContainer.style.display = 'block';
    newsCard.classList.remove('show');
    status.textContent = 'Запуск парсера...';
    status.className = 'status running';
    
    try {
        const settings = {
            newsCount: document.getElementById('newsCount').value,
            targetLanguage: document.getElementById('targetLanguage').value
        };
        
        const response = await fetch('/api/start-parser', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Ошибка запуска парсера');
        }
        
        status.textContent = 'Парсер запущен';
        
        // Monitor progress
        let progress = 0;
        const progressInterval = setInterval(async () => {
            try {
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();
                
                                if (statusData.running) {
                    progress = Math.min(progress + 5, 85);
                    document.getElementById('progressFill').style.width = progress + '%';
                    document.getElementById('progressText').textContent = statusData.message;
                } else if (statusData.result_file) {
                            clearInterval(progressInterval);
                            progress = 100;
                            document.getElementById('progressFill').style.width = '100%';
                            document.getElementById('progressText').textContent = 'Парсинг завершен!';
                            
                            // Ждем немного перед получением результатов
                            await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    // Start AI translator
                    status.textContent = 'Перевод с помощью ИИ...';
                    const translatorResponse = await fetch('/api/start-ai-translator');
                    const translatorData = await translatorResponse.json();
                    if (!translatorResponse.ok) {
                        throw new Error(translatorData.error || 'Ошибка перевода');
                    }
                    
                    // Get result
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    const filesResponse = await fetch('/api/files');
                    const filesData = await filesResponse.json();
                    if (filesData.files && filesData.files.length > 0) {
                        const latestFile = filesData.files[0];
                        const downloadResponse = await fetch(`/api/download/${latestFile.name}`);
                        const newsData = await downloadResponse.json();
                        if (newsData.articles && newsData.articles.length > 0) {
                            const latestArticle = newsData.articles[0];
                            displayNews(latestArticle);
                            status.textContent = 'Новость успешно получена!';
                            status.className = 'status';
                        } else {
                            throw new Error('Новости не найдены');
                        }
                    } else {
                        throw new Error('Файлы не найдены');
                    }
                }
            } catch (error) {
                clearInterval(progressInterval);
                throw error;
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error:', error);
        let errorMessage = error.message;
        
        // Более информативные сообщения об ошибках
        if (errorMessage.includes('greenlet')) {
            errorMessage = 'Ошибка: Модуль greenlet не найден. Парсер не может запуститься.';
        } else if (errorMessage.includes('playwright')) {
            errorMessage = 'Ошибка: Проблема с браузером Playwright.';
        } else if (errorMessage.includes('cloudflare')) {
            errorMessage = 'Ошибка: Сайт заблокировал доступ. Попробуйте позже.';
        } else if (errorMessage.includes('timeout') || errorMessage.includes('Таймаут')) {
            errorMessage = 'Ошибка: Превышено время ожидания. Парсер завис. Попробуйте еще раз.';
        } else if (errorMessage.includes('Файл не найден')) {
            errorMessage = 'Ошибка: Файл с результатами не создан. Попробуйте еще раз.';
        }
        
        status.textContent = errorMessage;
        status.className = 'status error';
    } finally {
        isProcessing = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        loading.style.display = 'none';
        progressContainer.style.display = 'none';
    }
}

async function stopParser() {
    try {
        const response = await fetch('/api/stop-parser', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('status').textContent = 'Парсер остановлен';
            document.getElementById('status').className = 'status';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        } else {
            throw new Error(data.error || 'Ошибка остановки парсера');
        }
    } catch (error) {
        console.error('Error stopping parser:', error);
        document.getElementById('status').textContent = `Ошибка остановки: ${error.message}`;
        document.getElementById('status').className = 'status error';
    }
}

function displayNews(article) {
    const newsCard = document.getElementById('newsCard');
    const newsTitle = document.getElementById('newsTitle');
    const newsDate = document.getElementById('newsDate');
    const newsContent = document.getElementById('newsContent');
    
    // Отображаем заголовок (оригинал и перевод)
    let titleHtml = `<div class="news-title-original">${article.title || 'Новость'}</div>`;
    if (article.title_ru) {
        titleHtml += `<div class="news-title-translated">🇷🇺 ${article.title_ru}</div>`;
    }
    newsTitle.innerHTML = titleHtml;
    
    // Дата
    const date = new Date();
    newsDate.textContent = date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Содержание (оригинал и перевод)
    let contentHtml = '';
    
    // Оригинальное содержание
    if (article.content) {
        contentHtml += `<div class="news-content-section">
            <h4>📝 Оригинал:</h4>
            <div class="news-content-original">${article.content.replace(/\n/g, '<br><br>')}</div>
        </div>`;
    }
    
    // Переведенное содержание
    if (article.content_ru) {
        contentHtml += `<div class="news-content-section">
            <h4>🇷🇺 Перевод:</h4>
            <div class="news-content-translated">${article.content_ru.replace(/\n/g, '<br><br>')}</div>
        </div>`;
    }
    
    // Полное содержание если есть
    if (article.full_content) {
        contentHtml += `<div class="news-content-section">
            <h4>📄 Полное содержание:</h4>
            <div class="news-content-full">${article.full_content.replace(/\n/g, '<br><br>')}</div>
        </div>`;
    }
    
    // Ссылка на оригинал
    if (article.link) {
        contentHtml += `<div class="news-link-section">
            <a href="${article.link}" target="_blank" class="news-link">🔗 Читать оригинал</a>
        </div>`;
    }
    
    if (!contentHtml) {
        contentHtml = '<div class="news-content-empty">Содержание новости недоступно</div>';
    }
    
    newsContent.innerHTML = contentHtml;
    newsCard.classList.add('show');
}

// Check status every 10 seconds
setInterval(async () => {
    if (!isProcessing) {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            const status = document.getElementById('status');
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            
            if (data.running) {
                status.textContent = data.message;
                status.className = 'status running';
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                status.textContent = 'Готов к работе';
                status.className = 'status';
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        } catch (error) {
            console.error('Status update error:', error);
        }
    }
}, 10000);

async function resetStatus() {
    try {
        const response = await fetch('/api/reset-status', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('status').textContent = 'Статус сброшен';
            document.getElementById('status').className = 'status';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            console.log('Статус сброшен:', data.message);
        } else {
            throw new Error(data.error || 'Ошибка сброса статуса');
        }
    } catch (error) {
        console.error('Error resetting status:', error);
        document.getElementById('status').textContent = `Ошибка сброса: ${error.message}`;
        document.getElementById('status').className = 'status error';
    }
}

async function testParser() {
    try {
        document.getElementById('status').textContent = 'Тестирование парсера...';
        document.getElementById('status').className = 'status running';
        
        const response = await fetch('/api/test-parser', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('status').textContent = 'Тест парсера завершен успешно!';
            document.getElementById('status').className = 'status';
            console.log('Тест парсера:', data.message);
        } else {
            throw new Error(data.error || 'Ошибка тестирования парсера');
        }
    } catch (error) {
        console.error('Error testing parser:', error);
        document.getElementById('status').textContent = `Ошибка теста: ${error.message}`;
        document.getElementById('status').className = 'status error';
    }
}

async function clearFiles() {
    try {
        const response = await fetch('/api/clear-files', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('status').textContent = 'Файлы очищены';
            document.getElementById('status').className = 'status';
            console.log('Файлы очищены:', data.message);
        } else {
            throw new Error(data.error || 'Ошибка очистки файлов');
        }
    } catch (error) {
        console.error('Error clearing files:', error);
        document.getElementById('status').textContent = `Ошибка очистки: ${error.message}`;
        document.getElementById('status').className = 'status error';
    }
} 