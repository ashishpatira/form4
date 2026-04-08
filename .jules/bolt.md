## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2026-04-08 - Native LXML HTML Parsing vs BeautifulSoup
**Learning:** `BeautifulSoup` wrapped around `lxml` is significantly slower (up to 4x) than native `lxml.html` when parsing and extracting text from large SEC documents. Furthermore, when dropping tags in native `lxml.html`, `element.drop_tree()` is essential because it drops the tag but crucially preserves its `.tail` text, which holds adjacent text content, avoiding data loss.
**Action:** Always prefer `lxml.html.fromstring` over `BeautifulSoup(content, 'lxml')` for performance-critical parsing of large documents, and safely remove unwanted tags using `drop_tree()`.
