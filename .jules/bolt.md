## 2026-04-03 - SEC Request Connection Pooling
**Learning:** Sequential, independent requests to `sec.gov` domains suffer significant overhead from TLS handshakes when executed outside of a persistent session, particularly during batch processing tasks like SEC filing downloads.
**Action:** Always utilize a `requests.Session()` object when making multiple HTTP calls to the same host/API domain to enable connection pooling, thus minimizing connection setup latency.
## 2026-04-03 - HTML Parsing and String Concatenation Bottlenecks
**Learning:** `BeautifulSoup` causes severe performance bottlenecks when parsing large SEC filings. Furthermore, using `+=` for string concatenation inside a loop to build large strings (like combining multiple SEC filings) adds significant overhead compared to appending to a list and joining. Benchmarks for ~1MB strings show ~50% performance gain for list join pattern.
**Action:** Use native `lxml` parsing (`lxml.html.fromstring`) with `lxml.etree.strip_elements` for faster HTML parsing of large documents. Use the `list.append()` and `str.join()` pattern instead of `+=` for building large strings.
## 2026-04-03 - Vectorization Absorbing Bound Gotcha
**Learning:** When vectorizing timeseries simulation loops that enforce absorbing bounds (like flooring prices to 0 upon bankruptcy), using a final `np.maximum` after `np.cumprod` introduces a mathematical regression because the internal cumulative products can underflow/overflow unpredictably.
**Action:** Identify the first boundary breach (e.g., `is_negative = multipliers <= 0`) and explicitly zero out all subsequent multipliers *before* running `np.cumprod` to ensure correctness.

## 2026-04-03 - Do not overwrite existing files with temporary scripts
**Learning:** Carelessly naming benchmark scripts `benchmark.py` in the root directory can overwrite an existing repository file, leading to accidental deletion in the patch.
**Action:** Always check `git status` to ensure you aren't overwriting tracked files, and prefer explicitly temporary filenames like `tmp_benchmark_sim.py`.
