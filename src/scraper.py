import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
BASE_URL = "https://www.trendyol.com/cep-telefonu-x-c103498"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
MAX_PAGES = 164
MAX_WORKERS = 5
OUTPUT_FILE = "data/raw_data.csv"

def fetch_page(url):
    """Fetch a single page from the given URL."""
    time.sleep(1)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

def parse_product_page(page_content):
    """Parse the HTML content of a page and extract product data."""
    soup = BeautifulSoup(page_content, "html.parser")
    trendyol_data = []

    # Use .select() to find product containers
    product_containers = soup.select("div.p-card-wrppr")
    for product in product_containers:
        try:
            # Use .select() to extract details from the product container
            brand = product.select_one("span.prdct-desc-cntnr-ttl")
            product_name = product.select_one("span.prdct-desc-cntnr-name.hasRatings")
            product_desc = product.select_one("div.product-desc-sub-text")
            rating_score = product.select_one("span.rating-score")
            ratings = product.select_one("div.ratings")
            price = product.select_one("div.prc-box-dscntd")
            
            # Extract text if the element exists, otherwise None
            brand = brand.text.strip() if brand else None
            product_name = product_name.text.strip() if product_name else None
            product_desc = product_desc.text.strip() if product_desc else None
            rating_score = rating_score.text.strip() if rating_score else None
            ratings = ratings.text.strip("()") if ratings else None
            price = price.text.strip() if price else None
            
            # Append the product data
            trendyol_data.append({
                "Product Brand": brand,
                "Product Name": product_name,
                "Product Description": product_desc,
                "Rating Score": rating_score,
                "Rating Count": ratings,
                "Price (TL)": price
            })
        except Exception as e:
            logging.warning(f"Failed to parse a product: {e}")

    return trendyol_data

def scrape_trendyol():
    """Scrape Trendyol website and return a list of product data."""
    trendyol_data = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}

        for page in range(1, MAX_PAGES + 1):
            url = f"{BASE_URL}?pi={page}" if page > 1 else BASE_URL
            futures[executor.submit(fetch_page, url)] = page

        for future in as_completed(futures):
            page = futures[future]
            try:
                page_content = future.result()
                if page_content:
                    page_data = parse_product_page(page_content)
                    trendyol_data.extend(page_data)
                    logging.info(f"Page {page} scraped successfully. {len(page_data)} products found.")
                else:
                    logging.warning(f"No content for page {page}.")
            except Exception as e:
                logging.error(f"Error processing page {page}: {e}")

    return trendyol_data

def save_to_csv(data, filename=OUTPUT_FILE):
    """Save the scraped data to a CSV file."""
    fieldnames = ["Product Brand", "Product Name", "Product Description", "Rating Score", "Rating Count", "Price (TL)"]
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Failed to save data to {filename}: {e}")

def main():
    logging.info("Starting Trendyol scraper...")
    data = scrape_trendyol()
    if data:
        save_to_csv(data)
        logging.info(f"Scraping completed. {len(data)} products saved.")
    else:
        logging.warning("No data scraped.")

if __name__ == "__main__":
    main()
