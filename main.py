import os
import smtplib

from dotenv import load_dotenv

import db
import scraper


load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")

if not MY_EMAIL or not MY_PASSWORD:
    raise ValueError("Set MY_EMAIL and MY_PASSWORD in your .env file before running the script.")

HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}


def send_price_alert(product_title, current_price, target_price, recipient_email):
    message = (
        f"Subject: Price Alert for {product_title}\n"
        f"From: {MY_EMAIL}\n"
        f"To: {recipient_email}\n"
        f"\n"
        f"{product_title} is now {current_price}, which is at or below your target price of {target_price}."
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=recipient_email,
            msg=message,
        )


def main():
    db.initialize_db()
    products = db.get_all_products()

    if not products:
        print("No monitored products found.")
        return

    for product_id, title, url, target_price, platform in products:
        if not platform or platform.lower() != "amazon":
            print(f"Skipped Product {product_id}: Unsupported platform '{platform}'")
            continue

        current_price = scraper.scrape_amazon_price(url, HEADERS)

        if current_price is None:
            print(f"Checked Product {product_id}: Current price unavailable, Target is {target_price}")
            continue

        db.log_price(product_id, current_price)
        print(f"Checked Product {product_id}: Current price is {current_price}, Target is {target_price}")

        if current_price <= target_price:
            send_price_alert(title or f"Product {product_id}", current_price, target_price, MY_EMAIL)
            print(f"Alert sent for Product {product_id}")


if __name__ == "__main__":
    main()

