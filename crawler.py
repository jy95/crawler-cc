import requests
import json
import os
from bs4 import BeautifulSoup

URL_TEMPLATE = "https://www.cashconverters.be/fr/recherche?controller=search&s=manette+ps3&q=Prix-%E2%82%AC-2.99-40.99&order=product.price.desc&page={}"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DATA_FILE = "products.json"
PR_BODY_FILE = "pr_body.md"

def load_existing_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4)

def generate_pr_body(new_products):
    with open(PR_BODY_FILE, "w", encoding="utf-8") as f:
        f.write("# New Products Available\n\n")
        f.write("| Title | Price | Store | URL |\n")
        f.write("|---|---|---|---|\n")
        for product in new_products:
            f.write(f"| {product['title']} | {product['price']} | {product['store']} | [Link]({product['url']}) |\n")

def scrape_page(page_number):
    url = URL_TEMPLATE.format(page_number)
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    product_elements = soup.select(".product-miniature")
    
    products = []
    for product in product_elements:
        link = product.select_one(".product-title a")
        price = product.select_one(".price")
        store = product.select_one(".product-store")  # Adjust selector if necessary

        if link and price and store:
            products.append({
                "title": link.text.strip(),
                "url": link["href"],
                "price": price.text.strip(),
                "store": store.text.strip()
            })
    return products

def main():
    existing_products = load_existing_products()
    existing_urls = {p["url"] for p in existing_products}
    new_products = []
    
    page = 1
    while True:
        products = scrape_page(page)
        if not products:
            break
        
        for product in products:
            if product["url"] not in existing_urls:
                new_products.append(product)
                existing_products.append(product)
        page += 1
    
    if new_products:
        save_products(existing_products)
        generate_pr_body(new_products)
        print("New products found and PR body generated.")
    else:
        print("No new products found.")

if __name__ == "__main__":
    main()
