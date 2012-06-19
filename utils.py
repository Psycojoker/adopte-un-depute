import feedparser
from dateutil.parser import parse

def prepare_rss(rss):
    entries = feedparser.parse(rss).entries[:10]
    for entrie in entries:
        entrie["published"] = parse(entrie["published"])
    return entries
