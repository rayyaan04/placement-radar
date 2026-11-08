# reads jobs from lever
import datetime as dt
from placement_radar.http import fetch_json
from placement_radar.models import Posting

def ms_to_date(ms):
    # lever gives dates as miliseconds since epoch time (1/1/1970), gotta convert it
    if not ms:
        return ""
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).date().isoformat()

def fetch(cfg, get=fetch_json):
    # cfg is one entry from sources.yaml (fetchers list of companies to check)
    # get is the function used to download json
    data = get(f"https://api.lever.co/v0/postings/{cfg['board']}?mode=json")
    # lever returns plain list of jobs not wrapped in {"jobs":"}
    return [
        Posting(
            company = cfg["company"],
            title = job.get("text", ""), #lever calls title "text"
            location = (job.get("categories") or {}).get("location", ""), # location is nested inside categories  e.g. {"categories": {"location": "Cambridge"}}
            url = job.get("hostedUrl", ""),
            source = "lever",
            posted = ms_to_date(job.get("createdAt")),
            description = job.get("descriptionPlain", ""), # already is plain text
        )
        for job in data
]