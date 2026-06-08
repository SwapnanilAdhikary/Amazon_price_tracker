import os
import smtplib

from dotenv import load_dotenv

from db import add_product, initialize_db, log_price
from scraper import scrape_amazon_price


load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")

if not MY_EMAIL or not MY_PASSWORD:
    raise ValueError("Set MY_EMAIL and MY_PASSWORD in your .env file before running the script.")

URL = "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"
headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

initialize_db()
product_id = add_product(
    title="Amazon product",
    url=URL,
    target_price=80,
    platform="Amazon",
)

price_as_float = scrape_amazon_price(URL, headers)

if price_as_float is None:
    print("waiting for a valid price")
elif price_as_float < 80:
    print("time to send mail")
    log_price(product_id, price_as_float)
    connection = smtplib.SMTP("smtp.gmail.com", 587)
    connection.starttls()
    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
    connection.sendmail(
        from_addr=MY_EMAIL,
        to_addrs="adhikaryswapnanil@gmail.com",
        msg="the product is price is at all time low , buy from amazon",
    )
else:
    print("waiting for price drop")
    log_price(product_id, price_as_float)

