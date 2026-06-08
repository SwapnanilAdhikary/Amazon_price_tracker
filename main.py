import os
import smtplib

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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

response = requests.get(URL, headers=headers)
web_page = response.text
soup = BeautifulSoup(web_page, "html.parser")
price = soup.find(class_="a-offscreen").get_text()
price_without_currency = price.split("$")[1]
price_as_float = float(price_without_currency)
print(price_as_float)

if price_as_float < 80:
    print("time to send mail")
    connection = smtplib.SMTP("smtp.gmail.com", 587)
    connection.starttls()
    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
    connection.sendmail(
        from_addr=MY_EMAIL,
        to_addrs="shekharadhikary024@gmail.com",
        msg="the product is price is at all time low , buy from amazon",
    )
else:
    print("waiting for price drop")

