# tests for each websites adapter 
# each test feeds the adapter a sample response

from placement_radar.sources import ashby, greenhouse, lever

def test_greenhouse(fixture):
    out = greenhouse.fetch({"company": "Ryoshu", "board": "ryoshu"}, get=lambda url: fixture("greenhouse.json"))
    assert len(out) == 2 # both jobs in sample come back
    assert out[0].title == "Software Engineering Intern, 2027"
    assert out[0].location == "London, UK" # pulled out of location field
    assert out[0].posted == "2026-11-05" # timestamp cut down to the date

def test_lever(fixture):
    out = lever.fetch({"company": "Ryoshu", "board": "acme"}, get=lambda url: fixture("lever.json")) 
    assert out[0].location == "Cambridge" 
    assert out[0].posted == "2025-11-05" #miliseconds turned into date

def test_ashby(fixture):
    out = ashby.fetch({"company": "Ryoshu", "board": "ryoshu"}, get=lambda url: fixture("ashby.json"))
    assert out[0].url == "https://jobs.ashbyhq.com/ryoshu/x1"