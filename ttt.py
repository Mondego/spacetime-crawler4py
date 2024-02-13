from urllib.parse import urlparse
x = set()
subdomains = {"www": (url , 3), "sch": (url , 3), "mwh": (url , 3),}

# rl = "https://redmiles.ics.uci.edu/people"
# parsed_url = urlparse(rl).netloc
# y = parsed_url.split('.')[0]
# # x.add(parsed_url.scheme + '://' + parsed_url.netloc)
# print(y)
subdomains["ics"].add(1)
subdomains["ics"].add(2)
subdomains["ics"].add(3)
print(len(subdomains["ics"]))
# x = (parsed_url.netloc.split('.'))

# if x[0] not in subdomains[x[1]]:
#             subdomains[x[1]].add(x[0])

# rl = "https://redsdmiles.ics.uci.edu/peopewlkffle"
# parsed_url = urlparse(rl)
# x = (parsed_url.netloc.split('.'))

# if x[0] not in subdomains[x[1]]:
#             subdomains[x[1]].add(x[0])

# print(subdomains)