# tests for http.py 
# Response and Session are mock values that pretend to be from internet to test retries without using real requests
import pytest 
import requests

from placement_radar.http import FetchError, fetch_json

class Response:
    # fake reply: status code and some json
    def __init__(self, code, data=None):
        self.status_code, self._data = code, data

    def json(self):
        return self._data


class Session:
    #fake session: hands back prepared replies in order and counts cells
    def __init__(self, replies):
        self.replies, self.calls = list(replies), 0

    def request(self, *a, **k):
        self.calls += 1
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

# sleep=lambda s: None replaces the real wait with nothing, so tests run instantly

def test_returns_json():
    # a 200 reply gives back its json
    assert fetch_json("u", session=Session([Response(200, {"ok": 1})]), sleep=lambda s: None) == {"ok": 1}

def test_retries_then_succeeds():
    #server error then network error, then success; should end with json
    s = Session([Response(503), requests.ConnectionError("down"), Response(200, [1])])
    assert fetch_json("u", session=s, sleep=lambda s: None) == [1]
    assert s.calls == 3 # check if it really tried 3 times

def test_gives_up_after_tries():
    # 3 fails in a row shouldBe FetchError
    s = Session([Response(503), Response(503), Response(503)])
    with pytest.raises(FetchError):
        fetch_json("u", session=s, sleep=lambda s: None)

    def test_no_retry_on_404():
        # 404 meanss wrong address so fail without retry
        s = Session([Response(404)])
        with pytest.raises(FetchError):
            fetch_json("u", session=s, sleep=lambda s: None)
        assert s.calls == 1