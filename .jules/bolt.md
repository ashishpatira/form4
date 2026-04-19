## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2024-05-15 - BeautifulSoup Severe Bottleneck on SEC Filings
**Learning:** Using BeautifulSoup with 'lxml' parser for large SEC HTML/XML filings causes severe performance bottlenecks due to unnecessary overhead.
**Action:** Always use native `lxml` (e.g., `lxml.html.fromstring`) instead of `BeautifulSoup` when parsing large SEC filings to significantly improve extraction speed.
