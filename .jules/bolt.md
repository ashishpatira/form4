## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - Native HTML Parsing with lxml
**Learning:** Parsing large SEC HTML/XML filings is a severe performance bottleneck when using BeautifulSoup. Using `lxml.html.fromstring` directly provides significant native speed benefits and reduces execution time drastically. Furthermore, using `element.drop_tree()` appropriately manages the `.tail` texts during tag removal, and `tree.itertext()` avoids text concatenation regressions that `tree.text_content()` suffers from.
**Action:** Default to `lxml.html` or `lxml.etree` natively for parsing large documents, bypassing abstractions like `BeautifulSoup` when speed is a primary concern.
