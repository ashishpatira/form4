## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - HTML Parsing and String Concatenation Bottlenecks
**Learning:** `BeautifulSoup` causes severe performance bottlenecks when parsing large SEC filings. Furthermore, using `+=` for string concatenation inside a loop to build large strings (like combining multiple SEC filings) adds significant overhead compared to appending to a list and joining. Benchmarks for ~1MB strings show ~50% performance gain for list join pattern.
**Action:** Use native `lxml` parsing (`lxml.html.fromstring`) with `lxml.etree.strip_elements` for faster HTML parsing of large documents. Use the `list.append()` and `str.join()` pattern instead of `+=` for building large strings.
## 2026-06-25 - Vectorized Time Series Generation is Essential
**Learning:** Using a `for` loop to iteratively compute daily prices in time series simulations (like Brownian motion) acts as a severe performance bottleneck. Generating prices vectorially requires replacing standard loops with NumPy array operations.
**Action:** Always utilize `np.cumprod` on a pre-generated array of daily multipliers instead of iteratively updating the price at each step in time series simulations. Furthermore, appending `np.maximum(array, 0)` avoids inefficient step-by-step conditional checks for non-negative bounding.
