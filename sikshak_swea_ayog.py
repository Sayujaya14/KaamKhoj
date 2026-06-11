from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for page_num in range(1, 4):  # Pages 1, 2, 3

        url = f"https://tsc.gov.np/category/74/?page={page_num}"
        print(f"Scraping page {page_num}...")

        page.goto(url, wait_until="networkidle")

        soup = BeautifulSoup(page.content(), "html.parser")

        cards = soup.select(".grid__card")

        print(f"Found {len(cards)} cards")

        for card in cards:

            title_tag = card.select_one(".card__title a")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)

            link = urljoin(
                "https://tsc.gov.np",
                title_tag.get("href", "").strip()
            )

            date_tag = card.select_one(".meta.post__date")

            published_date = (
                date_tag.get_text(" ", strip=True)
                if date_tag else ""
            )

            jobs.append({
                "organization": "TSC",
                "category": "NA",
                "title": title,
                "publishedDate": published_date,
                "url": link
            })

    browser.close()

with open("tsc_jobs.json", "w", encoding="utf-8") as f:
    json.dump(
        jobs,
        f,
        ensure_ascii=False,
        indent=4
    )

print(f"\nSaved {len(jobs)} jobs to tsc_jobs.json")