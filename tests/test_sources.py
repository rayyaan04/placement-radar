# tests for each websites adapter 
# each test feeds the adapter a sample response

from placement_radar.sources import ashby, greenhouse, lever, workday

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



def test_workday(fixture):
    calls = [] # records every call adapter marks

    def get(url, method="GET", body=None):
        # fake download: POST = the job list, GET = detail of one job
        calls.append((method, url))
        return fixture("workday_detail.json") if method == "GET" else fixture("workday_list.json")

    cfg = {"company": "AMD", "host": "amd.wd1.myworkdayjobs.com", "tenant": "amd", "site": "External", "searches": ["intern"]}
    out = workday.fetch(cfg, get=get)
    assert len(out) == 2 # intern and principal engineer
    intern = next(posting for posting in out if "Intern" in posting.title)
    # public link is built from host, site, and job path
    assert intern.url == "https://amd.wd1.myworkdayjobs.com/en-US/External/job/Edinburgh/Summer-2027-Software-Engineer-Intern_JR1"
    assert "Python" in intern.description # description came from detail GET call
    assert [method for method, _ in calls] == ["POST", "GET"] # one list (post) and one detail (get) call for intern only. principal isnt early careers, so no detail call for it