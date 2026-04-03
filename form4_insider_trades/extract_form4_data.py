import os
import requests
import datetime
import xml.etree.ElementTree as ET
import time
import json
import logging
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

def get_past_week_dates():
    today = datetime.date.today()
    return [today - datetime.timedelta(days=i) for i in range(7)]

def get_quarter(date):
    return (date.month - 1) // 3 + 1

def get_form4_urls_for_date(date):
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
                if form_type.strip() == '4':
                    form4_urls.append(BASE_URL + file_path.strip())

    return form4_urls

def extract_form4_data(xml_string):
    """Parses Form 4 XML and extracts matching transactions."""
    results = []
    try:
        root = ET.fromstring(xml_string)

        # XML namespace handling is tricky. EDGAR forms usually don't have default NS, but just in case
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

            # Extract Post-transaction shares
            updated_shares_str = get_text(tx, ".//postTransactionAmounts/sharesOwnedFollowingTransaction/value")
            updated_ownership_value = float(updated_shares_str) if updated_shares_str else 0.0

            results.append({
                "ticker": issuer_symbol,
                "transaction_date": tx_date,
                "transaction_amount": transaction_amount,
                "updated_ownership_value": updated_ownership_value
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
    dates = get_past_week_dates()
    all_form4_urls = []

    # Step 1: Collect URLs for all Form 4s in the past week
    for date in dates:
        urls = get_form4_urls_for_date(date)
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
