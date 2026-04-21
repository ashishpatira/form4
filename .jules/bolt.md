## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-17 - Efficient String Concatenation in extract_keywords.py
**Learning:** Using `"".join()` with a list of strings is significantly more efficient than using the `+=` operator in a loop for large strings (e.g., several MBs of SEC filing text).
**Action:** Use the list-append and join pattern whenever aggregating large amounts of text in a loop.
