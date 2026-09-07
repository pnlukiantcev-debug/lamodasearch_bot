import os 
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fake_useragent import UserAgent

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Список брендов для проверки
TARGET_BRANDS = {
    "tommy-hilfiger": "Tommy Hilfiger",
    "calvin-klein": "Calvin Klein",
    "lacoste": "Lacoste",
    "levis": "Levi's",
    "vans": "Vans",
    "adidas": "Adidas",
    "nike": "Nike",
    "reebok": "Reebok",
}

MIN_DISCOUNT = 50

def send_email(text):
    if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_TO:
        print("Ошибка: Не заданы настройки почты в секретах GitHub")
        return
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = "🔥 Найдены скидки на Ламоде!"
    
    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка отправки почты: {e}")

def check_lamoda():
    ua = UserAgent()
    found_items = []
    
    print("Начинаем сканирование каталога Ламода...")

    for brand_key, brand_name in TARGET_BRANDS.items():
        print(f"Проверяем бренд: {brand_name}...")
        url = f"https://www.lamoda.ru/api/v1/recommendations/search?brand={brand_key}&discount_per=50&limit=30"
        
        headers = {
            "User-Agent": ua.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9",
            "Referer": "https://www.lamoda.ru/"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                
                for item in products:
                    discount = item.get("discount", 0)
                    if discount >= MIN_DISCOUNT:
                        title = item.get("name", "Товар")
                        link = "https://www.lamoda.ru" + item.get("url", "")
                        old_price = item.get("price", 0)
                        new_price = item.get("price_discount", 0)
                        
                        found_items.append({
                            "brand": brand_name,
                            "title": title,
                            "old_price": old_price,
                            "new_price": new_price,
                            "discount": discount,
                            "link": link
                        })
        except Exception as e:
            print(f"Ошибка запроса для {brand_name}: {e}")
            
        time.sleep(2)

    if found_items:
        report = f"🔥 Найдены скидки от {MIN_DISCOUNT}%:\n\n"
        for item in found_items[:15]:
            report += f"▪️ {item['brand']} — {item['title']}\n"
            report += f" Цена: {item['old_price']}₽ ➡️ {item['new_price']}₽ (-{item['discount']}%)\n"
            report += f" Ссылка: {item['link']}\n\n"
    else:
        report = "Проверка завершена. Сегодня новых товаров со скидкой >= 50% по вашим брендам не найдено."

    send_email(report)

if __name__ == "__main__":
    check_lamoda()
