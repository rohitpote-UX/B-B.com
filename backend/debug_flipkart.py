"""Debug shoes/watches card layout"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36", "Accept-Language": "en-IN,en;q=0.9"}

resp = requests.get("https://www.flipkart.com/search?q=running+shoes+men", headers=HEADERS, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")
cards = soup.select("div[data-id]")
print(f"Cards: {len(cards)}")
if cards:
    c = cards[0]
    print("HTML:", str(c)[:2000])
    print("\n--- Classes ---")
    for el in c.find_all(True):
        if el.get("class") and el.get_text(strip=True):
            print(el.name, el.get("class"), "|", el.get_text(strip=True)[:80])
