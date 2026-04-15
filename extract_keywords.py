import argparse
import json
import logging
import os
import re
import time
from typing import List, Dict

import requests
import lxml.html
import lxml.etree
import pandas as pd
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SEC_USER_AGENT = "Sp500KeywordExtractor/1.0 (placeholder@example.com)"
SEC_RATE_LIMIT_DELAY = 0.15  # SEC allows 10 requests per second
SEC_REQUEST_TIMEOUT = 10  # Seconds
WIKIPEDIA_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

# Regex patterns
WHITESPACE_PATTERN = re.compile(r'\s+')

# Initialize a global session for connection pooling
# This significantly improves performance when making multiple requests to the SEC
sec_session = requests.Session()
sec_session.headers.update({"User-Agent": SEC_USER_AGENT})

# We use a large context model
model = genai.GenerativeModel('gemini-3.0-flash')

def fetch_sp500_tickers() -> List[str]:
    """Fetches the list of S&P 500 tickers from Wikipedia."""
    logger.info("Fetching S&P 500 list from Wikipedia...")
    try:
        # Provide a User-Agent to avoid Wikipedia returning 403 Forbidden
        storage_options = {'User-Agent': 'Mozilla/5.0'}
        tables = pd.read_html(WIKIPEDIA_SP500_URL, storage_options=storage_options)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Wikipedia sometimes uses dots for tickers like BRK.B, but SEC might expect BRK-B or BRK
        tickers = [t.replace('.', '-') for t in tickers]
        logger.info(f"Successfully fetched {len(tickers)} tickers.")
        return tickers
    except Exception as e:
        logger.error(f"Error fetching S&P 500 tickers: {e}")
        return []

def get_sec_ticker_to_cik_mapping() -> Dict[str, str]:
    """Fetches the SEC mapping of tickers to CIKs."""
    logger.info("Fetching SEC ticker to CIK mapping...")
    try:
        response = sec_session.get(SEC_TICKERS_URL, timeout=SEC_REQUEST_TIMEOUT)
        response.raise_for_status()
        time.sleep(SEC_RATE_LIMIT_DELAY)

        data = response.json()
        mapping = {}
        for entry in data.values():
            ticker = entry['ticker']
            cik = str(entry['cik_str']).zfill(10)  # CIKs must be 10 digits
            mapping[ticker] = cik
        logger.info(f"Successfully fetched mapping for {len(mapping)} tickers.")
        return mapping
    except Exception as e:
        logger.error(f"Error fetching SEC ticker mapping: {e}")
        return {}

def fetch_recent_filings(cik: str) -> List[Dict]:
    """Fetches the metadata for the most recent 10-K and up to 3 10-Qs for a given CIK."""
    logger.info(f"Fetching filing history for CIK {cik}...")
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"

    try:
        response = sec_session.get(submissions_url, timeout=SEC_REQUEST_TIMEOUT)
        response.raise_for_status()
        time.sleep(SEC_RATE_LIMIT_DELAY)

        data = response.json()
        recent_filings = data.get('filings', {}).get('recent', {})

        if not recent_filings:
            logger.warning(f"No recent filings found for CIK {cik}.")
            return []

        forms = recent_filings.get('form', [])
        accession_numbers = recent_filings.get('accessionNumber', [])
        primary_documents = recent_filings.get('primaryDocument', [])

        target_filings = []
        found_10k = False
        found_10q_count = 0

        for i in range(len(forms)):
            form = forms[i]

            # Identify 10-K and 10-Q
            if form == '10-K' and not found_10k:
                target_filings.append({
                    'form': form,
                    'accession_number': accession_numbers[i].replace('-', ''),
                    'primary_document': primary_documents[i]
                })
                found_10k = True
            elif form == '10-Q' and found_10q_count < 3:
                target_filings.append({
                    'form': form,
                    'accession_number': accession_numbers[i].replace('-', ''),
                    'primary_document': primary_documents[i]
                })
                found_10q_count += 1

            if found_10k and found_10q_count == 3:
                break

        logger.info(f"Found {len(target_filings)} target filings for CIK {cik} (10-K: {found_10k}, 10-Qs: {found_10q_count}).")
        return target_filings

    except Exception as e:
        logger.error(f"Error fetching filings for CIK {cik}: {e}")
        return []

