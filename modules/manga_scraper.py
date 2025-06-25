import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager


# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_handler = logging.FileHandler("scraper.log")
_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

# Also add console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setFormatter(_formatter)
logger.addHandler(console_handler)


def _extract_chapter_number(url: str) -> int:
    """Extract chapter number from URL for proper sorting."""
    # Try to find patterns like "capitulo-123", "chapter-123", "cap-123", etc.
    # More comprehensive patterns to handle different site formats
    patterns = [
        r'capitu?lo?[-_](\d+)',           # capitulo-123, capitulo_123
        r'chapter[-_](\d+)',              # chapter-123, chapter_123
        r'cap[-_](\d+)',                  # cap-123, cap_123
        r'ch[-_](\d+)',                   # ch-123, ch_123
        r'/(\d+)/?(?:\?|#|$)',           # /123/ or /123? or /123# or /123 at end
        r'[-_](\d+)[-_]',                 # -123- or _123_
        r'(\d+)/?$'                       # Number at the very end of URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url.lower())
        if match:
            return int(match.group(1))
    
    # Try to find any number in the URL as fallback
    numbers = re.findall(r'\d+', url)
    if numbers:
        # Return the largest number found (usually the chapter number)
        return max(int(num) for num in numbers)
    
    # If no number found, return a very high number to put it at the end
    return 999999


def _sort_chapter_links(chapter_links: List[str]) -> List[str]:
    """Sort chapter links by chapter number in ascending order."""
    return sorted(chapter_links, key=_extract_chapter_number)


def _get_latest_chapter_number(chapter_links: List[str]) -> Optional[int]:
    """Get the highest chapter number from the list of links."""
    if not chapter_links:
        return None
    
    # Get all chapter numbers and return the maximum
    chapter_numbers = [_extract_chapter_number(link) for link in chapter_links]
    # Filter out the fallback value (999999)
    valid_numbers = [num for num in chapter_numbers if num < 999999]
    
    return max(valid_numbers) if valid_numbers else None


def _load_checkpoint(manga_name: str) -> Dict[str, Any]:
    """Load checkpoint data for resuming downloads."""
    checkpoint_file = f".{manga_name.replace(' ', '_')}_checkpoint.json"
    try:
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as exc:
        logger.warning(f"⚠️  Erro ao carregar checkpoint: {exc}")
    
    return {"last_completed_chapter": 0, "failed_chapters": []}


def _save_checkpoint(manga_name: str, last_completed: int, failed_chapters: List[int] = None):
    """Save checkpoint data for resuming downloads."""
    checkpoint_file = f".{manga_name.replace(' ', '_')}_checkpoint.json"
    checkpoint_data = {
        "last_completed_chapter": last_completed,
        "failed_chapters": failed_chapters or [],
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.error(f"❌ Erro ao salvar checkpoint: {exc}")


def _delete_checkpoint(manga_name: str):
    """Delete checkpoint file after successful completion."""
    checkpoint_file = f".{manga_name.replace(' ', '_')}_checkpoint.json"
    try:
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            logger.info("🗑️  Checkpoint removido após conclusão")
    except Exception as exc:
        logger.warning(f"⚠️  Erro ao remover checkpoint: {exc}")


def _get_page_html(url: str, wait_selector: str = "body", timeout: int = 15) -> str:
    """Return fully rendered HTML from a page using Selenium."""
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()), options=options)
    except Exception as exc:
        logger.error(f"Erro ao instalar GeckoDriver: {exc}")
        return ""

    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        html = driver.page_source
    except Exception as exc:
        logger.error(f"Selenium falhou ao carregar {url}: {exc}")
        html = ""
    finally:
        driver.quit()

    return html


