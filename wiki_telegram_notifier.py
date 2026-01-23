import os
import requests
import json
from datetime import datetime, timezone
import logging
import sys
import re

# ------- Настройки из переменных окружения -------
WIKI_GRAPHQL_URL = os.getenv("WIKI_GRAPHQL_URL")
WIKI_API_TOKEN = os.getenv("WIKI_API_TOKEN")
SITE_URL = os.getenv("SITE_URL")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TELEGRAM_THREAD_ID = os.getenv("TELEGRAM_THREAD_ID")

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
CACHE_FILE = ".wiki_cache.json"

# ------- Логирование -------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/app.log")
    ]
)


# --- Вспомогательные функции ---
def escape_markdown(text):
    """Экранирует специальные символы MarkdownV2"""
    if not text:
        return ""
    # Список символов, которые нужно экранировать в MarkdownV2
    pattern = r"([_*\[\]()~`>#+\-={}.!\\])"
    return re.sub(pattern, r"\\\1", text)


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "message_thread_id": TELEGRAM_THREAD_ID,
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            logging.error("Ошибка отправки в Telegram: %s", response.text)
        else:
            logging.info("Сообщение успешно отправлено в Telegram")
    except Exception as e:
        logging.error("Не удалось отправить сообщение: %s", str(e))


def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning("Файл кэша не найден или повреждён: %s", str(e))
        return {}


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logging.debug("Кэш сохранён")


def fetch_wiki_pages():
    query = """
    {
      pages {
        list {
          id
          title
          description
          path
          createdAt
          updatedAt
        }
      }
    }
    """
    headers = {
        "Authorization": f"Bearer {WIKI_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(WIKI_GRAPHQL_URL, json={"query": query}, headers=headers)
        if response.status_code == 200:
            logging.debug("Успешно получены страницы из Wiki.js")
            return response.json()["data"]["pages"]["list"]
        else:
            logging.error("Ошибка при запросе к Wiki.js: %s", response.text)
    except Exception as e:
        logging.error("Ошибка подключения к Wiki.js: %s", str(e))
    return []


def check_wiki_updates():
    cache = load_cache()
    now = datetime.now(timezone.utc)
    cutoff_time = now.timestamp() - CHECK_INTERVAL_MINUTES * 60

    try:
        pages = fetch_wiki_pages()

        is_first_run = not bool(cache)

        for page in pages:
            page_id = str(page["id"])
            updated_at = datetime.fromisoformat(page["updatedAt"].replace("Z", "+00:00")).timestamp()

            cached = cache.get(page_id)

            # Экранируем заголовок и описание перед использованием
            escaped_title = escape_markdown(page['title'])
            escaped_description = escape_markdown(page['description']) if page.get('description') else ""
            description_text = f"\n\n{escaped_description}"
            link = f"{SITE_URL}{page['path']}"

            if is_first_run:
                cache[page_id] = {"createdAt": page["createdAt"], "updatedAt": page["updatedAt"]}
                continue

            if not cached:
                if len(description_text) > 2:
                    message = f'🆕 *Новая статья:*\n{escaped_title}{description_text}\n\n🔗 [Читать]({link})'
                else:
                    message = f'🆕 *Новая статья:*\n{escaped_title}\n🔗 [Читать]({link})'
                send_telegram_message(message)
                cache[page_id] = {"createdAt": page["createdAt"], "updatedAt": page["updatedAt"]}
                continue

            cached_updated_at = datetime.fromisoformat(cached["updatedAt"].replace("Z", "+00:00")).timestamp()
            if updated_at > cutoff_time and updated_at != cached_updated_at:
                if len(description_text) > 2:
                    message = f'*Обновлена статья:*\n{escaped_title}{description_text}\n\n🔗 [Читать]({link})'
                else:
                    message = f'*Обновлена статья:*\n{escaped_title}\n🔗 [Читать]({link})'
                send_telegram_message(message)
                cache[page_id]["updatedAt"] = page["updatedAt"]

        save_cache(cache)

    except Exception as e:
        logging.error("Ошибка при проверке обновлений Wiki: %s", str(e))


# --- Точка входа ---
if __name__ == "__main__":
    logging.info("Запуск проверки обновлений Wiki.js")
    check_wiki_updates()
    logging.info("Проверка завершена")
