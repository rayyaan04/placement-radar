# the shape of the job posting the fetcher passes around 
from dataclasses import dataclass, asdict


@dataclass # using dataclass initialises automatically
class Posting:
    company: str # company name written in sources
    title: str # title of job as given
    location: str # location text e.g. "London, UK"
    url: str #link to the job page
    source: str # the platform it came from e.g. workday
    posted: str = "" # date posted, in whichever form the platform gives
    description: str = "" # full job text - cleaned later
    key: str = "" # stable id, filled in by make_key later
    first_seen: str = ""  # date the fetcher first found it
    suspicious: bool = False # turns true if there is text which is aimed to make ai perform instructions (which is then removed)

    def to_dict(self):
        # turns posting into a dict so it can be saved as json
        return asdict(self)