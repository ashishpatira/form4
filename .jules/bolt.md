## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.

## 2026-04-15 - lxml tail loss
**Learning:** In `lxml`'s tree structure, the text immediately following an element is stored in that element's `.tail` attribute. By calling `element.drop_tree()` on elements, the script inadvertently deletes the `.tail` text alongside the element, causing data loss.
**Action:** When removing elements safely without data loss, use `lxml.etree.strip_elements(tree, 'tag1', 'tag2', with_tail=False)`.
