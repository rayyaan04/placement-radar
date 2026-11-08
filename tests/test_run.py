from placement_radar.http import FetchError
from placement_radar.models import Posting
from placement_radar.run import collect

def test_collect_keeps_early_careers_and_records_errors():
    # fake adapter that works: one student and one senior job
    def working(cfg):
        return [Posting("ryoshu", "Software Intern", "London", "u1", "fake", description="<p>Hi</p>"),
                Posting("ryoshu", "Senior Engineer", "London", "u2", "fake")]

    # fake adapter that fails like a broken website
    def broken(cfg):
        raise FetchError("http 404")

    sources = [{"company": "ryoshu", "platform": "working"}, {"company": "bad", "platform": "broken"}]
    postings, health = collect(sources, adapters={"working": working, "broken": broken})
    # check that only student job is kept
    assert [posting.title for posting in postings] == ["Software Intern"]
    # its html was cleaned, and given a key
    assert postings[0].description == "Hi" and postings[0].key.startswith("ryoshu_software-intern_london_")
    # health records 2 found, 1 kpt, no error for working soruce
    assert health[0] == {"company": "ryoshu", "platform": "working", "found": 2, "kept": 1, "error": ""}
    # error for broken one
    assert health[1]["error"].startswith("FetchError")


def test_main_writes_outputs(tmp_path, monkeypatch):
    # top path is throwaway folder made by pytest for this test
    # monkeypatch lets us add fake platform for this test
    import json
    from placement_radar import run

    monkeypatch.setitem(run.ADAPTERS, "fake", lambda cfg: [Posting("ryoshu", "Data Intern", "Leeds", "u", "fake")])
    (tmp_path / "sources.yaml").write_text("- company: ryoshu\n  platform: fake\n")
    run.main([str(tmp_path)])
    newPostings = json.loads((tmp_path / "data" / "new_postings.json").read_text())
    assert [posting["title"] for posting in newPostings["postings"]] == ["Data Intern"]
    run.main([str(tmp_path)])  # second run same day: still inside the window, nothing duplicated
    seen = json.loads((tmp_path / "data" / "seen.json").read_text())
    assert len(seen) == 1