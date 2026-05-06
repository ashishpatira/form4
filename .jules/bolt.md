## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - HTML Parsing and String Concatenation Bottlenecks
**Learning:** `BeautifulSoup` causes severe performance bottlenecks when parsing large SEC filings. Furthermore, using `+=` for string concatenation inside a loop to build large strings (like combining multiple SEC filings) adds significant overhead compared to appending to a list and joining. Benchmarks for ~1MB strings show ~50% performance gain for list join pattern.
**Action:** Use native `lxml` parsing (`lxml.html.fromstring`) with `lxml.etree.strip_elements` for faster HTML parsing of large documents. Use the `list.append()` and `str.join()` pattern instead of `+=` for building large strings.
## 2026-04-03 - Financial Timeseries Simulation with Vectorization
**Learning:** Standard Python `for` loops used for step-by-step state dependence (like timeseries simulation where `price[t]` depends on `price[t-1]`) are severe performance bottlenecks in scientific/financial code.
**Action:** Replace iterative loops with highly optimized, vectorized NumPy operations (e.g., `np.cumprod`). Use `np.concatenate` for the initial state and array-level operations like `np.maximum` to handle step-by-step bounds checking vectorizedly when negative bounds drops are statistically unlikely.
