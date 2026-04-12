## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2026-04-03 - HTML Parsing Performance Bottleneck
**Learning:** When parsing large HTML/XML files (like SEC filings) to extract plain text, using `BeautifulSoup` with the `'lxml'` parser incurs a severe performance overhead due to its intermediate object representation. Benchmarks show native `lxml.html` is ~6x faster.
**Action:** When extracting text from large documents, use native `lxml` (`lxml.html.fromstring`) instead of `BeautifulSoup` to prevent severe performance bottlenecks. For element removal, use `.drop_tree()` and for text extraction use `' '.join(tree.itertext())` to safely handle tail text.
