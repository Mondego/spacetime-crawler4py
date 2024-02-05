from bs4 import BeautifulSoup

# Example HTML content with hyperlinks
html_content = """
<html>
<body>
    <p>Some text with a <a href="https://example.com">link</a>.</p>
    <ul>
        <li><a href="https://example.com/page1">Page 1</a></li>
        <li><a href="https://example.com/page2">Page 2</a></li>
        <li><a href="https://example.com/page3">Page 3</a></li>
    </ul>
</body>
</html>
"""

# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Find all hyperlinks (a tags)
hyperlinks = soup.find_all('a')

# Extract and print the href attribute from each hyperlink
for link in hyperlinks:
    href = link.get('href')
    if href has the filter rule then add it to the set 
