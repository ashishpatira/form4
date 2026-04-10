## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2026-04-03 - Native lxml Performance over BeautifulSoup
**Learning:** For extremely large SEC filings (10-Ks, 10-Qs) parsed directly as HTML/XML, `BeautifulSoup` adds a massive abstraction layer overhead resulting in ~6x slower processing times compared to using native `lxml` directly, becoming a significant CPU bottleneck.
**Action:** When extracting bulk text from very large HTML/XML files where advanced DOM traversal isn't strictly necessary, parse and manipulate the tree using native `lxml.html.fromstring` and `.drop_tree()` rather than `BeautifulSoup`.
