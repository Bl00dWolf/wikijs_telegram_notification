# wikijs_telegram_notification

# Цель приложения

Данное приложение позволяет следить за изменениями и новыми статьями в WikiJS и присылает уведомление в телеграм, если появилась новая статья или была изменена \ обновлена существующая. 

Для работы нужен АПИ ключ от WikiJS, нужен телеграм бот и канал \ топик в который будут приходить уведомления. 

Docker контейнер основан на python 3.11 контейнере, дополнительно треубется модуль `requests` (устанавливается автоматически при сборке контейнера).

Первый запуск приложения происходит построение базы текущих статей в кэш. Затем уже происходит мониторинг на новые \ обновленные статьи.

# Структура проекта

```
wikijs_telegram_notification/
│
├── .env                   # Настройки через переменные окружения
├── Dockerfile             # Описание сборки Docker-образа
├── docker-compose.yml     # Конфиг для запуска через docker-compose
├── requirements.txt       # Зависимости Python
├── wiki_telegram_notifier.py  # Основной скрипт на Python
├── .wiki_cache.json       # Кэш статей — создаётся автоматически
└── logs/                  # Папка для логов
   └── app.log             # Файл логов — создаётся после первого запуска
```

## Пример .env файла
```bash
WIKI_GRAPHQL_URL=http://111.11.1.11/graphql
WIKI_API_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6I
SITE_URL=http://wikijs.int/

TELEGRAM_BOT_TOKEN=7:AAEmoI
TELEGRAM_CHANNEL_ID=-1002131673576
TELEGRAM_THREAD_ID=16151

CHECK_INTERVAL_MINUTES=5
```

В файле .env указываются основные переменные для работы:

`WIKI_GRAPHQL_URL` - адрес до `graphql` у WikiJS

`WIKI_API_TOKEN` - API токен от `WikiJS`

`SITE_URL` - адрес до `WikiJS`, он будет использован в ссылке в сообщении на статью, которую пришлет бот

`TELEGRAM_BOT_TOKEN` - API токен от телеграм бота

`TELEGRAM_CHANNEL_ID` - ID канала в который присылать сообщение от бота

`TELEGRAM_THREAD_ID` - ID топика (если есть) в который присылать сообщение от бота

`CHECK_INTERVAL_MINUTES` - как часто проверять WikiJS на новые или измененные статьи.


# Запуск

После задачи .env файла бот готов к запуску через команду
``` bash
docker compose up -d
```
Просмотр логов бота доступен через
```bash
docker compose logs -f
```


