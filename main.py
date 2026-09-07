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
        return
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = "🔥 Отчет Lamoda (Обход защиты)"
    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def check_lamoda():
    ua = UserAgent()
    found_items = []
    log_report = "Лог сканирования:\n"
    
    print("Начинаем сканирование каталога Ламода...")

    for brand_key, brand_name in TARGET_BRANDS.items():
        url = f"https://www.lamoda.ru/api/v1/recommendations/search?brand={brand_key}&limit=30"
        
        # Расширенные заголовки для имитации реального браузера
        headers = {
            "User-Agent": ua.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.lamoda.ru/",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Бренд {brand_name}: статус ответа {response.status_code}")
            log_report += f"{brand_name}: статус {response.status_code}\n"
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                print(f" Найдено товаров в ответе: {len(products)}")
                
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
            print(f"Ошибка для {brand_name}: {e}")
            log_report += f"{brand_name}: ошибка {e}\n"
            
        time.sleep(3) # Увеличиваем задержку между запросами, чтобы не триггерить защиту

    if found_items:
        report = f"🔥 Найдены скидки от {MIN_DISCOUNT}%:\n\n"
        for item in found_items[:15]:
            report += f"▪️ {item['brand']} — {item['title']}\n"
            report += f" Цена: {item['old_price']}₽ ➡️ {item['new_price']}₽ (-{item['discount']}%)\n"
            report += f" Ссылка: {item['link']}\n\n"
    else:
        report = "Сканирование завершено.\n\n" + log_report

    send_email(report)

if __name__ == "__main__":
    check_lamoda()
