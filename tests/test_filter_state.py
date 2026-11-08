# tests for filter.py and state.py
from placement_radar.filter import is_early_careers
from placement_radar.models import Posting
from placement_radar.state import update

def make_posting(title, key=""):
    # makes a test posting with just title and key
    return Posting("Co", title, "London", "u", "test", key=key)
def test_early_careers():
    assert is_early_careers(make_posting("Software Engineering Intern"))
    assert is_early_careers(make_posting("Industrial Placement 2027/28"))
    assert is_early_careers(make_posting("Spring Week 2027"))
    assert not is_early_careers(make_posting("Senior Software Engineer")) # not lf senior roles
    assert not is_early_careers(make_posting("Internal Tools Engineer")) # internal is not intern

def test_update_marks_new_and_keeps_window():
    # already seen: one job from a week ago, one from yesterday
    seen = {"old": "2026-11-01", "yday": "2026-11-06"}
    # this run finds both again, plus a new job twice (eg from two searches)
    postings = [make_posting("a", "old"), make_posting("b", "yday"), make_posting("c", "new"), make_posting("c", "new")]
    recent, updatedSeen = update(postings, seen, "2026-11-07")
    # yesterday and today are inside the 2 day window, last week is not
    assert {posting.key for posting in recent} == {"yday", "new"}
    # new job recorded as first seen today, old date untouched
    assert updatedSeen["new"] == "2026-11-07" and updatedSeen["old"] == "2026-11-01"