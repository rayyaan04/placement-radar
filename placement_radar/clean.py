# turns raw job description text into plaintext, removes anything hidden or aimed at ai instruction injection before cowork reads it
import html
import re

#invisible unicode characters, which can hide words
ZERO_WIDTH = re.compile("[\u200b-\u200f\u2028-\u202e\u2060-\u2064\ufeff]")

# html element styled to be invisible by using "style=display:none"
HIDDEN = re.compile(
    r"<([a-z0-9]+)[^>]*(display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0)[^>]*>.*?</\1>",
    re.I | re.S,  # i ignores whether its upper or lowercase, s lets . match across new lines
)

#script and style blocks need to be removed - they are code and not text
SCRIPT = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.I | re.S)

# turns tags that end line/paragraph into real new lines
BREAKS = re.compile(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", re.I)

# any remaining html tag, eg <b> or <a href="...">
TAGS = re.compile(r"<[^>]+>")

# phrases that try to give instructions to an ai reading the page
SUSPICIOUS = re.compile(
    r"ignore (all |any )?(previous|prior|above) instructions|you are (an? )?(ai|assistant|language model)\b|system prompt",
    re.I,
)

def clean_text(raw):
    # returns clean text and a flag that checks if anything suspicious was found
    # 1)turn escaped html into standard html form
    text = html.unescape(raw or "")
    # 2) remove hidden elements first, so their words dont get into any plaintext
    text = HIDDEN.sub(" ", text)
    # 3)remove script and style code
    text = SCRIPT.sub(" ", text)
    # 4) line breaking tags become \n
    text = BREAKS.sub("\n", text)
    # 5) every other tag is removed, leaving just words
    text = TAGS.sub(" ", text)
    # 6)delete invisible characters
    text = ZERO_WIDTH.sub("", text)
    # 7) go line by line dropping suspicious lines and fix up the spacing
    kept, suspicious = [], False
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if SUSPICIOUS.search(line):
            # flag suspicious as true, and leave this line out
            suspicious = True
            continue
        if line:
            # keep non empty lines
            kept.append(line)
    # join the kept lines back into single string
    return "\n".join(kept), suspicious