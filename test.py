from email.quoprimime import unquote


raw_url1 = "https://evoke.ics.uci.edu/health-data-exploration-report-published/#comment-75669"
raw_url2 = "https://evoke.ics.uci.edu/health-data-exploration-report-published/#comment-75669#wtf#gg"


unique_url = raw_url1.split('#',1)[0]

print(unique_url)

test_set = set()
test_set.add("hello")
print(test_set)