import csv
import re

import pandas as pd
from pathlib import Path
from playwright.async_api import (
    Page,
)


async def detect_captcha(page: Page) -> bool:
    count = await page.locator(
        'iframe[title*="captcha" i], iframe[src*="captcha" i]'
    ).count()
    return count > 0


def apply_blacklist(df, role_blacklist, company_blacklist):
    df = df[~df["Company Name"].str.strip('"').isin(company_blacklist)]
    role_blacklist = [role.lower() for role in role_blacklist]
    role_filter_pattern = "|".join(role_blacklist)

    df = df[
        ~df["Role"].str.lower().str.contains(role_filter_pattern, na=False)
    ]

    return df


def load_blacklist(filename: str) -> list[str]:
    BASE_DIR = Path(__file__).parent  # folder where this script is
    path = BASE_DIR / "blacklisted" / filename
    with open(path, mode="r") as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader]


def dataframe(jobs):
    data = []
    for job in jobs:
        data.append(
            {"Company Name": job.company, "Role": job.role, "URL": job.url}
        )
    df = pd.DataFrame(data)
    result = df.drop_duplicates(subset=["Company Name", "Role"])
    result["Company Name"] = df["Company Name"].fillna("").astype(str)
    result["Role"] = df["Role"].fillna("").astype(str)
    return result


async def navigate_to_all_jobs(page):
    # Find the more jobs button
    button = page.locator(
        "span", has_text=re.compile(r"\d+\+?\s+more jobs")
    ).first
    await button.wait_for(state="visible", timeout=0)
    await button.hover()
    await button.click()
    await page.wait_for_load_state("domcontentloaded")


async def scroll(page):
    while True:
        current_height = await page.evaluate("document.body.scrollHeight")
        await page.evaluate(f"window.scrollTo(0, {current_height})")
        # wait for new content to load
        await page.wait_for_timeout(1000)
        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == current_height:
            break
