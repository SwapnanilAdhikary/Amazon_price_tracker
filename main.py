import requests
from bs4 import BeautifulSoup
import smtplib
MY_EMAIL="adhikaryswapnanil@gmail.com"
MY_PASSWORD="hozm qowj kzli cvey "
URL2 = "https://www.amazon.in/MSI-i5-11260H-Windows-GeForce-11SC-1477IN/dp/B0C6F9GMW1/ref=sr_1_4?crid=1IKBRC8PHZKMP&dib=eyJ2IjoiMSJ9.7SqFCyAPjugrAYbM6QShPD8jsMNJ0q-R6zKNFNq5DIvMj_tUx17J2-nKdWKAUIolTrqwzAGm4Kc9pcV3mktTQq2HvaZAew1QNvhi9ryqC-Jlbd-IVX_Iet09VJsBskgAIBzOPyZmkooto0ntsgR18ueIkLvP1i-3jlyTg5X-pa3pgJg1QaUyiAW0CR0692hmpHkIspBXmrLZdPf8u0H_PcCYirJtkK1K-iykYQv7U4A.MAMoZesXmS548oukRzuALZPaB7dpjSKENWz26AX_nGk&dib_tag=se&keywords=gaming+laptop&qid=1714553477&sprefix=gaming+%2Caps%2C323&sr=8-4"
URL = "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"
response = requests.get(URL)
header = {
    'Accept-Language': "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
}
Web_page=response.text
soup = BeautifulSoup(Web_page,"html.parser")
price = soup.find(class_="a-offscreen").get_text()
price_without_currency = price.split("$")[1]
price_as_float = float(price_without_currency)
print(price_as_float)

if price_as_float <80:
    print("time to send mail")
    connection = smtplib.SMTP("smtp.gmail.com",587)
    connection.starttls()
    connection.login(user=MY_EMAIL,password=MY_PASSWORD)
    connection.sendmail(from_addr=MY_EMAIL,to_addrs="shekharadhikary024@gmail.com",msg="the product is price is at "
                                                                                       "all time low , buy from amazon")

else:
    print("waiting for price drop")

