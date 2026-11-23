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

def fetch_json(url, method="GET", body=None, tries=3, timeout=20, session=None, sleep=time.sleep, waits=(5, 15)):
    # gets a url and returns its json as dict and list
    # method: GET to read POST to send a search
    # body: json to send with a POST
    # tries: how many attempts before giving up
    # timeout: seconds to wait for reply before giving up on attempt
    # waits: seconds to wait after each failed try, longer each time
    # session and sleep are swapped for mocks in testing
    httpSession = session or requests.Session()
    last = "no attempt"  # remembers latest problem for final error msg
    for attempt in range(tries):
        retryAfter = ""  # seconds the site asked us to wait, if it said
        try:
            response = httpSession.request(method, url, json=body, timeout=timeout, headers={"User-Agent": UA, "Accept": "application/json"})
        except requests.RequestException as error:
            # network problem (no connection/timeout, retry)
            last = str(error)
        else:
            # reply obtained, check its status code. 200 = ok
            if response.status_code == 200:
                return response.json()
            if response.status_code not in RETRY:
                # not a server problem, or not too many requests, not worth retrying
                raise FetchError(f"http {response.status_code} for {url}")
            last = f"http {response.status_code} for {url}"
            # a 429 reply can say how many seconds to wait in its retry-after header
            retryAfter = response.headers.get("Retry-After", "")
        if attempt < tries - 1:
            # wait longer each time, 5s then 15s
            wait = waits[min(attempt, len(waits) - 1)]
            if retryAfter.isdigit():
                # wait at least as long as the site asked, capped at 2 minutes so a run cant hang
                wait = min(max(wait, int(retryAfter)), 120)
            sleep(wait)
    # if every try failed
    raise FetchError(last)