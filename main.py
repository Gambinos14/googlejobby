import asyncio
from dataclasses import dataclass
from urllib.parse import urlencode

from playwright.async_api import async_playwright

from utils import (
    apply_blacklist,
    dataframe,
    detect_captcha,
    load_blacklist,
    navigate_to_all_jobs,
    scroll,
)

positions = [
    "backend engineer",
    "software engineer",
    "fullstack software engineer",
    "fullstack engineer",
]


@dataclass
class Job:
    role: str
    company: str
    url: str


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()

        jobs: list[Job] = []
        for position in positions:
            search_phrase = (
                f"{position} jobs remote united states since yesterday"
            )
            params = {"q": search_phrase}
            query_string = urlencode(params)
            url = f"https://www.google.com/search?{query_string}"
            await page.goto(url, wait_until="domcontentloaded")

            if await detect_captcha(page):
                print("User action required. Solve CAPTCHA ...")

            await navigate_to_all_jobs(page)
            await scroll(page)

            elements = await page.locator(
                'a[href^="https://www.google.com/search"]'
            ).all()

            for element in elements:
                # Find the specific divs as per the described path
                divs = element.locator(
                    "span:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div"
                )

                count = await divs.count()
                role = ""
                company = ""
                for i in range(count):
                    div_content = await divs.nth(i).inner_text()
                    if i == 0:
                        role = div_content
                    elif i == 1:
                        company = div_content

                role_search = f"{role} {company}"
                role_url = f"https://www.google.com/search?{urlencode({'q': role_search})}"
                job = Job(role, company, role_url)
                jobs.append(job)

        # Prepare data for DataFrame
        df = dataframe(jobs)

        role_blacklist = load_blacklist("roles.csv")
        company_blacklist = load_blacklist("companies.csv")

        # Filter by company blacklist
        df = apply_blacklist(df, role_blacklist, company_blacklist)

        df.to_csv("out.csv", index=False)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
