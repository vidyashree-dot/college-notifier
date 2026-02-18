import feedparser
import ssl

# Disable SSL certificate verification (fix for your laptop)
ssl._create_default_https_context = ssl._create_unverified_context

RSS_FEEDS = [
    "https://www.freejobalert.com/feed/",
    "https://www.sarkariexam.com/feed",
    "https://freshersnow.com/feed"
]

KEYWORDS = [
    "recruitment", "vacancy", "hiring", "jobs", "freshers",
    "engineer", "trainee", "2025",
    "bank", "railway", "ssc", "upsc",
    "tcs", "wipro", "infosys", "amazon", "accenture", "hcl"
]

def get_all_jobs():
    jobs = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:30]:
            title = entry.title.lower()
            if any(keyword in title for keyword in KEYWORDS):
                jobs.append({"title": entry.title, "link": entry.link})
    
    return jobs[:12]   # latest 12 jobs only