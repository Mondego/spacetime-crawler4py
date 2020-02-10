import re

'''part A Word Frequencies'''

'''
The run time complexity will be O(n**2).
The first for loop is O(n), and the splits in the while loop are O(n) .
The second for loop is O(n).
The run time complexity = O(n)*O(n) + O(n) = O(n**2)
'''


def tokenize(filename: str) -> list:
    try:
        f = open(filename, "r")
        array = f.read().split()
        f.close()

        array1 = []
        for word in array:
            if re.match(r"\w+\W+\w+", word):
                array1.extend(re.split(r"\W+", word))
            elif re.match(r"^\W+$", word):
                pass
            elif re.match(r"^\w+\W+$", word):
                array1.append(re.search(r"^(\w+)(\W+)$", word).group(1))
            elif re.match(r"\w*[^a-zA-Z0-9]+\w*[^a-zA-Z0-9]*", word):
                array1.extend(re.split(r"[^a-zA-Z0-9]+", word))
            else:
                array1.append(word)

        for i in range(len(array1)):
            if array1[i].lower() != array1[i]:
                array1[i] = array1[i].lower()

        return " ".join(array1).split()
    except:
        pass

def computeWordFrequencies(listOfToken: list) -> dict:
    try:
        m = dict()
        for word in listOfToken:
            if m.get(word):
                m[word] += 1
            else:
                m[word] = 1
        return m
    except:
        pass

def printf(m: dict) -> None:
    try:
        print("Word Frequency Counts")
        for key, value in sorted(m.items(), key=lambda item: item[1], reverse=True):
            print("<{token}>\t<{freq}>".format(token=key, freq=value))
        print()
    except:
        pass


def intersection(filename1: str, filename2: str) -> int:
    try:
        m1 = computeWordFrequencies(tokenize(filename1))
        m2 = computeWordFrequencies(tokenize(filename2))
        return len(set(m1) & set(m2))
    except:
        pass
