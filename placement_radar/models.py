from dataclasses import dataclass, asdict

@dataclass
class Posting:
    company: str
    title: str
    location: str
    url: str
    source: str
    posted: str = "" #given by source
    description: str = ""
    key: str = ""
    first_seen: str = "" 
    suspicious: bool = False

    def to_dict(self):
        return asdict(self)