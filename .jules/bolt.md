## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-04 - SEC Filing Parsing Bottleneck
**Learning:** `BeautifulSoup` is a major performance bottleneck when parsing massive (10s of MBs) HTML/XML SEC filings. Switching to native `lxml.html` functions yields a nearly 10x speedup in CPU-bound text extraction. However, beware that `tree.text_content()` merges text without spaces; use `' '.join(tree.itertext())` instead to preserve word boundaries.
**Action:** When extracting text from large SEC filings or comparable huge HTML files, always bypass `BeautifulSoup` and use native `lxml` tree parsing.
