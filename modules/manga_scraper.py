import json
import logging
import os
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_handler = logging.FileHandler("scraper.log")
_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)


def _get_page_html(url: str, wait_selector: str = "body", timeout: int = 15) -> str:
    """Return fully rendered HTML from a page using Selenium."""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        html = driver.page_source
    except Exception as exc:
        logger.error("Selenium failed to load %s: %s", url, exc)
        html = ""
    finally:
        driver.quit()

    return html


def fetch_chapter_links(series_url: str, output_json: str) -> List[str]:
    """Fetch chapter links from a manga series page and store them in a JSON file."""

    html = _get_page_html(series_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    chapter_links: List[str] = []
    for a in soup.find_all("a"):
        text = (a.text or "").lower()
        href = a.get("href")
        if not href:
            continue
        if "chapter" in text or "capitulo" in text or "capítulo" in text:
            full_url = urljoin(series_url, href)
            chapter_links.append(full_url)
    chapter_links = sorted(set(chapter_links))

    try:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(chapter_links, f, indent=2, ensure_ascii=False)
        logger.info("Saved %d chapter links to %s", len(chapter_links), output_json)
    except Exception as exc:
        logger.error("Failed to write JSON %s: %s", output_json, exc)

    return chapter_links


def download_chapter_images(chapter_url: str, dest_dir: str, delay: float = 1.0) -> None:
    """Download all images from a chapter page into the destination directory."""

    os.makedirs(dest_dir, exist_ok=True)
    html = _get_page_html(chapter_url)
    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")
    image_urls: List[str] = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src or src.startswith("data:"):
            continue
        full_url = urljoin(chapter_url, src)
        image_urls.append(full_url)

    if not image_urls:
        logger.warning("No images found on %s", chapter_url)
        return

    for i, url in enumerate(image_urls, 1):
        try:
            img_resp = requests.get(url, timeout=10)
            img_resp.raise_for_status()
            ext = os.path.splitext(url)[1] or ".jpg"
            file_name = os.path.join(dest_dir, f"{i:03d}{ext}")
            with open(file_name, "wb") as f:
                f.write(img_resp.content)
            logger.info("Downloaded %s", file_name)
        except Exception as exc:
            logger.error("Failed to download %s: %s", url, exc)
        if delay:
            import time
            time.sleep(delay)


def download_chapters(chapter_links: List[str], manga_name: str, delay: float = 1.0) -> None:
    """Download all chapters into a structured directory."""

    for idx, url in enumerate(chapter_links, 1):
        chapter_dir = os.path.join(manga_name, f"chapter-{idx}")
        download_chapter_images(url, chapter_dir, delay=delay)
        logger.info("Finished chapter %d", idx)
