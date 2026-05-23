## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - HTML Parsing and String Concatenation Bottlenecks
**Learning:** `BeautifulSoup` causes severe performance bottlenecks when parsing large SEC filings. Furthermore, using `+=` for string concatenation inside a loop to build large strings (like combining multiple SEC filings) adds significant overhead compared to appending to a list and joining. Benchmarks for ~1MB strings show ~50% performance gain for list join pattern.
**Action:** Use native `lxml` parsing (`lxml.html.fromstring`) with `lxml.etree.strip_elements` for faster HTML parsing of large documents. Use the `list.append()` and `str.join()` pattern instead of `+=` for building large strings.
## 2026-05-23 - Python Loop Bottleneck in Time Series Simulation
**Learning:** Python `for` loops act as severe performance bottlenecks when simulating lengthy time series (e.g., millions of days). Array operations shouldn't be iterated.
**Action:** Replace Python loops with vectorized NumPy operations. Specifically, use `np.cumprod` to calculate cumulative returns, followed by `np.maximum` to bound the results, yielding significant execution time reductions (e.g., dropping from 4.68s to 1.43s, or proportionally faster for smaller sizes).
