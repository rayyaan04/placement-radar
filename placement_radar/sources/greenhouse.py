# reads jobs from greenhouse (used by anthropic and monzo)
# greenhouse gives every company a free public json feed of its open jobs
from placement_radar.http import fetch_json
from placement_radar.models import Posting

def fetch(cfg, get=fetch_json):
    # cfg is one entry from sources.yaml (fetchers list of companies to check)
    # get is the function used to download json
    data = get(f"https://boards-api.greenhouse.io/v1/boards/{cfg['board']}/jobs?content=true")
    # build one Posting per job in the list
    # feed looks like {"jobs": [{...}, {...}]}
    # build one Posting per job in list
    return [
        Posting(
            company = cfg["company"],
            title = job.get("title", ""),
            location = (job.get("location") or {}).get("name", ""),# location is nested e.g. {"location": {"name": "London, UK"}}
            url = job.get("absolute_url", ""),
            source = "greenhouse",
            posted = (job.get("updated_at") or "")[:10], # date is formatted with lots of unneeded characters - only need the first 10 for a YYYY-MM-DD format
            description = job.get("content", ""),
        )
        for job in data.get("jobs", [])
    ]