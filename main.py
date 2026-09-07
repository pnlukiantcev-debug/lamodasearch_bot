import os 
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fake_useragent import UserAgent

EMAIL_USER = os.getenv("EMAIL_USER") # Ваша почта (откуда и куда отправляем)
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # Пароль приложения
EMAIL_TO = os.getenv("EMAIL_TO") # Почта получателя

CLOTHING_SIZES = ["48", "50", "M", "L", "48-50"]
SHOE_SIZES = ["43", "43 RU", "9.5", "10"]

TARGET_BRANDS = {
    "tommy-hilfiger": {"name": "Tommy Hilfiger", "type": "clothing", "sizes": CLOTHING_SIZES},
    "calvin-klein": {"name": "Calvin Klein", "type": "clothing", "sizes": CLOTHING_SIZES},
    "lacoste": {"name": "Lacoste", "type": "clothing", "sizes": CLOTHING_SIZES},
    "levis": {"name": "Levi's", "type": "clothing", "sizes": CLOTHING_SIZES},
    "vans": {"name": "Vans", "type": "all", "sizes": CLOTHING_SIZES + SHOE_SIZES},
    "adidas": {"name": "Adidas", "type": "shoes", "sizes": SHOE_SIZES},
    "nike": {"name": "Nike", "type": "shoes", "sizes": SHOE_SIZES},
    "reebok": {"name": "Reebok", "type": "shoes", "sizes": SHOE_SIZES},
}

MIN_DISCOUNT = 50

def send_email(text):
    if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_TO:
        print("Не заданы настройки почты в секретах GitHub")
        return
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = "🔥 Новые скидки на Lamoda (от 50%)"
    
    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    
    try:
        # Настройка для Gmail (если используете Яндекс, смените на smtp.yandex.ru и порт 465)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
        print("Письмо успешно отправлено на почту!")
    except Exception as e:
        print(f"Ошибка отправки почты: {e}")

def check_lamoda():
    ua = UserAgent()
    found_items = []
    
    print("Начинаем сканирование каталога Lamoda...")

    for brand_key, brand_info in TARGET_BRANDS.items():
        print(f"Проверяем бренд: {brand_info['name']}...")
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
                            "brand": brand_info["name"],
                            "title": title,
                            "old_price": old_price,
                            "new_price": new_price,
                            "discount": discount,
                            "link": link
                        })
        except Exception as e:
            print(f"Ошибка: {e}")
            
        time.sleep(2)

    if found_items:
        report = f"Найдены скидки от {MIN_DISCOUNT}%:\n\n"
        for item in found_items[:10]:
            report += f"- {item['brand']} — {item['title']}\n"
            report += f" Цена: {item['old_price']}₽ -> {item['new_price']}₽ (-{item['discount']}%)\n"
            report += f" Ссылка: {item['link']}\n\n"
        send_email(report)
    else:
        print("Пока ничего не найдено.")

if __name__ == "__main__":
    check_lamoda()
