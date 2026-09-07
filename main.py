import os
import time
import requests
from fake_useragent import UserAgent
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CLOTHING_SIZES = ["48", "50", "M", "L"]
SHOE_SIZES = ["43", "43 RU", "9.5 UK", "10 US"]
TARGET_BRANDS = {
    "Tommy Hilfiger": {"type": "clothing", "sizes": CLOTHING_SIZES},
    "Calvin Klein": {"type": "clothing", "sizes": CLOTHING_SIZES},
    "Lacoste": {"type": "clothing", "sizes": CLOTHING_SIZES},
    "Levi's": {"type": "clothing", "sizes": CLOTHING_SIZES},
    "Vans": {"type": "all", "sizes": CLOTHING_SIZES + SHOE_SIZES},
    "Adidas": {"type": "shoes", "sizes": SHOE_SIZES},
    "Nike": {"type": "shoes", "sizes": SHOE_SIZES},
    "Reebok": {"type": "shoes", "sizes": SHOE_SIZES},
}
def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Не заданы TELEGRAM_TOKEN или TELEGRAM_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка: {e}")
def check_lamoda():
    found_items = []
    ua = UserAgent()
    print("Запуск проверки...")
    # Здесь скрипт будет обходить бренды по вашему списку
    for brand_name, settings in TARGET_BRANDS.items():
        time.sleep(1)
    if found_items:
        report = "🔥 Найдены скидки > 50% для вас:\n\n"
        for item in found_items:
            report += f"▪️ {item['brand']} — {item['title']} ({item['size']})\n"
        send_telegram_message(report)
    else:
        print("Пока ничего нового по заданным критериям не найдено.")
if __name__ == "__main__":
    check_lamoda()
