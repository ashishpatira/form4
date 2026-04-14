## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-14 - Native lxml for large SEC Filings
**Learning:** Using BeautifulSoup on top of lxml for parsing large SEC HTML/XML filings is a severe performance bottleneck due to BeautifulSoup creating its own heavy Python object tree.
**Action:** When extracting text from large SEC filings, bypass BeautifulSoup entirely and use native lxml (e.g. lxml.html.fromstring) along with itertext() to preserve space boundaries between adjacent tags.
