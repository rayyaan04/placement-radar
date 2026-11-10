# main program - reads every source in sources.yaml, writes results to data/
# python -m placement_radar.run

import datetime as dt
import json
import sys
from pathlib import Path
import yaml
import shutil

from placement_radar.clean import clean_text
from placement_radar.filter import is_early_careers
from placement_radar.http import FetchError
from placement_radar.keys import make_key
from placement_radar.sources import ashby, greenhouse, lever, workday
from placement_radar.state import load_seen, update

# maps the platform name in sources.yaml to the function that reads that platform
# adding a new platform later = writing its adapter, then adding one line here
ADAPTERS = {
    "greenhouse": greenhouse.fetch,
    "lever": lever.fetch,
    "ashby": ashby.fetch,
    "workday": workday.fetch,
}

def collect(sources, adapters=ADAPTERS):
    # reads every source and returns 2 lists: postings (cleaned and keyed), health: one row per source saying how it went (saved as health.json later)
    postings, health = [], []
    for cfg in sources:
        # start each health row as a success with 0 counts
        healthRow = {"company": cfg["company"], "platform": cfg["platform"], "found": 0, "kept": 0, "error": ""}
        try:
            # look up right adapter by platform name and run it
            found = adapters[cfg["platform"]](cfg)
        except (FetchError, KeyError, ValueError) as error:
            # FetchError = site failed, KeyError = typo in sources.yaml, ValueError = site sent back something that wasnt valid json
            # record problem and move on, one broken source shouldnt cancel rest
            healthRow["error"] = f"{type(error).__name__}: {error}"
            health.append(healthRow)
            continue
        # keep only the early career roles
        kept = [posting for posting in found if is_early_careers(posting)]
        for posting in kept:
            # clean the text, make note if any suspicious text was removed
            posting.description, posting.suspicious = clean_text(posting.description)
            # giving each posting its own key
            posting.key = make_key(posting.company, posting.title, posting.location)
        healthRow["found"], healthRow["kept"] = len(found), len(kept)
        postings += kept
        health.append(healthRow)
    return postings, health


def write_json(path, data):
    #saves data as indented json, creating data folder if needed
    # ensure_ascii=False keeps characters readable 
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    # argv lets tests point the run at temp folder. normally its empty and poitns at current folder
    root = Path(argv[0]) if argv else Path(".")

    #read list of sources e.g. [{"company": "monzo", "platform": "greenhouse", "board": "monzo"}]
    sources = yaml.safe_load((root / "sources.yaml").read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date().isoformat()  # turns date into YYYY-MM-DD format
    # 1. read every source
    postings, health = collect(sources)
    # 2. compare with whats been seen before. keep recent ones
    recent, seen = update(postings, load_seen(root/"data"/"seen.json"), today)
    # save the output files. new_postings.json keeps every posting in one file for reference,
    # cowork reads the smaller index and the per posting files below instead
    write_json(root/"data"/"new_postings.json", {
        "generated": now.isoformat(timespec="seconds"),
        "window_days": 2,
        "postings": [posting.to_dict() for posting in recent],
    })
    # postings/ holds one small file per recent posting with its full description
    # cleared each run so it only holds what is inside the window
    postingsFolder = root / "data" / "postings"
    shutil.rmtree(postingsFolder, ignore_errors=True)
    for posting in recent:
        write_json(postingsFolder / f"{posting.key}.json", posting.to_dict())
    # the index lists every recent posting without its description
    # so it stays small enough for cowork to read in one go
    write_json(root / "data" / "new_postings_index.json", {
        "generated": now.isoformat(timespec="seconds"),
        "window_days": 2,
        "postings": [
            {field: value for field, value in posting.to_dict().items() if field != "description"}
            for posting in recent
        ],
    })
    # health.json says which sources worked, cowork uses it to know what to skip
    write_json(root/"data"/"health.json", {"generated": now.isoformat(timespec="seconds"), "sources": health})
    # seen.json is memory fo next time
    write_json(root/"data"/"seen.json", seen)
    # one summary line for the terminal and github actions log
    errors = sum(1 for healthRow in health if healthRow["error"])
    print(f"{len(sources)} sources, {len(postings)} early careers postings, {len(recent)} new, {errors} errors")

# only runs main when this file is started directly, not when it is imported by a test
if __name__ == "__main__":
    main(sys.argv[1:])