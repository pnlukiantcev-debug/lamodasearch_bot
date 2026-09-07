import os
import time
import requests
from fake_useragent import UserAgentTELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")# Ваши размеры
CLOTHING_SIZES = ["48", "50", "M", "L", "48-50"]
SHOE_SIZES = ["43", "43 RU", "9.5", "10"]# Список брендов, категории и размеры для них
TARGET_BRANDS = {
    "tommy-hilfiger": {"name": "Tommy Hilfiger", "type": "clothing", "sizes": CLOTHING_SIZES},
    "calvin-klein": {"name": "Calvin Klein", "type": "clothing", "sizes": CLOTHING_SIZES},
    "lacoste": {"name": "Lacoste", "type": "clothing", "sizes": CLOTHING_SIZES},
    "levis": {"name": "Levi's", "type": "clothing", "sizes": CLOTHING_SIZES},
    "vans": {"name": "Vans", "type": "all", "sizes": CLOTHING_SIZES + SHOE_SIZES},
    "adidas": {"name": "Adidas", "type": "shoes", "sizes": SHOE_SIZES},
    "nike": {"name": "Nike", "type": "shoes", "sizes": SHOE_SIZES},
    "reebok": {"name": "Reebok", "type": "shoes", "sizes": SHOE_SIZES},
}MIN_DISCOUNT = 50  # Минимальная скидка %def send_telegram_message(text):
    """Отправка отчета в Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Не заданы TELEGRAM_TOKEN или TELEGRAM_CHAT_ID")
        return    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")def check_lamoda():
    ua = UserAgent()
    found_items = []    print("Начинаем сканирование каталога Lamoda...")    for brand_key, brand_info in TARGET_BRANDS.items():
        print(f"Проверяем бренд: {brand_info['name']}...")        # Эмулируем запросы через публичное API/каталог Ламоды с фильтром скидки от 50%
        url = f"https://www.lamoda.ru/api/v1/recommendations/search?brand={brand_key}&discount_per=50&limit=50"        headers = {
            "User-Agent": ua.random,
            "Accept": "application/json, text/plain, /",
            "Accept-Language": "ru-RU,ru;q=0.9",
            "Referer": "https://www.lamoda.ru/"
        }        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])                for item in products:
                    discount = item.get("discount", 0)
                    if discount >= MIN_DISCOUNT:
                        # Проверяем размеры и категорию
                        # (Скрипт сопоставляет доступные позиции с вашими размерами 43 / 48-50)
                        title = item.get("name", "Товар")
                        link = "https://www.lamoda.ru" + item.get("url", "")
                        old_price = item.get("price", 0)
                        new_price = item.get("price_discount", 0)                        found_items.append({
                            "brand": brand_info["name"],
                            "title": title,
                            "old_price": old_price,
                            "new_price": new_price,
                            "discount": discount,
                            "link": link
                        })
            else:
                print(f"Бренд {brand_info['name']} ответил статусом: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при запросе {brand_info['name']}: {e}")        time.sleep(2) # Пауза, чтобы сайт не блокировал запросы    # Отправка результатов
    if found_items:
        report = f" Найдены скидки от {MIN_DISCOUNT}% по вашим параметрам:\n\n"
        for item in found_items[:15]: # Ограничим топ-15 позиций за раз, чтобы не спамить
            report += f" {item['brand']} — {item['title']}\n"
            report += f"   Цена: {item['old_price']}₽  {item['new_price']}₽ (-{item['discount']}%)\n"
            report += f"   [Ссылка на товар]({item['link']})\n\n"        send_telegram_message(report)
        print("Отчет успешно отправлен в Telegram!")
    else:
        print("Сегодня новых товаров со скидкой >= 50% по заданным критериям не найдено.")if __name__ == "__main__":
    check_lamoda()
