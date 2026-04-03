# S&P 500 SEC Filing Keyword Extractor

This project is a Python tool that extracts business keywords from SEC public filings (10-K and 10-Q) for S&P 500 companies using the Gemini model (`google-generativeai`).

## Features
- Fetches the current list of S&P 500 tickers.
- Retrieves SEC ticker-to-CIK mapping.
- Downloads the most recent 10-K and up to three 10-Qs for a given company.
- Extracts plain text from the HTML/XML filings.
- Uses Gemini (specifically the `gemini-1.5-flash` model) to identify exactly 10 unique business keywords that represent important factors affecting the business.
- Outputs the result in JSON format.

## Prerequisites
- Python 3.7+
- A Google Gemini API Key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Copy the example environment file and add your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and set the `GEMINI_API_KEY`:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Usage

The script is designed to run in batches due to SEC rate limits and processing time.

```bash
python extract_keywords.py --batch <BATCH_NUMBER> [OPTIONS]
```

### Command-line Arguments

- `--batch` (required): Batch number to process (1-based index). Each batch defaults to 25 companies.
- `--batch-size` (optional): Number of companies per batch (default: 25).
- `--test` (optional): Run in test mode, which only processes the first company in the selected batch.

### Examples

Process the first batch of 25 companies:
```bash
python extract_keywords.py --batch 1
```

Run a test on the first company of the first batch:
```bash
python extract_keywords.py --batch 1 --test
```

Process the 5th batch with a custom batch size of 10:
```bash
python extract_keywords.py --batch 5 --batch-size 10
```

## Output

The script outputs a JSON file for each batch containing a dictionary mapping company tickers to their extracted keywords.
The file will be named `sp500_keywords_batch_<BATCH_NUMBER>.json`.

Example output format:
```json
{
    "AAPL": [
        "smartphones",
        "personal computers",
        "tablets",
        "wearables",
        "digital content",
        "cloud services",
        "software",
        "semiconductors",
        "supply chain",
        "retail"
    ]
}
```
