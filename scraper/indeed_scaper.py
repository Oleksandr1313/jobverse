import os
import sys
import time
from playwright.sync_api import sync_playwright

# Add project root to path to import db_manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.db_manager import insert_job, create_tables

create_tables()

job_titles = ["Data Scientist", "Software Developer"]
city = "Winnipeg"

# Format job title for URL
def format_job_title(job):
    return job.replace(" ", "+")

# Scrape jobs using Playwright
def scrape_jobs(playwright, job, city):
    url = f"https://ca.indeed.com/jobs?q={format_job_title(job)}&l={city.replace(' ', '+')}"
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print(f"Scraping {job} jobs in {city} from {url}")
    page.goto(url, timeout=60000)
    
    # Wait for job cards to load
    try:
        page.wait_for_selector("div.job_seen_beacon", timeout=10000)
    except:
        print(f"No job listings found for {job}")
        browser.close()
        return []

    job_cards = page.query_selector_all("div.job_seen_beacon")
    jobs_list = []

    for card in job_cards:
        try:
            title = card.query_selector("h2.jobTitle span").inner_text().strip()
        except:
            title = None
        try:
            company = card.query_selector("span.companyName").inner_text().strip()
        except:
            company = None
        try:
            location = card.query_selector("div.companyLocation").inner_text().strip()
        except:
            location = None
        try:
            desc = card.query_selector("div.job-snippet").inner_text().strip()
        except:
            desc = None
        try:
            url_elem = card.query_selector("h2.jobTitle a").get_attribute("href")
            if url_elem and not url_elem.startswith("http"):
                url_elem = "https://ca.indeed.com" + url_elem
        except:
            url_elem = url

        job_data = {
            "job_title": title,
            "company": company,
            "location": location,
            "description": desc,
            "source_url": url_elem
        }

        insert_job(job_data)
        jobs_list.append(job_data)

    browser.close()
    return jobs_list


def main():
    all_jobs = []
    with sync_playwright() as playwright:
        for job in job_titles:
            jobs = scrape_jobs(playwright, job, city)
            print(f"Scraped {len(jobs)} {job} jobs in {city}")
            all_jobs.extend(jobs)
            time.sleep(2)  # polite delay
    print(f"Total jobs scraped and inserted: {len(all_jobs)}")

if __name__ == "__main__":
    main()
