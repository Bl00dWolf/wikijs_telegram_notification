FROM python:3.11-slim

LABEL maintainer="Bl00dWolf"

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт
COPY wiki_telegram_notifier.py .

# Создаём директорию для логов
RUN mkdir -p logs

# Создаём .wiki_cache.json, если его нет
RUN sh -c 'cat .wiki_cache.json 2>/dev/null || echo "{}" > .wiki_cache.json'

# Запуск скрипта каждые N минут
CMD ["sh", "-c", "while true; do python3 wiki_telegram_notifier.py; sleep $(( $(echo $CHECK_INTERVAL_MINUTES)*60 )); done"]
