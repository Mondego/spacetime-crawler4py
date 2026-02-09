import sys
import os

#O(n), n = characters in file; O(1) for each line and each char check and O(n) to concatenate the token
#Can take O(n^2) if word is really big
def tokenize(file_path: str):
    tokens = []
    buff = ""
    try:
        with open(file_path, 'r') as f:
            for line in f:
                for char in line:
                    if char.isalnum() and char.isascii():
                            buff = buff + char.lower()
                    else:
                        if buff != "":
                            tokens.append(buff)
                            buff = ""

        if buff != "": tokens.append(buff)
        return tokens
    except FileNotFoundError:
        print(f"File ({file_path}) Not Found")

#O(n), n = tokens; lookup takes O(1) for each word and loop for each token
def computeWordFrequencies(arr: list):
    try:
        word_freq = {}
        for word in arr:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        return word_freq
    except Exception as e:
        print(f'Error occurred: {e}')