## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2026-04-06 - SEC Filing HTML Parsing Bottleneck
**Learning:** `BeautifulSoup` introduces severe performance bottlenecks (approx. 6x slower) when parsing large SEC HTML/XML filings. However, simply using `element.getparent().remove(element)` or `element.drop_tree()` in `lxml.html` causes data loss by removing the `.tail` text of the element.
**Action:** Use native `lxml.html` (`lxml.html.fromstring`) instead of `BeautifulSoup` for large documents to drastically improve parsing speed. When removing elements, manually preserve the `.tail` text by reassigning it to the previous sibling's tail or the parent's text before removing the node, and extract text using `' '.join(tree.itertext())`.