def download_and_parse_filing(cik: str, filing_info: Dict) -> str:
    """Downloads a filing and extracts plain text from the HTML/XML."""
    accession_no = filing_info['accession_number']
    doc_name = filing_info['primary_document']

    url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession_no}/{doc_name}"
    logger.info(f"Downloading {filing_info['form']} from {url}...")

    try:
        response = sec_session.get(url, timeout=SEC_REQUEST_TIMEOUT)
        response.raise_for_status()
        time.sleep(SEC_RATE_LIMIT_DELAY)

        # Parse HTML/XML and extract text using native lxml for performance
        tree = lxml.html.fromstring(response.content)
        # Remove script and style elements safely while preserving .tail text
        lxml.etree.strip_elements(tree, 'script', 'style', with_tail=False)

        text = ' '.join(tree.itertext())
        # Collapse multiple spaces
        text = WHITESPACE_PATTERN.sub(' ', text)

        logger.info(f"Successfully downloaded and extracted {len(text)} characters.")
        return text
    except Exception as e:
        logger.error(f"Error downloading/parsing filing from {url}: {e}")
        return ""

def extract_keywords_with_gemini(ticker: str, all_text: str) -> List[str]:
    """Uses Gemini to extract 10 unique business keywords from the provided text."""
    logger.info(f"Sending text to Gemini for ticker {ticker}...")

    prompt = f"""
    You are an expert financial analyst. I am providing you with the text from recent SEC public filings (10-K and 10-Q) for the company with ticker '{ticker}'.

    Based ONLY on this text, identify exactly 10 unique business keywords that represent important factors affecting this business.
    These keywords should be specific business terms (e.g., "AI", "defense", "staples", "datacenter", "cloud computing", "semiconductors").

    Please provide ONLY a JSON list of strings containing exactly 10 keywords. Do not provide any other text, explanation, or markdown formatting outside of the JSON array.

    Text:
    {all_text}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        # Parse the JSON response
        response_text = response.text.strip()
        # Clean up possible markdown codeblocks
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        keywords = json.loads(response_text.strip())
        if isinstance(keywords, list):
            return keywords
        else:
            logger.warning(f"Unexpected response format from Gemini: {response_text}")
            return []

    except Exception as e:
        logger.error(f"Error calling Gemini for {ticker}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Extract business keywords from S&P 500 SEC filings.")
    parser.add_argument("--batch", type=int, required=True, help="Batch number to process (1-based index). Each batch is 25 companies.")
    parser.add_argument("--batch-size", type=int, default=25, help="Number of companies per batch (default: 25).")
    parser.add_argument("--test", action="store_true", help="Run in test mode (only processes the first company in the batch).")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("Please set the GEMINI_API_KEY environment variable.")
        return

    genai.configure(api_key=api_key)

    tickers = fetch_sp500_tickers()
    if not tickers:
        logger.error("Failed to fetch tickers. Exiting.")
        return

    ticker_to_cik = get_sec_ticker_to_cik_mapping()
    if not ticker_to_cik:
        logger.error("Failed to fetch SEC ticker mapping. Exiting.")
        return

    # Calculate batch indices
    start_idx = (args.batch - 1) * args.batch_size
    end_idx = start_idx + args.batch_size

    batch_tickers = tickers[start_idx:end_idx]

    if not batch_tickers:
        logger.warning(f"No tickers found for batch {args.batch}. Max batch is likely {len(tickers) // args.batch_size + 1}.")
        return

    if args.test:
        logger.info("Running in TEST mode. Only processing the first ticker.")
        batch_tickers = batch_tickers[:1]

    logger.info(f"Processing batch {args.batch} with {len(batch_tickers)} tickers: {batch_tickers}")

    results = {}

    for ticker in batch_tickers:
        logger.info(f"\n--- Processing {ticker} ---")
        cik = ticker_to_cik.get(ticker)

        if not cik:
            logger.warning(f"No CIK found for ticker {ticker}. Skipping.")
            continue

        filings = fetch_recent_filings(cik)
        if not filings:
            logger.warning(f"No suitable filings found for {ticker}. Skipping.")
            continue

        all_text = ""
        for filing in filings:
            text = download_and_parse_filing(cik, filing)
            all_text += text + "\n\n"

        if not all_text.strip():
            logger.warning(f"No text extracted for {ticker}. Skipping.")
            continue

        if len(all_text) > 3000000:
            logger.info(f"Truncating text for {ticker} from {len(all_text)} to 3000000 characters.")
            all_text = all_text[:3000000]

        keywords = extract_keywords_with_gemini(ticker, all_text)

        if keywords:
            logger.info(f"Extracted keywords for {ticker}: {keywords}")
            results[ticker] = keywords
        else:
            logger.warning(f"Failed to extract keywords for {ticker}.")

    # Save results
    output_filename = f"sp500_keywords_batch_{args.batch}.json"
    with open(output_filename, 'w') as f:
        json.dump(results, f, indent=4)

    logger.info(f"Finished processing batch {args.batch}. Results saved to {output_filename}.")

if __name__ == "__main__":
    main()
