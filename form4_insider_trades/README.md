# SEC Form 4 Insider Trades Extractor

This tool efficiently downloads and extracts specific insider trading information from SEC Form 4 filings. It focuses on identifying **Open Market or Private Purchases** (Transaction Code `P`) of **Common Stock**.

## Features

- **Efficient Fetching:** Uses the SEC's daily EDGAR index to locate Form 4 documents quickly.
- **Concurrent Processing:** Employs thread pooling to download and parse multiple documents simultaneously while strictly adhering to SEC API rate limits (max 10 requests/second).
- **Targeted Extraction:** Parses the internal `<XML>` structures of the filings to extract Table 1 ("nonDerivativeTransaction") details, specifically focusing on Common Stock and Code "P" transactions.
- **Custom Metrics:** Calculates specialized metrics like `transaction_amount`, `updated_ownership_value` (using transaction price to estimate value), and `transaction_ratio_pct`.
- **Filtering:** Optionally filter filings by specific stock tickers and custom date ranges.

## Installation

Ensure you have Python 3.x installed. Install the necessary dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Usage

By default, running the script without arguments will extract matching transactions for all companies over the **past 7 days**.

```bash
python extract_form4_data.py
```

### Command-Line Arguments

The script supports the following optional arguments to filter the data:

- `--start-date`: The start date of the reporting period (Format: `YYYY-MM-DD`).
- `--end-date`: The end date of the reporting period (Format: `YYYY-MM-DD`).
- `--tickers`: A comma-separated list of stock tickers to filter by (e.g., `AAPL,MSFT,TSLA`).

### Examples

**1. Filter by specific tickers for the past week:**
```bash
python extract_form4_data.py --tickers TPL,FGBI
```

**2. Filter by a specific date range:**
```bash
python extract_form4_data.py --start-date 2024-01-01 --end-date 2024-01-15
```

**3. Combine date range and specific tickers:**
```bash
python extract_form4_data.py --start-date 2024-01-01 --end-date 2024-01-15 --tickers AAPL,MSFT
```

## Output Output

The script outputs the extracted data to a JSON file named `form4_trades_past_week.json` in the same directory. The file will contain a list of transactions with the following fields:

- `ticker`: The company's stock ticker symbol.
- `transaction_date`: The date the transaction occurred.
- `type`: Whether the transaction was "Acquired" or "Disposed".
- `transaction_amount`: The total dollar amount of the transaction (Shares Transacted × Price Per Share).
- `updated_ownership_value`: The estimated dollar value of the insider's total remaining shares after the transaction (Shares Owned Following Transaction × Price Per Share).
- `transaction_ratio_pct`: The percentage ratio of the `transaction_amount` to the `updated_ownership_value`.
