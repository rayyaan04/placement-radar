# reads csv export of trackers Roles and Filtered out tabs. joins them on link and writes to dataset.csv
# adds the agents decision field - shows whether the posting was filtered out or not
# text comes from postings from the data/archive folder - so only postings that come from this placement radar get text (reduces scope of the dataset, slight limitation))
import json
from pathlib import Path
import pandas as pd

archiveFolder = Path("data/archive")
evaluationFolder = Path("evaluation")
sampleSize = 300 # no. of postings i will hand label the verdict for

def clean_url(url):
    # lowercase, drop everything after ? or #, drop any trailing slashes
    # keeps consistency in urls, and also so same posting link matches even when written slightly differently
    url = str(url).strip().lower().split("?")[0].split("#")[0]
    return url.rstrip("/")

def load_archive():
    # reads every archived posting file into a table
    rows = []
    for filePath in archiveFolder.glob("*.json"):
        posting = json.loads(filePath.read_text(encoding="utf-8"))
        rows.append({
            "url": posting.get("url", ""),
            "company": posting.get("company", ""),
            "title": posting.get("title", ""),
            "location": posting.get("location", ""),
            "description": posting.get("description") or "", # has "or" as the value of description key COULD be None, so let it be None instead of "" if so
        })
    archive = pd.DataFrame(rows)
    archive["match_url"] = archive["url"].apply(clean_url)
    return archive

def load_tracker():
    # reads 2 tracker exports (roles and filtered out) and then stacks them into one table 
    roles = pd.read_csv(evaluationFolder/"roles.csv")
    filtered = pd.read_csv(evaluationFolder/"filtered.csv")

    roles["agent_decision"] = "eligible"
    roles.loc[roles["Posting state"] == "Filtered", "agent_decision"] = "not eligible" # changes state to not eligible if the role is filtered (from a refresh)
    roles["requirements_unread"] = roles["Flags"].str.contains("Requirements unread", na = False)  # checks if a role has requirements unread, adds a column that shows that it is (used to report agents scores with and without these weak decisoins later)

    filtered["agent_decision"] = "not eligible"
    filtered["requirements_unread"] = False # requirements unmet column only covers roles - but its still needed in filtered csv so it can be concatenated to roles

    # keep only the columns needed, then stack filtered rows below roles rows in one table
    columns = ["Posting link", "agent_decision", "requirements_unread"]
    tracker = pd.concat([roles[columns], filtered[columns]], ignore_index=True)
    tracker["match_url"] = tracker["Posting link"].apply(clean_url)
    tracker = tracker[tracker["Posting link"].notna()]

    duplicateCount = tracker["match_url"].duplicated().sum()
    print(f"{duplicateCount} tracker links appear 1+ times, keeping first of each")
    tracker = tracker.drop_duplicates(subset="match_url", keep="first")

    # links whose copies disagree on the agent's decision
    decisionCounts = tracker.groupby("match_url")["agent_decision"].nunique()
    print((decisionCounts > 1).sum(), "links have conflicting decisions")

    return tracker[["match_url", "agent_decision", "requirements_unread"]]


def main():
    archive = load_archive()
    tracker = load_tracker()

    # keep only archived postings that have a tracker row, then add its decision
    pool = archive.merge(tracker, on="match_url", how="inner")
    pool = pool[pool["description"].str.strip() != ""]

    print(f"{len(archive)} archived postings, {len(pool)} matched tracker row with a description")
    print(pool["agent_decision"].value_counts().to_string())
    pool.to_csv(evaluationFolder/"pool.csv", index=False)

    # random sample to label, same 300 every run cus of the fixed seed
    dataset = pool.sample(n=min(sampleSize, len(pool)), random_state=4)
    dataset.to_csv(evaluationFolder/"dataset.csv", index=False)

    # creating a seperate copy with agents decision columns left out, so i can label them blind
    toLabel = dataset[["url", "company", "title", "location", "description"]].copy()
    toLabel["my_label"] = ""
    labelFile = evaluationFolder/"to_label.csv"
    # never overwrite labels i have already labelled it
    if labelFile.exists() and pd.read_csv(labelFile)["my_label"].notna().any():
        print("to_label.csv already has labels, not overwriting it")
    else:
        toLabel.to_csv(labelFile, index=False)
    print(f"wrote {len(dataset)} postings to dataset.csv and to_label.csv")


if __name__ == "__main__":
    main()