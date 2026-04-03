import os
import requests
import datetime
import xml.etree.ElementTree as ET
import time
import json
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from ratelimit import limits, sleep_and_retry
import threading

# SEC API configurations
SEC_USER_AGENT = "Form4Extractor/1.0 (contact@example.com)"
DAILY_INDEX_URL = "https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{quarter}/master.{date}.idx"
BASE_URL = "https://www.sec.gov/Archives/"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up requests session
session = requests.Session()
session.headers.update({"User-Agent": SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"})

# Enforce SEC rate limit: max 10 requests per second. Using 8 to be safe.
@sleep_and_retry
@limits(calls=8, period=1)
def fetch_url(url, is_text=True):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text if is_text else response.content
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def get_date_range(start_date_str=None, end_date_str=None):
    if start_date_str and end_date_str:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        delta = end_date - start_date
        return [end_date - datetime.timedelta(days=i) for i in range(delta.days + 1)]
    else:
        # Default to past week
        today = datetime.date.today()
        return [today - datetime.timedelta(days=i) for i in range(7)]

def get_quarter(date):
    return (date.month - 1) // 3 + 1

def fetch_company_tickers():
    """Fetches SEC company tickers to map Ticker -> CIK for filtering."""
    url = "https://www.sec.gov/files/company_tickers.json"
    logging.info(f"Fetching company tickers from {url}")
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Build mapping: ticker (upper) -> CIK (str)
        ticker_to_cik = {}
        for entry in data.values():
            ticker = entry.get('ticker', '').upper()
            cik_str = str(entry.get('cik_str'))
            if ticker and cik_str:
                ticker_to_cik[ticker] = cik_str
        return ticker_to_cik
    except Exception as e:
        logging.error(f"Failed to fetch company tickers: {e}")
        return {}

def get_form4_urls_for_date(date, allowed_ciks=None):
    date_str = date.strftime("%Y%m%d")
    year = date.year
    quarter = get_quarter(date)
    url = DAILY_INDEX_URL.format(year=year, quarter=quarter, date=date_str)

    logging.info(f"Fetching daily index for {date_str} from {url}")
    text = fetch_url(url)
    if not text:
        return []

    form4_urls = []
    # Index files have headers, the actual data usually starts after a line of dashes
    lines = text.split('\n')
    data_started = False
    for line in lines:
        if line.startswith('---'):
            data_started = True
            continue
        if data_started and line.strip():
            parts = line.split('|')
            if len(parts) >= 5:
                cik, company, form_type, date_filed, file_path = parts
                cik = cik.strip()
                if form_type.strip() == '4':
                    if allowed_ciks is not None and cik not in allowed_ciks:
                        continue
                    form4_urls.append(BASE_URL + file_path.strip())

    return form4_urls

import re

def extract_form4_data(xml_string):
    """Parses Form 4 XML and extracts matching transactions."""
    results = []
    try:
        # Strip XML namespaces using regex to avoid ElementTree namespace issues.
        # This removes xmlns="..." or xmlns:foo="..." from all tags.
        xml_string = re.sub(r'\s+xmlns(:\w+)?="[^"]+"', '', xml_string)

        root = ET.fromstring(xml_string)

        def get_text(element, path):
            node = element.find(path)
            return node.text.strip() if node is not None and node.text else None

        issuer_symbol = get_text(root, ".//issuerTradingSymbol")
        if not issuer_symbol:
            return results

        # Process Table 1 (nonDerivativeTable)
        for tx in root.findall(".//nonDerivativeTransaction"):
            # Check security title
            title = get_text(tx, ".//securityTitle/value")
            if not title or "common stock" not in title.lower():
                continue

            # Check transaction code
            tx_code = get_text(tx, ".//transactionCoding/transactionCode")
            if tx_code != "P":
                continue

            # Extract Date
            tx_date = get_text(tx, ".//transactionDate/value")

            # Extract Shares and Price
            shares_str = get_text(tx, ".//transactionAmounts/transactionShares/value")
            price_str = get_text(tx, ".//transactionAmounts/transactionPricePerShare/value")

            if not shares_str or not price_str:
                continue

            try:
                shares = float(shares_str)
                price = float(price_str)
            except ValueError:
                continue

            if price == 0:
                continue

            transaction_amount = shares * price

            # Extract Acquired/Disposed code (A or D)
            acq_disp_code = get_text(tx, ".//transactionAmounts/transactionAcquiredDisposedCode/value")
            tx_type = "Acquired" if acq_disp_code == "A" else ("Disposed" if acq_disp_code == "D" else None)

            # Extract Post-transaction shares
            updated_shares_str = get_text(tx, ".//postTransactionAmounts/sharesOwnedFollowingTransaction/value")
            post_tx_shares = float(updated_shares_str) if updated_shares_str else 0.0

            # Multiply Box 5 (shares owned following) by price inferred from Box 4
            updated_ownership_value = post_tx_shares * price

            # Calculate ratio of transaction_amount to the redefined updated_ownership_value
            transaction_ratio_pct = 0.0
            if updated_ownership_value > 0:
                transaction_ratio_pct = (transaction_amount / updated_ownership_value) * 100

            # Apply formatting requirements
            transaction_amount_rounded = round(transaction_amount)
            updated_ownership_value_rounded = round(updated_ownership_value)
            transaction_ratio_pct_rounded = round(transaction_ratio_pct, 1)

            results.append({
                "ticker": issuer_symbol,
                "transaction_date": tx_date,
                "transaction_amount": transaction_amount_rounded,
                "updated_ownership_value": updated_ownership_value_rounded,
                "type": tx_type,
                "transaction_ratio_pct": transaction_ratio_pct_rounded
            })

    except ET.ParseError as e:
        logging.debug(f"XML parse error: {e}")
    except Exception as e:
        logging.debug(f"Error extracting data: {e}")

    return results

def process_filing(url):
    """Fetches a Form 4 text file, extracts the XML part, and parses it."""
    text = fetch_url(url)
    if not text:
        return []

    # Extract XML block
    start_tag = "<XML>"
    end_tag = "</XML>"
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag)

    if start_idx == -1 or end_idx == -1:
        return []

    # extract the content after <XML> and before </XML>
    # Note: Sometimes there is an <XML> block for the PDF or other files.
    # A standard Form 4 has an <XML> block inside a <DOCUMENT> block with <TYPE>4 or <TYPE>XML

    # safer extraction: get all XML blocks and find the ownershipDocument
    xml_blocks = []
    curr_idx = 0
    while True:
        s_idx = text.find(start_tag, curr_idx)
        if s_idx == -1:
            break
        e_idx = text.find(end_tag, s_idx)
        if e_idx == -1:
            break

        xml_content = text[s_idx + len(start_tag):e_idx].strip()
        # Remove potential first line if it's an xml declaration that might cause issues, or check if it's ownershipDocument
        if "ownershipDocument" in xml_content:
             # Just in case the XML declaration is present but stripped, or multiple namespaces
             # Remove leading XML declaration if any issues
             if xml_content.startswith("<?xml"):
                 xml_content = xml_content.split("?>", 1)[1].strip()
             xml_blocks.append(xml_content)

        curr_idx = e_idx + len(end_tag)

    all_results = []
    for xml_data in xml_blocks:
        all_results.extend(extract_form4_data(xml_data))

    return all_results

def main():
    parser = argparse.ArgumentParser(description="Extract Form 4 Insider Trades")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", help="End date in YYYY-MM-DD format")
    parser.add_argument("--tickers", help="Comma-separated list of tickers to filter by (e.g., AAPL,MSFT)")
    args = parser.parse_args()

    dates = get_date_range(args.start_date, args.end_date)

    allowed_ciks = None
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
        ticker_to_cik = fetch_company_tickers()
        allowed_ciks = set()
        for t in tickers:
            if t in ticker_to_cik:
                # Need to match the CIK format in the idx file (sometimes it lacks leading zeros)
                # Int casting removes leading zeros, which matches the idx file format usually.
                allowed_ciks.add(str(int(ticker_to_cik[t])))
            else:
                logging.warning(f"Ticker {t} not found in SEC company tickers list.")

        logging.info(f"Filtering for CIKs: {allowed_ciks}")

    all_form4_urls = []

    # Step 1: Collect URLs for all Form 4s in the date range
    for date in dates:
        urls = get_form4_urls_for_date(date, allowed_ciks)
        all_form4_urls.extend(urls)

    logging.info(f"Found {len(all_form4_urls)} Form 4 filings in the past week.")

    # Step 2: Fetch and process filings concurrently
    all_extracted_data = []

    # Using a max_workers of 8 to stay well within SEC rate limits,
    # and using the rate-limited fetch_url.
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(process_filing, url): url for url in all_form4_urls}

        completed = 0
        total = len(future_to_url)
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                if data:
                    all_extracted_data.extend(data)
            except Exception as e:
                logging.error(f"Filing {url} generated an exception: {e}")

            completed += 1
            if completed % 100 == 0:
                logging.info(f"Processed {completed}/{total} filings...")

    # Step 3: Save to JSON
    output_file = os.path.join(os.path.dirname(__file__), "form4_trades_past_week.json")
    with open(output_file, 'w') as f:
        json.dump(all_extracted_data, f, indent=4)

    logging.info(f"Extraction complete. Found {len(all_extracted_data)} matching transactions.")
    logging.info(f"Saved results to {output_file}")

if __name__ == "__main__":
    main()
