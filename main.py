import asyncio
import random

from linkedin_scraper.callbacks import JSONLogCallback
from linkedin_scraper.core.browser import BrowserManager
from linkedin_scraper.scrapers.job import JobScraper
from linkedin_scraper.scrapers.job_search import JobSearchScraper

from actions import login, scroll
from session import session_valid
from utils import save_job


async def main():
    """Search for jobs and save details"""
    async with BrowserManager(headless=False) as browser:
        JSON_logger = JSONLogCallback("logs.json")
        # Hydrate session or login
        if session_valid():
            await browser.load_session("session.json")
        else:
            await login(browser)
            await scroll(browser)

        await JSON_logger.on_progress("✓ Session loaded", 100)

        # Search for jobs
        search_scraper = JobSearchScraper(
            browser.page, callback=JSON_logger
        )
        await JSON_logger.on_progress("🔍 Searching for jobs...", 0)
        # TODO fix the search functionality to add scrolling behavior
        job_urls = await search_scraper.search(
            keywords="software engineer AND python",
            location="United States",
            limit=50,
        )
        await JSON_logger.on_progress(
            f"\n✓ Found {len(job_urls)} jobs", 100
        )

        # Scrape first job details if any found
        if job_urls:
            await JSON_logger.on_progress(
                f"\n📄 Scraping first job details...", 0
            )
            job_scraper = JobScraper(browser.page, callback=JSON_logger)
            for job_url in job_urls:
                await asyncio.sleep(random.uniform(1, 5))
                job = await job_scraper.scrape(job_url)

                save_job(job)

    await JSON_logger.on_complete("main", {"total_jobs": len(job_urls)})


if __name__ == "__main__":
    asyncio.run(main())
