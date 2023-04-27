from maxWordCount import *
from ics_subdomains import icsSubdomains

report = open("reports.txt", "w")
report.write("2. The maximum number of words overall the webpages crawled is:", maxWordCount.maxWords, "\n")
report.write("\n")
report.write("""4. Here is a list of all the subdomains found in the ics.uci.edu domain in alphabetical order, 
             along with the number of unique pages detected in each subdomain:\n""")
for key, value in icsSubdomains.subdomainDict.items():
    report.write(key, value + "\n")
report.close()
