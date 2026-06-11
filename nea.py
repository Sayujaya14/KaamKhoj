from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient
import json
import time

# =====================================
# CONFIG
# =====================================

BASE_URL = "https://nea.org.np"
START_URL = "https://nea.org.np/np/recruitment/open/advertisements"

SAVE_TO_MONGO = False  # Change to True if you want MongoDB insertion

# =====================================
# MONGODB CONNECTION
# =====================================

if SAVE_TO_MONGO:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["kaamkhoj"]
    collection = db["jobs"]

# =====================================
# SCRAPER
# =====================================

all_jobs = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    page.goto(
        START_URL,
        wait_until="networkidle",
        timeout=120000
    )

    page_num = 1

    while True:

        print(f"\nScraping Page {page_num}")

        soup = BeautifulSoup(
            page.content(),
            "html.parser"
        )

        cards = soup.select(
            "li.position-relative.p-2.pt-0.pb-3.border-bottom.mb-3"
        )

        print(f"Found {len(cards)} advertisements")

        if not cards:
            break

        page_jobs = []

        for card in cards:

            try:

                title_tag = card.select_one(
                    "h4.fs-15.fw-500.text-dark.mb-0"
                )

                date_tag = card.select_one(
                    "span.fs-14.fw-500.text-black-50"
                )

                link_tag = card.select_one(
                    "a.stretched-link"
                )

                title = (
                    title_tag.get_text(strip=True)
                    if title_tag
                    else ""
                )

                published_date = (
                    date_tag.get_text(" ", strip=True)
                    if date_tag
                    else ""
                )

                url = ""

                if link_tag and link_tag.get("href"):
                    url = urljoin(
                        BASE_URL,
                        link_tag["href"]
                    )

                job = {
                    "organization": "NEA",
                    "category": "Recruitment",
                    "title": title,
                    "publishedDate": published_date,
                    "url": url
                }

                page_jobs.append(job)

            except Exception as e:
                print("Error:", e)

        print(f"Extracted {len(page_jobs)} jobs")

        all_jobs.extend(page_jobs)

        # =====================================
        # PAGINATION
        # =====================================

        next_button = page.locator(
            "a[rel='next']"
        )

        if next_button.count() == 0:
            print("No more pages.")
            break

        try:

            next_button.first.click()

            page.wait_for_load_state(
                "networkidle"
            )

            time.sleep(2)

            page_num += 1

        except Exception:
            print("Pagination ended.")
            break

    browser.close()

# =====================================
# REMOVE DUPLICATES
# =====================================

unique_jobs = []
seen = set()

for job in all_jobs:

    key = job["url"]

    if key not in seen:
        seen.add(key)
        unique_jobs.append(job)

# =====================================
# SAVE JSON
# =====================================

with open(
    "nea_jobs.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        unique_jobs,
        f,
        ensure_ascii=False,
        indent=4
    )

print(
    f"\nSaved {len(unique_jobs)} jobs to nea_jobs.json"
)

# =====================================
# SAVE TO MONGODB
# =====================================

if SAVE_TO_MONGO:

    inserted = 0

    for job in unique_jobs:

        result = collection.update_one(
            {
                "url": job["url"]
            },
            {
                "$set": job
            },
            upsert=True
        )

        if result.upserted_id:
            inserted += 1

    print(
        f"Inserted/Updated {len(unique_jobs)} records in MongoDB"
    )

# =====================================
# SAMPLE OUTPUT
# =====================================

print("\nFirst 5 Records:\n")

for job in unique_jobs[:5]:
    print(
        json.dumps(
            job,
            ensure_ascii=False,
            indent=2
        )
    )