## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - HTML Parsing and String Concatenation Performance
**Learning:** `BeautifulSoup` parsing of multi-megabyte SEC HTML filings introduces a severe bottleneck. Furthermore, loop-based string concatenation (`+=`) becomes extremely slow for large texts.
**Action:** Always use native `lxml.html` and `lxml.etree` combined with `itertext()` for large document extraction, and build large strings by appending to a list and calling `''.join()` at the end.
