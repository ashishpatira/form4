import time
import requests

SEC_USER_AGENT = "Sp500KeywordExtractor/1.0 (placeholder@example.com)"
headers = {"User-Agent": SEC_USER_AGENT}
url1 = "https://www.sec.gov/files/company_tickers.json"
url2 = "https://data.sec.gov/submissions/CIK0000320193.json" # AAPL

# Without session
start = time.time()
for _ in range(3):
    requests.get(url1, headers=headers)
    time.sleep(0.15)
    requests.get(url2, headers=headers)
    time.sleep(0.15)
print(f"requests.get: {time.time() - start:.2f}s")

# With session
session = requests.Session()
session.headers.update(headers)
start = time.time()
for _ in range(3):
    session.get(url1)
    time.sleep(0.15)
    session.get(url2)
    time.sleep(0.15)
print(f"requests.Session: {time.time() - start:.2f}s")
