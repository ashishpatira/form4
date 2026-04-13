import time
from bs4 import BeautifulSoup
import lxml.html
import re

html_content = b"<html><body>" + b"<div>hello <script>alert()</script> world</div>" * 10000 + b"</body></html>"
WHITESPACE_PATTERN = re.compile(r'\s+')

# BS4
start = time.time()
soup = BeautifulSoup(html_content, 'lxml')
for script in soup(['script', 'style']):
    script.decompose()
text = soup.get_text(separator=' ', strip=True)
text = WHITESPACE_PATTERN.sub(' ', text)
print(f"BS4: {time.time() - start:.4f}s")

# LXML
start = time.time()
tree = lxml.html.fromstring(html_content)
for element in tree.xpath('//script | //style'):
    element.drop_tree()
text = ' '.join(tree.itertext())
text = WHITESPACE_PATTERN.sub(' ', text).strip()
print(f"LXML: {time.time() - start:.4f}s")
