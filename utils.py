import json
import re
from datetime import datetime
from pathlib import Path


def save_job(job):
    """
    Extract all relevant details from a job and save to a JSON file.
    Creates a directory with today's date and saves the job details
    with the job ID as the filename.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    dir_path = Path(today)
    dir_path.mkdir(exist_ok=True)

    url = job.linkedin_url
    match = re.search(r"/jobs/view/(\d+)", url)
    if not match:
        raise ValueError("Could not extract job ID from URL")

    # Sanitize filename
    id = str(re.sub(r"[^\w\-]", "_", match.group(1)))
    filepath = dir_path / f"{id}.json"

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(job.to_dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠ Failed to save job details: {e}")
