# remembers which postings we have already seen, and when we first saw them - stored as data/seen.json, e.g. {"ryoshu-intern_london_1a2b3c": "2026-11-07"}
#  seen.json stores every key with the date it was first seen. update adds new keys, removes duplicates, and returns postings firts seen within last 2 days (which becomes new_postings.json)

import datetime as dt
import json
from pathlib import Path


def load_seen(path):
    # reads seen.json to see if it exists, else start with empty record
    filePath = Path(path)
    return json.loads(filePath.read_text(encoding="utf-8")) if filePath.exists() else {}

def update(postings, seen, today, window_days = 2):
    # returns recent postings (postings seen within last window_days days - set to 2), and also returns seen: the record with any brand new keys added
    seen = dict(seen) # work on a copy of seen.json, not the real main file
    current = {} # key -> posting, removes duplicates within this one run
    for posting in postings:
        if posting.key in current:
            # same job found twice this run, keep the first
            continue
        # setdefault only adds key if it is new, so old firts seen dates are kept
        seen.setdefault(posting.key, today)
        posting.first_seen = seen[posting.key]
        current[posting.key] = posting
    # earliest date that still coutns as recent - a window of 2 on 2026-11-08 gives cutoff of 2026-11-07
    cutoff = (dt.date.fromisoformat(today) - dt.timedelta(days=window_days -1)).isoformat()
    # dates in YYYY-MM-DD form sort correctly as text, so >= works for comparison
    recent = [posting for posting in current.values() if posting.first_seen >= cutoff]
    return recent, seen