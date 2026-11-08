# reads jobs from workday - used by nvidia and big banks
# workday works differently as it does not have one public feed - where one POST search returns 20 jobs at a time with the given search
# each listing in the POST search has no description - needs another request call for its details for each job
from placement_radar.filter import is_early_careers
from placement_radar.http import fetch_json
from placement_radar.models import Posting

def fetch(cfg, get=fetch_json, page=20, max_pages=10):
    # cfg needs company, host, tenant (company using site) and site taken from real job link
    # e.g. https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/
    # host = nvidia.wd5.myworkdayjobs.com, tenant = nvidia, site = NVIDIAExternalCareerSite
    # page = jobs given per request, max_pages = safety limit so one company cant infinitely loop
    base = f"https://{cfg['host']}/wday/cxs/{cfg['tenant']}/{cfg['site']}"
    # found dict maps each jobs path to its Posting
    found = {}
    # search once per term - intern, and placement
    for term in cfg.get("searches", ["intern", "placement"]):
        offset = 0 # how many results to skip, where 0 = first page
        for i in range(max_pages):
            # request for one page of results matching search term
            data = get(f"{base}/jobs", method = "POST", body={"appliedFacets": {}, "limit": page, "offset": offset, "searchText": term})
            jobs = data.get("jobPostings", [])
            for job in jobs:
                # externalPath is the jobs own path, e.g. /job/London/Software-Intern
                path = job.get("externalPath", "")
                found[path] = Posting(
                    company=cfg["company"],
                    title=job.get("title", ""),
                    location=job.get("locationsText", ""),
                    url=f"https://{cfg['host']}/en-US/{cfg['site']}{path}",
                    source="workday",
                    posted=job.get("postedOn", ""), # text like "posted 3 days ago"
                )
            # move onto next page
            offset += page
            # stop when page is empty, or we have passed total no. of jobs
            if not jobs or offset >= data.get("total", 0):
                break
    for path, p in found.items():
        if is_early_careers(p):
            info = get(f"{base}{path}").get("jobPostingInfo", {})
            p.description = info.get("jobDescription", "")
    return list(found.values())
    