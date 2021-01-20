import sys

from PartA import set_tokenize

# O(N) if n is the size of the file inputs
#
# used set_tokenize to improve efficiency
# 
# set_tokenize is called twice, which is O(N)
# intersection is called once, which is O(N) 
# https://wiki.python.org/moin/TimeComplexity#set
def print_compare_files(file1_name: str, file2_name: str) -> None:
  file1_toks = set_tokenize(file1_name)
  file2_toks = set_tokenize(file2_name)
  in_common_toks = file1_toks.intersection(file2_toks)
  print(len(in_common_toks))

# O(N) if n is the size of the file inputs
# 
# print_compare_files is called once, O(N)
if __name__ == "__main__":
  sys_args = sys.argv
  if (len(sys_args) != 3):
    print("Please specify two files")
  else:
    print_compare_files(sys_args[1], sys_args[2])
  
