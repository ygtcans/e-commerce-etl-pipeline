import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TrendyolScraper:
    def __init__(self, base_url="https://www.trendyol.com/cep-telefonu-x-c103498", 
                 max_pages=164, max_workers=5, output_file="data/raw_data.csv"):
        self.base_url = base_url
        self.max_pages = max_pages
        self.max_workers = max_workers
        self.output_file = output_file

    def fetch_page(self, url):
        """Fetch a single page from the given URL."""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch {url}: {e}")
            return None

    def parse_product_page(self, page_content):
        """Parse the HTML content of a page and extract product data."""
        soup = BeautifulSoup(page_content, "html.parser")
        trendyol_data = []

        # Use .select() to find product containers
        product_containers = soup.select("div.p-card-wrppr")
        for product in product_containers:
            try:
                brand = product.select_one("span.prdct-desc-cntnr-ttl")
                product_name = product.select_one("span.prdct-desc-cntnr-name.hasRatings")
                product_desc = product.select_one("div.product-desc-sub-text")
                rating_score = product.select_one("span.rating-score")
                ratings = product.select_one("div.ratings")
                price = product.select_one("div.prc-box-dscntd")

                brand = brand.text.strip() if brand else None
                product_name = product_name.text.strip() if product_name else None
                product_desc = product_desc.text.strip() if product_desc else None
                rating_score = rating_score.text.strip() if rating_score else None
                ratings = ratings.text.strip("()") if ratings else None
                price = price.text.strip() if price else None

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

    def scrape_trendyol(self):
        """Scrape Trendyol website and return a list of product data."""
        trendyol_data = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for page in range(1, self.max_pages + 1):
                url = f"{self.base_url}?pi={page}" if page > 1 else self.base_url
                futures[executor.submit(self.fetch_page, url)] = page

            for future in as_completed(futures):
                page = futures[future]
                try:
                    page_content = future.result()
                    if page_content:
                        page_data = self.parse_product_page(page_content)
                        trendyol_data.extend(page_data)
                        logging.info(f"Page {page} scraped successfully. {len(page_data)} products found.")
                    else:
                        logging.warning(f"No content for page {page}.")
                except Exception as e:
                    logging.error(f"Error processing page {page}: {e}")

        return trendyol_data

    def save_to_csv(self, data):
        """Save the scraped data to a CSV file after converting to DataFrame."""
        df = pd.DataFrame(data)
        # Check if the file exists
        if os.path.exists(self.output_file):
            logging.info(f"{self.output_file} already exists. Appending new data.")
            df.to_csv(self.output_file, mode='a', header=False, index=False, encoding='utf-8')
        else:
            df.to_csv(self.output_file, mode='w', header=True, index=False, encoding='utf-8')
        logging.info(f"Data saved to {self.output_file}")

    def run(self):
        """Run the scraping process and save the data to CSV."""
        logging.info("Starting Trendyol scraper...")
        data = self.scrape_trendyol()
        if data:
            self.save_to_csv(data)
            logging.info(f"Scraping completed. {len(data)} products saved.")
        else:
            logging.warning("No data scraped.")