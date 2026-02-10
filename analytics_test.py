from analytics import record_page, write_report_files
from urllib.parse import urldefrag

# Page 1 HTML: has links with http/https variants + fragments
html1 = b"""
<html><body>
<h1>Page One</h1>
<p>""" + b"word " * 60 + b"""</p>

<a href="http://www.ics.uci.edu/about#section1">About (http + #section1)</a>
<a href="http://www.ics.uci.edu/about#section2">About (http + #section2)</a>
<a href="https://www.ics.uci.edu/about#section1">About (https + #section1)</a>
<a href="https://www.ics.uci.edu/about/">About (https trailing slash)</a>

<a href="https://www.ics.uci.edu/people">People</a>
<a href="https://www.ics.uci.edu/people#faculty">People (fragment)</a>

</body></html>
"""

# Page 2 HTML: same content idea, plus more words so it passes
html2 = b"""
<html><body>
<h1>Page Two</h1>
<p>""" + b"test " * 60 + b"""</p>

<a href="https://www.ics.uci.edu/about">About (https no slash)</a>
<a href="http://www.ics.uci.edu/about">About (http no fragment)</a>

</body></html>
"""

# Simulate the crawler visiting multiple pages.
# NOTE: record_page doesn't extract links; scraper does that.
# Here we only test URL uniqueness + defrag behavior.
urls_to_record = [
    "https://www.ics.uci.edu/index.html#top",      # fragment version
    "https://www.ics.uci.edu/index.html#bottom",   # same after defrag
    "http://www.ics.uci.edu/index.html#top",       # different scheme => should count separately
    "https://www.ics.uci.edu/index.html",          # same as https defrag
    "https://www.ics.uci.edu/index.html/",         # trailing slash => different unless you normalize it
]

# Record Page 1 under the first URL
record_page(urls_to_record[0], html1)

# Record Page 2 under another URL
record_page("https://www.ics.uci.edu/another.html#frag", html2)

# Record the rest as "visited" too (simulate more fetches)
for u in urls_to_record[1:]:
    record_page(u, html1)

# Force-write files now (don’t rely on atexit)
write_report_files()

print("Done. Check visited_urls.txt and report_unique_count.txt")
print("Expectation:")
print(" - https index.html counted once (fragments collapse)")
print(" - http index.html counted separately from https")
print(" - trailing slash may be counted separately unless you normalize it")
