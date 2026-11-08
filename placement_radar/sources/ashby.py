# reads jobs from ashby - has public json feed
from placement_radar.http import fetch_json
from placement_radar.models import Posting

def fetch(cfg, get=fetch_json):
    # cfg is one entry from sources.yaml (fetchers list of companies to check)
    # get is the function used to download json
    data = get(f"https://api.ashbyhq.com/posting-api/job-board/{cfg['board']}")
    # ashby wraps jobs like greenhouse: {"jobs": []}
    # .get(field, "") returns "" instead of crashing if field is missing
    return [
        Posting(
            company = cfg["company"],
            title = job.get("title", ""),
            location = job.get("location", ""), # plaintext - e.g. "London, UK"
            url = job.get("jobUrl", ""),
            source = "ashby",
            posted = (job.get("publishedAt") or "")[:10],
            description = job.get("descriptionPlain", ""),
        )
        for job in data.get("jobs", [])
    ]