def fetch_chapter_links(series_url: str, output_json: str) -> List[str]:
    """Fetch chapter links from a manga series page and store them in a JSON file."""

    start_time = time.time()
    logger.info(f"🚀 Iniciando busca de capítulos em: {series_url}")
    
    # Extract manga name from URL
    manga_name = _extract_manga_name(series_url)
    
    html = _get_page_html(series_url)
    if not html:
        logger.error("❌ Não foi possível obter HTML da página")
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
    
    # Remove duplicates and sort by chapter number
    chapter_links = list(set(chapter_links))
    chapter_links = _sort_chapter_links(chapter_links)
    
    # Get latest chapter number
    latest_chapter_number = _get_latest_chapter_number(chapter_links)
    
    end_time = time.time()
    execution_time = end_time - start_time

    # Save manga info, links and metadata in JSON
    manga_data = {
        "manga_name": manga_name,
        "series_url": series_url,
        "total_chapters": len(chapter_links),
        "latest_chapter_number": latest_chapter_number,
        "fetch_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chapter_links": chapter_links
    }

    try:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(manga_data, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Concluído! {len(chapter_links)} capítulos encontrados e ordenados em {execution_time:.2f}s")
        logger.info(f"📁 Arquivo salvo: {output_json}")
        logger.info(f"📚 Mangá: {manga_name}")
        if latest_chapter_number:
            logger.info(f"📖 Último capítulo: #{latest_chapter_number}")
    except Exception as exc:
        logger.error(f"❌ Falha ao escrever JSON {output_json}: {exc}")

    return chapter_links


def _extract_manga_name(url: str) -> str:
    """Extract manga name from URL."""
    # Try to extract manga name from common URL patterns
    patterns = [
        r'/manga/([^/]+)/?',           # /manga/manga-name/
        r'/series/([^/]+)/?',          # /series/manga-name/
        r'/([^/]+)/?$',                # manga-name/ at the end
        r'/([^/]+)/capitulo',          # manga-name/capitulo-123
        r'/([^/]+)/chapter'            # manga-name/chapter-123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url.lower())
        if match:
            name = match.group(1)
            # Clean up the name
            name = name.replace('-', ' ').replace('_', ' ')
            name = ' '.join(word.capitalize() for word in name.split())
            return name
    
    # Fallback: use domain name
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain.replace('www.', '').split('.')[0].capitalize()


def download_chapter_images(
    chapter_url: str,
    dest_dir: str,
    chapter_num: int,
    delay: float = 1.0,
) -> bool:
    """Download all images from a chapter page into the destination directory."""

    try:
        os.makedirs(dest_dir, exist_ok=True)
        html = _get_page_html(chapter_url)
        if not html:
            logger.error(f"❌ Falha ao carregar HTML do capítulo {chapter_num}")
            return False

        soup = BeautifulSoup(html, "html.parser")
        image_urls: List[str] = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src or src.startswith("data:"):
                continue
            full_url = urljoin(chapter_url, src)
            image_urls.append(full_url)

        if not image_urls:
            logger.warning(
                f"⚠️  Nenhuma imagem encontrada no capítulo {chapter_num}"
            )
            return False

        successful_downloads = 0
        for i, url in enumerate(image_urls, 1):
            try:
                img_resp = requests.get(url, timeout=10)
                img_resp.raise_for_status()
                ext = os.path.splitext(url)[1] or ".jpg"
                file_name = os.path.join(dest_dir, f"{i:03d}{ext}")
                with open(file_name, "wb") as f:
                    f.write(img_resp.content)
                successful_downloads += 1
            except Exception as exc:
                logger.error(
                    f"❌ Erro ao baixar imagem {i} do capítulo {chapter_num}: {exc}"
                )

            if delay:
                time.sleep(delay)

        success = successful_downloads > 0
        if success:
            logger.info(
                f"✅ Capítulo {chapter_num}: {successful_downloads}/{len(image_urls)} imagens baixadas"
            )
        else:
            logger.error(
                f"❌ Capítulo {chapter_num}: Falha total no download"
            )

        return success

    except Exception as exc:
        logger.error(f"❌ Erro geral no capítulo {chapter_num}: {exc}")
        return False


def _download_chapter_batch(batch_data: List[tuple], manga_name: str, delay: float) -> List[int]:
    """Download a batch of chapters and return list of successful chapter numbers."""
    successful_chapters = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all chapters in the batch
        future_to_chapter = {}
        for idx, url, chapter_dir in batch_data:
            future = executor.submit(download_chapter_images, url, chapter_dir, idx, delay)
            future_to_chapter[future] = idx
        
        # Process completed downloads
        for future in as_completed(future_to_chapter):
            chapter_num = future_to_chapter[future]
            try:
                success = future.result()
                if success:
                    successful_chapters.append(chapter_num)
            except Exception as exc:
                logger.error(f"❌ Erro no thread do capítulo {chapter_num}: {exc}")
    
    return successful_chapters


def download_chapters(json_file: str, delay: float = 1.0, batch_size: int = 3) -> None:
    """Download all chapters from JSON file into a structured directory with checkpoint support."""

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            manga_data = json.load(f)
        
        # Handle both old format (list) and new format (dict)
        if isinstance(manga_data, list):
            # Old format - just a list of links
            chapter_links = manga_data
            manga_name = "Unknown_Manga"
            logger.warning("⚠️  JSON antigo detectado. Considere refazer o fetch para incluir o nome do mangá.")
        else:
            # New format - dict with manga info
            chapter_links = manga_data["chapter_links"]
            manga_name = manga_data["manga_name"]
            
    except Exception as exc:
        logger.error(f"❌ Erro ao ler arquivo JSON: {exc}")
        return

    # Load checkpoint
    checkpoint = _load_checkpoint(manga_name)
    last_completed = checkpoint.get("last_completed_chapter", 0)
    failed_chapters = checkpoint.get("failed_chapters", [])
    
    start_time = time.time()
    logger.info(f"🚀 Iniciando download de {len(chapter_links)} capítulos")
    logger.info(f"📚 Mangá: {manga_name}")
    
    if last_completed > 0:
        logger.info(f"🔄 Continuando do capítulo {last_completed + 1} (checkpoint encontrado)")
    
    if failed_chapters:
        logger.info(f"⚠️  {len(failed_chapters)} capítulos falharam anteriormente e serão reprocessados")

    # Prepare chapters to download
    chapters_to_download = []
    
    # Add chapters from where we left off
    for idx, url in enumerate(chapter_links, 1):
        if idx > last_completed:
            chapter_dir = os.path.join(manga_name, f"chapter-{idx}")
            chapters_to_download.append((idx, url, chapter_dir))
    
    # Add previously failed chapters
    for failed_idx in failed_chapters:
        if failed_idx <= len(chapter_links):
            url = chapter_links[failed_idx - 1]
            chapter_dir = os.path.join(manga_name, f"chapter-{failed_idx}")
            chapters_to_download.append((failed_idx, url, chapter_dir))
    
    # Remove duplicates and sort
    chapters_to_download = list(set(chapters_to_download))
    chapters_to_download.sort(key=lambda x: x[0])
    
    if not chapters_to_download:
        logger.info("✅ Todos os capítulos já foram baixados!")
        _delete_checkpoint(manga_name)
        return
    
    logger.info(f"📥 {len(chapters_to_download)} capítulos para baixar")
    
    # Process in batches
    total_successful = 0
    new_failed_chapters = []
    
    for i in range(0, len(chapters_to_download), batch_size):
        batch = chapters_to_download[i:i + batch_size]
        batch_nums = [ch[0] for ch in batch]
        
        logger.info(f"🔄 Processando lote: capítulos {min(batch_nums)} a {max(batch_nums)}")
        
        successful_in_batch = _download_chapter_batch(batch, manga_name, delay)
        total_successful += len(successful_in_batch)
        
        # Update checkpoint with highest completed chapter
        if successful_in_batch:
            new_last_completed = max(last_completed, max(successful_in_batch))
            
            # Find failed chapters in this batch
            batch_failed = [num for num in batch_nums if num not in successful_in_batch]
            new_failed_chapters.extend(batch_failed)
            
            # Save checkpoint
            _save_checkpoint(manga_name, new_last_completed, new_failed_chapters)
            last_completed = new_last_completed
        
        # Small delay between batches
        if i + batch_size < len(chapters_to_download):
            time.sleep(2)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Final summary
    logger.info(f"✅ Download concluído!")
    logger.info(f"📊 {total_successful}/{len(chapters_to_download)} capítulos baixados com sucesso")
    logger.info(f"⏱️  Tempo total: {execution_time:.2f}s")
    
    if new_failed_chapters:
        logger.warning(f"⚠️  {len(new_failed_chapters)} capítulos falharam: {new_failed_chapters}")
        logger.info("💡 Execute novamente para tentar baixar os capítulos que falharam")
    else:
        logger.info("🎉 Todos os capítulos foram baixados com sucesso!")
        _delete_checkpoint(manga_name)
