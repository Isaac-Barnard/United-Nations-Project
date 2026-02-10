import feedparser
import re

CHANNEL_ID = 'UCmH46kUnnHgBSCgODH_Gd7w'
FEED_URL = f'https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}'

def get_latest_video_id():
    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        return None
    latest_entry = feed.entries[0]
    video_url = latest_entry.link
    
    # Extract just the 11-character video ID
    match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', video_url)
    if match:
        return match.group(1)
    return None