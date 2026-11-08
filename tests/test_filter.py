# tests for filter.py 
from placement_radar.filter import is_early_careers
from placement_radar.models import Posting

def p(title, key=""):
    # makes a test posting with just title and key
    return Posting("Co", title, "London", "u", "test", key=key)
def test_early_careers():
    assert is_early_careers(p("Software Engineering Intern"))
    assert is_early_careers(p("Industrial Placement 2027/28"))
    assert is_early_careers(p("Spring Week 2027"))
    assert not is_early_careers(p("Senior Software Engineer")) # not lf senior roles
    assert not is_early_careers(p("Internal Tools Engineer")) # internal is not intern
    