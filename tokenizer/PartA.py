import re
import sys
from collections import defaultdict

# O(n) if n is the size of the file
# 
# this function is more efficient than tokenize for
# finding the collection of UNIQUE tokens in a file
# so it is used in PartB instead of tokenize
#
# the code iterates through each "token" a 
# constant number of times, once in re.split(),
# once to add to final toks set
def set_tokenize(file_name: str) -> set:
  toks = set()
  try:
    with open(file_name, "r") as f:
      for line in f:
        strings = re.split('[^a-zA-Z0-9]', line)
        for string in strings:
          if string != "":
            toks.add(string.lower())
  except FileNotFoundError:
    print(f"File not found: {file_name}")
  return toks

# O(n) if n is the size of the file
#
# the code iterates through each "token" a
# constant number of times, once in re.split(),
# once to add to final toks list
def tokenize(file_name: str) -> list:
  toks = []
  try:
    with open(file_name, "r") as f:
      for line in f:
        strings = re.split('[^a-zA-Z0-9]', line)
        for string in strings:
          if string != "":
            toks.append(string.lower())
  except FileNotFoundError:
    print(f"File not found: {file_name}")
  return toks

# O(n) if n is the number of tokens
#
# the code iterates through each "token" once
def compute_word_frequencies(tokens: list) -> dict:
  word_freqs = defaultdict(int)
  for tok in tokens:
    word_freqs[tok] += 1
  return word_freqs

# O(nlogn) if n is the number of tokens/frequency associations
#
# Uses python "sorted" algorithm, which is Timsort with a
# time complexity of O(nlogn)
# https://en.wikipedia.org/wiki/Timsort
def print_frequencies(tok_freqs: dict) -> None:
  for assoc in sorted(tok_freqs, key=tok_freqs.get, reverse=True):
    print(f"{assoc}\t{tok_freqs[assoc]}")

# O(n) calls tokenize, compute_word_frequencies, 
# and print_frequencies once each
def main():
  sys_args = sys.argv
  if (len(sys_args) != 2):
    print("Please specify a single file")
  else:
    tokens = tokenize(sys_args[1])
    word_freqs = compute_word_frequencies(tokens)
    print_frequencies(word_freqs)

if __name__ == "__main__": 
  main()
