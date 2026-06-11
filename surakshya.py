from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://psc.gov.np/category/security-vacancies",
        wait_until="networkidle"
    )

    html = page.content()

    browser.close()

soup = BeautifulSoup(html, "html.parser")

jobs = []

rows = soup.select(
    "table.caption-bottom.text-base.w-full tbody tr"
)

print("Rows Found:", len(rows))

for row in rows:
    cols = row.find_all("td")

    if len(cols) < 4:
        continue

    link = cols[1].find("a")

    if not link:
        continue

    jobs.append({
        "organization": "PSC",
        "category": "सुरक्षा",
        "title": link.get_text(strip=True),
        "publishedDate": cols[2].get_text(strip=True),
        "url": link.get("href")
    })

print(json.dumps(jobs, ensure_ascii=False, indent=2))