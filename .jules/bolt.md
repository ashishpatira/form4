## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - HTML Parsing and String Concatenation Bottlenecks
**Learning:** `BeautifulSoup` causes severe performance bottlenecks when parsing large SEC filings. Furthermore, using `+=` for string concatenation inside a loop to build large strings (like combining multiple SEC filings) adds significant overhead compared to appending to a list and joining. Benchmarks for ~1MB strings show ~50% performance gain for list join pattern.
**Action:** Use native `lxml` parsing (`lxml.html.fromstring`) with `lxml.etree.strip_elements` for faster HTML parsing of large documents. Use the `list.append()` and `str.join()` pattern instead of `+=` for building large strings.
## 2026-04-03 - Vectorize Python Loops for NumPy Arrays
**Learning:** Standard Python `for` loops used for step-by-step array generation (like time series simulations) are severe performance bottlenecks compared to optimized C-level operations.
**Action:** Always replace Python iterative loops acting on numerical arrays with vectorized NumPy operations. Specifically, for cumulative multiplications like asset price paths, use `np.cumprod`, and for step-by-step flooring (e.g. `if price < 0: price = 0`), apply a final `np.maximum(prices, 0)` on the resulting array to achieve massive speedups (~22x) while maintaining functional parity.
