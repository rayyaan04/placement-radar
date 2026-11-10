# builds a stable id (key) for each posting. Same job gets the same key, so we can tell if theres a duplicate
import hashlib
import re

def slug(text):
    # turns text into slug to be able to be used as a key
    # lowercases it, then turns anything that isnt a letter or number into a hyphen
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")

def make_key(company, title, location):
    #creates the key. only the first location counts
    # splits on ; , / | so only takes the city name
    first = re.split(r"[;,/|]", location or "")[0]

    # full version of the key, only used to maek the hash
    full = f"{slug(company)}_{slug(title)}_{slug(first)}"

    # uses sha1 as hash, turns text into a fingerprint - we only keep first 6 chars
    fingerprint = hashlib.sha1(full.encode()).hexdigest()[:6]
    #create a readable key - cut title to 60 characters so keys stay short
    return f"{slug(company)}_{slug(title)[:60]}_{slug(first)}_{fingerprint}"

