#tests for #keys.py, each test checks one rule about how keys are built
from placement_radar.keys import make_key, slug

def test_slug():
    #turns dots and spaces into hypens, and makes everything lowercase - slug format
    assert slug("J.P. Morgan") == "j-p-morgan"

def test_key_shape():
    k = make_key("AMD", "Summer 2027 Software Engineer Intern", "Edinburgh, UK")
    #readable part: company_title_first_location
    assert k.startswith("amd_summer-2027-software-engineer-intern_edinburgh_")
    #splits on the last underscore - part after is the 6 character hash
    assert len(k.rsplit("_", 1)[1]) == 6

def test_same_title_different_city():
    #two jobs in diff cities must not be treated as one
    a = make_key("AMD", "Software Intern", "Edinburgh")
    b = make_key("AMD", "Software Intern", "Cambridge")
    assert a != b

def test_long_titles_stay_distinct():
    # titles are identical for 70 characters, and are different at the end
    # the readable part is cut at 60 so it matches, the hash must tell them apart
    base = "x" * 70
    assert make_key("Co", base + "a", "") != make_key("Co", base + "b", "")