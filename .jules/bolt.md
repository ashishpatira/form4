## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2026-04-11 - SEC Filing Parsing Bottleneck
**Learning:** Parsing massive SEC EDGAR filings (e.g., 10-K, 10-Q) using `BeautifulSoup` introduces a severe performance bottleneck because of its Python-based DOM construction overhead.
**Action:** Always use native `lxml.html.fromstring` directly for processing massive XML/HTML strings, taking advantage of its underlying C-based performance while securely stripping unneeded elements via xpath (`tree.xpath`) and removing them with `element.drop_tree()`.
