import unittest
import tokenizer
import simHash

from pathlib import Path

class TestSimilarity(unittest.TestCase):
    def test_simpleFiles(self):
        p1 = Path(r"TestFiles/a.txt")
        p2 = Path(r"TestFiles/b.txt")

        freq1 = tokenizer.computeWordFrequencies(tokenizer.tokenize(p1))
        freq2 = tokenizer.computeWordFrequencies(tokenizer.tokenize(p2))

        f1 = simHash.generate_Fingerprint(freq1)
        f2 = simHash.generate_Fingerprint(freq2)

        assert simHash.calc_similarity(f1, f1)

if __name__ == "__main__":
    unittest.main()