import time
from bs4 import BeautifulSoup
import lxml.html
import requests

# Download a sample SEC filing
url = "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm"
headers = {"User-Agent": "Sp500KeywordExtractor/1.0 (placeholder@example.com)"}
response = requests.get(url, headers=headers)
html_content = response.content

print(f"Downloaded {len(html_content)} bytes")

# BeautifulSoup parsing
start_bs = time.time()
soup = BeautifulSoup(html_content, 'lxml')
for script in soup(['script', 'style']):
    script.decompose()
text_bs = soup.get_text(separator=' ', strip=True)
bs_time = time.time() - start_bs
print(f"BeautifulSoup time: {bs_time:.4f}s, length: {len(text_bs)}")

# Native lxml parsing
start_lxml = time.time()
tree = lxml.html.fromstring(html_content)
for element in tree.xpath('//script | //style'):
    # Preserve tail text
    tail = element.tail
    if tail:
        prev = element.getprevious()
        if prev is not None:
            prev.tail = (prev.tail or '') + tail
        else:
            parent = element.getparent()
            if parent is not None:
                parent.text = (parent.text or '') + tail
    element.drop_tree()

text_lxml = ' '.join(tree.itertext())
text_lxml = ' '.join(text_lxml.split()) # to match the output of BS strip=True and separator=' ' behavior
lxml_time = time.time() - start_lxml
print(f"lxml time: {lxml_time:.4f}s, length: {len(text_lxml)}")

print(f"Speedup: {bs_time / lxml_time:.2f}x")
