## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2024-04-05 - Native lxml outperforms BeautifulSoup for SEC filings
**Learning:** Using `BeautifulSoup` to parse very large SEC HTML/XML filings introduces a severe performance bottleneck. Tests show native `lxml` (`lxml.html.fromstring`) is over 4x faster for ~1.5MB documents.
**Action:** When parsing large SEC HTML/XML filings, use native `lxml` instead of `BeautifulSoup` to prevent performance issues. When extracting text from `lxml` parsed HTML trees, use `' '.join(tree.itertext())` instead of `tree.text_content()` to ensure spaces are preserved between adjacent tags and prevent text concatenation regressions.
