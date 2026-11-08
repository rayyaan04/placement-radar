# sharped helper for calling job platform apis
# handles timeouts retries and errors in one place so it isnt repeated by adaptors
import time
import requests

# identifies us to the sites we call
UA = "placement-radar/0.1 (+https://github.com/rayyaan04/placement-radar)"
# http status codes that usualy mean try again later
# 429 = too many requests, 5xx = server had a temp problem
RETRY = {429, 500, 502, 503, 504}

class FetchError(Exception):
    # custom error type so run.py can catch fetch problems specifically
    pass

def fetch_json(url, method="GET", body=None, tries=3, timeout=20, session=None, sleep=time.sleep):
    # gets a url and returns its json as dict and list
    #method: GET to read POST to send a search
    # body: json to send with a POST
    # tries: how many attempts before giving up
    # timeout: seconds to wait for reply before giving up on attempt
    # session and sleep are swapped for mocks in testing
    s = session or requests.Session()
    last = "no attempt" # remembers latest problem for final error msg
    for i in range(tries):
        try: 
            r = s.request(method, url, json=body, timeout=timeout, headers={"User-Agent": UA, "Accept": "application/json"})
        except requests.RequestException as e:
            # network prolem (no connection/timeout, retry)
            last = str(e)
        else:
            # reply obtained, check its status code. 200 = ok
            if r.status_code == 200:
                return r.json()
            if r.status_code not in RETRY: 
                # not a server problem, or not too many requests, not worth retrying
                raise FetchError(f"http {r.status_code} for {url}")
            last = f"http {r.status_code} for {url}"
        if i < tries - 1:
            # wait before next try, so it doesnt send too many requests at once
            sleep(2)
    #if every try failed
    raise FetchError(last)