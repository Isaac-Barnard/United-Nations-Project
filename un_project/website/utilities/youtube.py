import feedparser

CHANNEL_ID = 'UCmH46kUnnHgBSCgODH_Gd7w'
FEED_URL = f'https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}'

def get_latest_video_id():
    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        return None
    latest_entry = feed.entries[0]
    video_url = latest_entry.link
    # Extract video ID from URL, e.g. https://www.youtube.com/watch?v=VIDEO_ID
    video_id = video_url.split('=')[-1]
    return video_id