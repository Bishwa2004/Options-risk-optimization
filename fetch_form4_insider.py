import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_form4_insider_trades(cik, limit=10):
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&owner=only&count={limit}&output=atom"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "xml")
    entries = soup.find_all("entry")

    data = []
    for entry in entries:
        title = entry.title.text
        date = entry.updated.text
        link = entry.link['href']
        data.append({"title": title, "date": date, "link": link})

    return pd.DataFrame(data)
