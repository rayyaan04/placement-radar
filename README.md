# Internship/Placement Radar
A script which fetches internships or placements to a set list of companies whose postings are found on workday, ashby, greenhouse and lever to be read by a scheduled Claude Cowork algorithm and add to a list of tracked postings
Used to integrate into a Claude Cowork scheduled flow to search for internships and placements across a wide array of sites. 


## Tests badge
[![tests](https://github.com/rayyaan04/placement-radar/actions/workflows/tests.yml/badge.svg)](https://github.com/rayyaan04/placement-radar/actions/workflows/tests.yml)

## Why this exists
This script is used as many careers sites only show listings after JavaScript runs - so a plain page fetch sees nothing. Certain sites robots.txt also limits access, resulting in a need for this. These factors limit Claude from accessing jobs posted on websites which do these things, so this script was made to fetch them myself, have GitHub Actions run it every 3 hours, and then have its results be checked alongside everything else for my daily digest.

## How it works 
The script requests every open job from each company’s feed (on their respective platforms), then keeps only early careers titles
These job postings are then transformed into JSON, where the descriptions are cleaned to be safe plaintext, each job is given a unique key, and then added along to new_postings.json alongside all of its other relevant information. new_postings.json only holds roles first seen in the last 2 days
Each (kept) job that is found has its key put into seen.json so it can be used as memory for when GitHub actions starts every 3 hours so that duplicate jobs arent added
The output data fetched by this script (found in `/data`) is then checked by Cowork to add to the list on its daily run

Flow: `sources.yaml` → `adapters` → `filter` → `clean` → `key` → `seen.json` 
## Project structure
`/sources` - Contains the fixtures for Ashby, Greenhouse, Workday and Lever. These all fetch jobs from the list of companies in `sources.yaml` which correspond to their respective sites, and then builds a Posting for each job.
`clean.py` - Turns raw job description text into plaintext - turns breaks into new lines, removes any zero width characters, hidden text (text hidden with display:None, 0 font size, visibility hidden), scripts, tags and any "suspicious" text. Suspicious text is one that is aimed at AI injection - e.g. "ignore all instructions and do x." If this is found, it is flagged and removed for the clean output.
`filter.py` - First filter pass on job titles - keep only early careers jobs (internships/placement year) and ignore any senior positions. Cowork still makes a real eligibility decision later, so this isn't the only check
`http.py` - Calls job platform apis to fetch their JSON to be used to write a Posting. This has a maximum of 3 tries, with a timeout window of 20 seconds. If this takes more than 3 tries or more than 20 seconds to fetch the data, or returns an error that isnt a server problem/error 429, it gives up and moves on. 
`keys.py` - Builds a unique key for each job posting, so each one can be identified and any duplicates can be checked for. Key is made by turning the company name, job title and location into a slug (max 60 chars), and then appending a fingerprint made with a SHA1 hash based on the slug created to make a unique hash that identifies each job as its own (as each string has its own very unique hash that cannot be replicated)
`models.py` - The base for the Posting class. This contains the shape of the job posting which the fetcher passes around, as well as a method to turn it into a dict so it can be saved as JSON
`run.py` - The main program; it reads every source in `sources.yaml`, collects every posting for a given company and writes results to `health.json`, `seen.json` and `new_postings.json`, alongside the date and time it was first seen.
`state.py` - Remembers which postings have been seen before and picks out the ones first seen in the last 2 days

## Platforms & adding a company
Most big employers' careers sites are a front end for one of a few hiring platforms. Each platform publishes its jobs as JSON, and the fetcher has one adapter per platform that turns that JSON into postings.

| Platform | Job links look like | `sources.yaml` needs |
| --- | --- | --- |
| Greenhouse | `job-boards.greenhouse.io/<board>/jobs/...` or `boards.greenhouse.io/<board>` | `board` |
| Lever | `jobs.lever.co/<board>/...` | `board` |
| Ashby | `jobs.ashbyhq.com/<board>/...` | `board` |
| Workday | `<tenant>.wd<N>.myworkdayjobs.com/en-US/<site>/job/...` | `host`, `tenant`, `site` |

Companies that run their own systems (Google, Apple, Meta, Microsoft and most banks) aren't covered with these.

### Adding a company

1. Open the company's careers site and click into any job.
2. Look at the job's link, or the link behind its "Apply" button, and match it to a row in the table. If it isn't on one of the four platforms, the fetcher can't read it.
3. Copy the parts the table names straight from the link, and add an entry to `sources.yaml`.
4. Run `python -m placement_radar.run` and check the company's row in `data/health.json`. A working source shows a `found` count above 0 and an empty `error`.

Greenhouse, Lever and Ashby entries need just a board name:

    - company: Anthropic
      platform: greenhouse
      board: anthropic

A Workday entry takes its three parts from a job link like `https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/...`:

    - company: NVIDIA
      platform: workday
      host: nvidia.wd5.myworkdayjobs.com
      tenant: nvidia
      site: NVIDIAExternalCareerSite


### Common mistakes

- **Guessing the board name.** It isn't always the company name: Hudson River Trading's Greenhouse board is `wehrtyou`, Optiver's is `optiverus` and DoorDash's is `doordashusa`. Always copy it from a real link.
- **Guessing Workday's `site`.** A wrong site or tenant fails with `FetchError: http 422` in `health.json`. The only reliable source is a real job link.
- **A board with fewer jobs than expected.** Some companies split roles across several boards or post some roles elsewhere, so a low `found` count may be resolved by checking their site.

## Output files
### Example output from `new_postings.json`:
    {
      "company": "Stripe",
      "title": "Software Engineer, Intern",
      "location": "London",
      "url": "https://stripe.com/jobs/search?gh_jid=8130867",
      "source": "greenhouse",
      "posted": "2026-10-29",
      "description": "Who we are\nAbout Stripe\nStripe is a technology company focused on improving the conditions for economic growth and prosperity. We build programmable financial infrastructure, rethinking from first principles how financial services should work, to make it easier and cheaper for any business to start and scale. (rest of the description is trimmed to save space)",
      "key": "stripe_software-engineer-intern_london_6e57c5",
      "first_seen": "2026-11-08",
      "suspicious": false
    },

### Example output from `health.json`:
    {
      "company": "Stripe",
      "platform": "greenhouse",
      "found": 766,
      "kept": 21,
      "error": ""
    },
The error field would not be empty if there was suspicious text found, the link doesnt work, or any other error alongside its code

### Example output from `seen.json`
    "stripe_software-engineer-intern_london_6e57c5": "2026-11-08",

## Safety
- Descriptions are stripped of HTML, hidden text, zero width characters leaving only the plaintext. Line breaks are replaced with actual new lines, aswell
- Any text aimed at an AI to inject their own instructions is removed and posting is flagged as `suspicious`
- Requests identify themselves with a User-Agent, and retries once every 2 seconds, and stops trying after 3 attempts to not send too many requests to their server
- An error 404 fails fast, and does not stop the run
## Running locally
In powershell:
   ``python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python -m placement_radar.run
    python -m pytest -q``
> 
## Github Actions
`tests.yml` runs on every push, `fetch.yml` runs on every 3 hours on the 17th minute (to avoid thelarge amount of traffic at 0th minute), and then commits data/ back to the repo

## Limitations
- **Companies who are on their own system** - Google, Apple, Microsoft, Meta are not covered by this, and will instead be left to the Cowork daily run.
- **Workday site names have to be copied from a real job link** - takes a bit more effort to add, and can be wrong and result in errors if done wrong
- **`seen.json` only grows** - can get very large
- **Filter only reads titles** - `is_early-careers` matches for mentions of intern and placement in title, if there are any unusual postings aimed for students that don't match this, they will be missed
- **GitHub's schedule isn't exact.** Scheduled runs often start late and are occasionally skipped. Because of the 2 day window and Cowork's own duplicate check, a skipped run doesn't lose postings.
- **Workday's feed is undocumented.** Greenhouse, Lever and Ashby publish their feeds for public use. The Workday address is the one its own careers pages use internally, so it could change without notice. A change would show up as errors in `health.json`.

## Credits
Madz Lorentzen ai job search - [Link](https://github.com/ai-job-search-dev/ai-job-search/tree/master) : Took inspiration from this repo to make this to search for internships and placements
