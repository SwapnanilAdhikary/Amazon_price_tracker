import logging
import re

import requests
from bs4 import BeautifulSoup


def scrape_amazon_price(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        logging.warning("Unable to fetch Amazon page: %s", error)
        return None

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        price_element = soup.find(class_="a-offscreen")

        if price_element is None or not price_element.get_text(strip=True):
            price_element = soup.find(class_="a-price-whole")

        if price_element is None or not price_element.get_text(strip=True):
            price_element = soup.find(id="priceblock_ourprice")

        if price_element is None or not price_element.get_text(strip=True):
            title = soup.title.text if soup.title and soup.title.text else "Unknown title"
            logging.warning("Could not find a price element. Page title: %s", title)
            return None

        price_text = price_element.get_text(strip=True)
        price_match = re.search(r"\d+(?:[.,]\d+)?", price_text)

        if price_match is None:
            logging.warning("Could not parse a numeric price from: %s", price_text)
            return None

        cleaned_price = price_match.group(0).replace(",", "")
        return float(cleaned_price)
    except (ValueError, TypeError, AttributeError) as error:
        logging.error("Failed to parse Amazon price: %s", error)
        return None