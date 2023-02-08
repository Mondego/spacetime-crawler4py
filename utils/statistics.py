
def write_statistics(pages):
    with open('statistics.txt', 'w+') as f:
        f.write('Number of unique pages: ' + str(len(pages)))