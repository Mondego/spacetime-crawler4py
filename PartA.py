import sys
import re
from collections import defaultdict


# O(N) since it only iterate the whole file one time
def tokenize(TextFilePath):
    all_word = []
    # focus on a-z A-Z 0-9
    try:
        file = open(TextFilePath, 'r+')
        for line in file:
            line = re.sub(r'[^A-Z^a-z^0-9^ ]', ' ', line.strip().lower())
            for i in line.split():
                all_word.append(i)
    except IOError:
        print("Error, can't find file.")
    else:
        file.close()
    return all_word

# O(N) only 1 single for loop
def computeWordFrequencies(Token):
    Freq = defaultdict(int)
    for i in Token:
        Freq[i] += 1
    return Freq


# O(NlogN) since there is 1 for loop and 1 sorted which sorted is bigger.
def Frequence(Token):
    dict_sort = sorted(Token.items(), key=lambda x: -x[1])
    for i in dict_sort:
        print(i[0], " = ", i[1])


if __name__ == '__main__':
    TextFilePath = sys.argv[1]
    Frequence(computeWordFrequencies(tokenize(TextFilePath)))



