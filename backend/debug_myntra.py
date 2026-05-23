"""
Debug Myntra API endpoints - check if Myntra has accessible JSON APIs
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.myntra.com/",
    "X-Meta-App": "appFamily=Web2.0",
    "x-myntra-abtest": "cms-ux:v2;",
}

# Try known Myntra search API patterns
endpoints = [
    "https://www.myntra.com/gateway/v2/search/shirts?rows=50&o=0&plaEnabled=false",
    "https://www.myntra.com/gateway/v2/search/shoes?rows=50&o=0",
    "https://www.myntra.com/gateway/v2/search/men-tshirts?rows=50&o=0",
    "https://www.myntra.com/v1/products/search?q=shirts&rows=50",
    "https://myntra.com/gateway/v2/search?query=shirts&rows=24&o=0",
]

for url in endpoints:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        print(f"\nURL: {url}")
        print(f"Status: {resp.status_code} | Content-Type: {resp.headers.get('Content-Type','')}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                print("JSON keys:", list(data.keys())[:10])
                print("Sample:", str(data)[:300])
            except:
                print("Not JSON. Body snippet:", resp.text[:200])
    except Exception as e:
        print(f"Error for {url}: {e}")
