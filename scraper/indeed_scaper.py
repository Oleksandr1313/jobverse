import os
import sys
import time
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.db_manager import insert_job, create_tables

create_tables()

job_titles = ["Data Scientist", "Software developer"]
city = "Winnipeg"

def format_job_title(job: str) -> str:
    return job.replace(" ", "+")

def scrape_jobs(playwright, job, city):
    url = f"https://ca.indeed.com/jobs?q={format_job_title(job)}&l={city.replace(' ', '+')}"
    logger.info(f"URL: {url}")

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url, timeout=60000)

    for _ in range(3):
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(2)

    try:
        page.wait_for_selector("div.cardOutline", timeout=15000)
        job_cards = page.query_selector_all("div.cardOutline")
        logger.info(f"Cards: {len(job_cards)} {job}")
    except Exception as e:
        logger.info(f"No jobs for {job}: {e}")
        browser.close()
        return []

    jobs_list = []
    for idx, card in enumerate(job_cards, start=1):
        try:
            link_elem = card.query_selector("h2.jobTitle a")
            job_url = link_elem.get_attribute("href")
            if job_url and not job_url.startswith("http"):
                job_url = "https://ca.indeed.com" + job_url
            job_title = card.query_selector("h2.jobTitle span").inner_text().strip()
            company_elem = card.query_selector("span[data-testid='company-name']")
            company = company_elem.inner_text().strip() if company_elem else "Unknown"
            location_elem = card.query_selector("div[data-testid='text-location']")
            location = location_elem.inner_text().strip() if location_elem else "N/A"
        except Exception:
            continue

        detail_page = context.new_page()
        try:
            detail_page.goto(job_url, timeout=60000)
            detail_page.wait_for_selector("div#jobDescriptionText", timeout=10000)
            desc_elem = detail_page.query_selector("div#jobDescriptionText")
            description = desc_elem.inner_text().strip() if desc_elem else None
        except Exception:
            description = None

        job_data = {
            "job_title": job_title,
            "company": company,
            "location": location,
            "description": description,
            "source_url": job_url
        }

        logger.info(f"Insert: {job_title} | {company} | {location}")
        insert_job(job_data)
        jobs_list.append(job_data)

        detail_page.close()
        time.sleep(1)

    browser.close()
    return jobs_list

def main():
    all_jobs = []
    with sync_playwright() as playwright:
        for job in job_titles:
            jobs = scrape_jobs(playwright, job, city)
            logger.info(f"Scraped {len(jobs)} {job}")
            all_jobs.extend(jobs)
            time.sleep(2)
    logger.info(f"Total: {len(all_jobs)}")

if __name__ == "__main__":
    main()