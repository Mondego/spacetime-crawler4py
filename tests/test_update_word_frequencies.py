"""
Test suite for update_word_frequencies function in scraper.py
"""
import unittest
import sys
import os

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import update_word_frequencies, analytics


class TestUpdateWordFrequencies(unittest.TestCase):
    """Test the update_word_frequencies helper function"""
    
    def setUp(self):
        """Reset analytics before each test"""
        analytics["word_frequencies"].clear()
    
    def test_basic_frequency_update(self):
        """Test basic word frequency counting"""
        words = ["hello", "world", "hello"]
        update_word_frequencies(words)
        
        self.assertEqual(analytics["word_frequencies"]["hello"], 2)
        self.assertEqual(analytics["word_frequencies"]["world"], 1)
    
    def test_stopwords_excluded(self):
        """Test that stopwords are excluded from frequency count"""
        words = ["the", "hello", "and", "world", "the"]
        update_word_frequencies(words)
        
        self.assertNotIn("the", analytics["word_frequencies"])
        self.assertNotIn("and", analytics["word_frequencies"])
        self.assertEqual(analytics["word_frequencies"]["hello"], 1)
        self.assertEqual(analytics["word_frequencies"]["world"], 1)
    
    def test_empty_word_list(self):
        """Test with empty word list"""
        words = []
        update_word_frequencies(words)
        
        self.assertEqual(len(analytics["word_frequencies"]), 0)
    
    def test_all_stopwords(self):
        """Test with list containing only stopwords"""
        words = ["the", "and", "or", "but"]
        update_word_frequencies(words)
        
        self.assertEqual(len(analytics["word_frequencies"]), 0)
    
    def test_cumulative_updates(self):
        """Test that multiple calls accumulate frequencies"""
        words1 = ["hello", "world"]
        words2 = ["hello", "test"]
        
        update_word_frequencies(words1)
        update_word_frequencies(words2)
        
        self.assertEqual(analytics["word_frequencies"]["hello"], 2)
        self.assertEqual(analytics["word_frequencies"]["world"], 1)
        self.assertEqual(analytics["word_frequencies"]["test"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)