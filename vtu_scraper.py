import requests
from bs4 import BeautifulSoup

VTU_URL = "https://vtu.ac.in/category/examination/"

def fetch_vtu_updates():
    updates = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(VTU_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Try multiple patterns — whichever exists will be used
        selectors = [
            "h3.entry-title a",
            ".entry-title a",
            ".grid-post .entry-title a"
        ]

        notices = []
        for selector in selectors:
            notices = soup.select(selector)
            if len(notices) > 0:
                break

        for n in notices[:6]:
            title = n.get_text(strip=True)
            link = n["href"] if n["href"].startswith("http") else ("https://vtu.ac.in" + n["href"])
            updates.append({"title": title, "link": link})

    except Exception as e:
        print("VTU fetch error:", e)

    print("VTU test:", updates)  # watch this in terminal
    return updates