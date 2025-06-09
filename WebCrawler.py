import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
import cloudscraper
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


visited_urls = set()
scraper = cloudscraper.create_scraper()


def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver

# FDA website is no permitting scripts to access
# def extract_text_from_page(url):
#     try:
#         response = scraper.get(url, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")
#         for tag in soup(["header", "footer", "nav", "aside", "script", "style"]):
#             tag.decompose()
#         paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
#         return "\n".join(paragraphs)
#     except Exception as e:
#         print(f"Error parsing {url}: {e}")
#         return ""

def extract_text_with_selenium(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for tag in soup(["header", "footer", "nav", "aside", "script", "style"]):
            tag.decompose()

        paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
        text = "\n".join(paragraphs)

        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
        print(f"Found {len(links)} links on {url}")
        return text, links
    except Exception as e:
        print(f"Error parsing {url} with Selenium: {e}")
        return "", []

def is_valid_fda_cosmetic_url(url):
    parsed = urlparse(url)
    return (
        "fda.gov" in parsed.netloc and
        "/cosmetics/" in parsed.path and
        not any(ex in url for ex in ["#", ".pdf", ".doc", "mailto", "?"])
    )


def crawl_fda(start_url, max_pages=100):
    to_visit = [start_url]
    crawled = []
    driver = init_driver()

    while to_visit and len(crawled) < max_pages:
        url = to_visit.pop(0)
        if url in visited_urls:
            continue

        print(f"Crawling: {url}")
        visited_urls.add(url)
        text, links = extract_text_with_selenium(driver, url)
        if text:
            crawled.append({"url": url, "text": text})

        try:
            for abs_url in links:
                if is_valid_fda_cosmetic_url(abs_url) and abs_url not in visited_urls:
                    to_visit.append(abs_url)
        except Exception as e:
            print(f"Error extracting links from {url}: {e}")

        time.sleep(2)  # be polite

    return crawled

def main():
    start_url = "https://www.fda.gov/cosmetics/resources-you-cosmetics/resources-industry-cosmetics"
    output_dir = "data/fda_cosmetics_pages"
    os.makedirs(output_dir, exist_ok=True)

    print("Starting FDA cosmetics crawler...")
    pages = crawl_fda(start_url, max_pages=100)

    print(f"\nSaving {len(pages)} pages...")
    for i, page in enumerate(pages):
        filename = os.path.join(output_dir, f"page_{i:03d}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(page, f, ensure_ascii=False, indent=2)

    print(f"Done. Files saved in: {output_dir}")

if __name__ == "__main__":
    main()