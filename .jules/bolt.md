## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2026-04-16 - Parsing large SEC HTML/XML filings
**Learning:** When parsing large SEC HTML/XML filings, using `BeautifulSoup` introduces severe performance bottlenecks.
**Action:** Use native `lxml` (e.g., `lxml.html.fromstring`) instead of `BeautifulSoup` to parse large HTML/XML filings, which is significantly faster. Remove elements like `<script>` or `<style>` with `lxml.etree.strip_elements(tree, 'script', 'style', with_tail=False)` to prevent dropping `.tail` text. Use `' '.join(tree.itertext())` instead of `tree.text_content()` to ensure spaces are preserved between adjacent tags.
