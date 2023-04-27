from pathlib import Path
from collections import defaultdict
import sys


# TIME COMPLEXITY: 
# O(n*m) where n is the number of lines in the text file and m is the number of chars in a line
# polynomial time that increases as the number of lines or number of chars increases
def tokenize(filepath: Path) -> list[str]:
    """
    Reads a text file and returns a list of tokens in that file.
    Tokens: a sequence of alphanumeric characters regardless of capitalization
    """

    filepath = Path(filepath) #ensure the object passed is a path
    if not filepath.exists():
        print(f"The file({filepath}) does not exist")
        return []
    if not filepath.is_file():
        print("The file is not a file.")
        return []

    with open(filepath, 'rb') as file: # checks if a file name is in binary
        if b'\0' in file.read(): #b\0 is null byte which would indicate the file is binary
            print("File is binary")
            return []
        
    tokens = list()

    try:
        with open(filepath, 'r', errors="ignore") as txt_file:  #errors=ignore omits bad data
            for line in txt_file:
                token_to_add = ""
                for potential_char in line.strip():
                    try:
                        if ord(potential_char) in range(ord('a'), ord('z') +1) or ord(potential_char) in range(ord('A'), ord('Z') +1) or ord(potential_char) in range(ord('0'), ord('9') +1):
                            token_to_add += potential_char
                        else: #when we reach a character that isn't alphanumeric
                            if token_to_add:
                                tokens.append(token_to_add)
                                token_to_add = ""
                    except UnicodeDecodeError:
                        print("invalid character")
                        if token_to_add:  #if we reach in invalid character then that's our split point
                            tokens.append(token_to_add)
                            token_to_add = ""

                
                if token_to_add:  #for when we are in the last line, last word
                    tokens.append(token_to_add)
                    token_to_add = ""
    except MemoryError:   # CHANGE: said in lec to read byte by byte
        print("File too big")
        return []

    return tokens


# TIME COMPLEXITY: 
# O(N) where n is the size of "tokens"
# linear time that grows as the number of "tokens" increases 
def computeWordFrequencies(tokens: list[str]) -> defaultdict():
    """
    Computes word frequencies given a list of tokens.
    """
    word_freq = defaultdict(lambda: 0) #sets default frequency to 0
    for t in tokens:
        t = t.lower()
        word_freq[t] += 1

    return word_freq


# TIME COMPLEXITY:
# O(N) where N is the length of "freq"
# linear time that grows as the number of keys in the dictionary grows
def printFreq(freq: dict()) -> None:
    """
    Prints the frequencies given a dictionary where keys are the tokens and values are their frequencies.
    """
    sorted_dict ={key:val for key,val in sorted({k: freq[k] for k in sorted(freq)}.items(), key=lambda x:-x[1]) } #creates a dictionary sorted by frequency and then in alphabetical, O(N)

    #f = open("output.txt", "w")
    for item in sorted_dict.items():   #O(N) runtime complexity
        #f.write(f"{item[0]} -> {item[1]}\n")       
        print(f"{item[0]} -> {item[1]}")
    
    #f.close()

if __name__ == "__main__":
    try:
        p = Path(sys.argv[1])
    # p = Path(r"C:\Users\steie\OneDrive\Desktop\College\CS 121\Assignment 1\tests\simpletest.txt")
        freq = computeWordFrequencies(tokenize(p))
        printFreq(freq)

    except IndexError:
        print("Not enough inputs provided")

