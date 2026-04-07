## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-07 - lxml drop_tree tail text behavior
**Learning:** `lxml`'s `element.drop_tree()` method natively preserves `.tail` text (moving it to the preceding sibling or parent text). Manually trying to preserve the tail text before calling `drop_tree()` leads to text duplication and data corruption.
**Action:** When removing tags from an `lxml` tree where tail text needs to be preserved, simply call `element.drop_tree()`. Do not manually reassign `element.tail`.
