import db


def main():
    url = input("Paste the Amazon URL: ").strip()
    while True:
        try:
            target_price = float(input("Enter your target price: ").strip())
            break
        except ValueError:
            print("Invalid target price. Please enter numbers only, such as 79.99.")
    title = input("Enter a short product title: ").strip()
    platform = "amazon"

    db.initialize_db()
    product_id = db.add_product(title, url, target_price, platform)

    print(f"Successfully added '{title}' with product ID {product_id}.")


if __name__ == "__main__":
    main()