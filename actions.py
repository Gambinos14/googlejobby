from linkedin_scraper import login_with_credentials
from linkedin_scraper.core.browser import BrowserManager


import asyncio
import random


async def scroll(
    browser: BrowserManager,
    scroll_count: int = 5,
    delay_range: tuple = (2, 5),
):
    """
    Simulate natural user scrolling behavior.

    Args:
        browser: BrowserManager instance from linkedin_scraper
        scroll_count: Number of scroll actions to perform
        delay_range: Tuple of (min, max) seconds to delay between scrolls
    """
    page = browser.page

    for _ in range(scroll_count):
        # Random scroll distance (between 300-800 pixels)
        scroll_distance = random.randint(300, 800)

        # Scroll down with smooth behavior
        await page.evaluate(f"window.scrollBy(0, {scroll_distance})")

        # Random delay between scrolls to simulate natural behavior
        delay = random.uniform(delay_range[0], delay_range[1])
        await asyncio.sleep(delay)

        # Occasionally scroll back up slightly (like a real user might)
        if random.random() < 0.3:  # 30% chance
            await asyncio.sleep(random.uniform(0.3, 0.8))
            await page.evaluate(
                f"window.scrollBy(0, {-random.randint(100, 300)})"
            )
            await asyncio.sleep(random.uniform(0.5, 1.5))


async def login(browser: BrowserManager):
    # Login with credentials
    await login_with_credentials(browser.page)

    # Save session for reuse
    await browser.save_session("session.json")
