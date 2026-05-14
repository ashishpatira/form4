## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - HTML Parsing and String Concatenation Bottlenecks
**Learning:** `BeautifulSoup` causes severe performance bottlenecks when parsing large SEC filings. Furthermore, using `+=` for string concatenation inside a loop to build large strings (like combining multiple SEC filings) adds significant overhead compared to appending to a list and joining. Benchmarks for ~1MB strings show ~50% performance gain for list join pattern.
**Action:** Use native `lxml` parsing (`lxml.html.fromstring`) with `lxml.etree.strip_elements` for faster HTML parsing of large documents. Use the `list.append()` and `str.join()` pattern instead of `+=` for building large strings.

## 2026-05-14 - Isolate Optimizations from Pre-existing Test Bugs
**Learning:** Even if a test suite has pre-existing issues (e.g. broken import paths causing module not found errors), I should not bundle those fixes in the same commit/PR if my primary task is performance optimization. Reviewers expect hyper-focused PRs for performance.
**Action:** Before running tests to verify my optimization, I should ensure I can run them successfully. If they fail due to unrelated issues, I should either isolate my testing (e.g., test only my function locally in a separate script) or address the test bug in a completely separate change, but I must only commit and submit the specific performance code changes.
