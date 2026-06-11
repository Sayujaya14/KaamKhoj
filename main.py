from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from mongodb import save_jobs


CATEGORIES = [
    {
        "url": "https://psc.gov.np/category/security-vacancies",
        "category": "सुरक्षा"
    },
    {
        "url": "https://psc.gov.np/category/sangathit-vacancies",
        "category": "संगठित"
    },
    {
        "url": "https://psc.gov.np/category/notice-advertisement",
        "category": "निजामती"
    }
]


def scrape_category(page, url, category):
    print(f"\nScraping: {category}")

    page.goto(
        url,
        wait_until="networkidle"
    )

    soup = BeautifulSoup(
        page.content(),
        "html.parser"
    )

    jobs = []

    rows = soup.select(
        "table.caption-bottom.text-base.w-full tbody tr"
    )

    print(f"Rows Found: {len(rows)}")

    for row in rows:

        cols = row.find_all("td")

        if len(cols) < 4:
            continue

        link = cols[1].find("a")

        if not link:
            continue

        jobs.append({
            "organization": "PSC",
            "category": category,
            "title": link.get_text(strip=True),
            "publishedDate": cols[2].get_text(strip=True),
            "url": link.get("href")
        })

    return jobs


def main():

    all_jobs = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        for category in CATEGORIES:

            jobs = scrape_category(
                page,
                category["url"],
                category["category"]
            )

            all_jobs.extend(jobs)

        browser.close()

    print(f"\nTotal Jobs Found: {len(all_jobs)}")

    save_jobs(all_jobs)

    print("MongoDB save completed.")


if __name__ == "__main__":
    main()