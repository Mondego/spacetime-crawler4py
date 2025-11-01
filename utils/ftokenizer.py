from stokenizer import STokenizer as stn
from collections import defaultdict
import sys


class FileTokenizer:
    def __init__(self, path, lines_per_read=100):
        self.path = path
        self.lines_per_read = lines_per_read
        self.count_dict = defaultdict(int)

    """
    Time complexity O(N*logN). Since it basically just read all text, consumed it character by character
    and stored token inside a dictionary. This is just O(N). However, I sorted the dictionary and return
    it as a list 0(N*logN). Therefore, the time complexity is O(N*logN).
    """
    def tokenize(self):
        with open(self.path, "r", encoding="utf-8") as f:
            while True:
                lines = [line for _ in range(self.lines_per_read) if (line := f.readline())]
                if not lines:
                    break

                # combine all lines to string and feed into tokenizer
                texts = "".join(lines)
                tokenizer = stn(texts)

                for token in tokenizer.tokenize():
                    self.count_dict[token] += 1

        return sorted(self.count_dict.keys())

    """
    This is a method just return the dictionary that finished in method: tokenize(). This method call is just O(1),
    but the "tokenize" part for this is O(N).
    """
    def computeWordFrequencies(self):
        return self.count_dict


    def print(self):
        sorted_list = sorted(self.count_dict.items(), key=lambda t: t[1], reverse=True)  # Descending order: value
        for item in sorted_list:
            print(f"{item[0]}\t{item[1]}")


def main():
    if len(sys.argv) < 2:
        print("python <script_name.py> <file_path>")
        sys.exit(1)

    path = sys.argv[1]
    ftokenizer = FileTokenizer(path)
    ftokenizer.tokenize()
    ftokenizer.print()


if __name__ == "__main__":
    main()
