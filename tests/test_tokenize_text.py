"""
Test suite for tokenize_text function in scraper.py
"""
import unittest
import sys
import os

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import tokenize_text


class TestTokenizeText(unittest.TestCase):
    """Test the tokenize_text helper function"""
    
    def test_simple_text(self):
        """Test tokenization of simple text"""
        text = "Hello world"
        expected = ["hello", "world"]
        self.assertEqual(tokenize_text(text), expected)
    
    def test_mixed_case(self):
        """Test that text is converted to lowercase"""
        text = "Hello WORLD Test"
        expected = ["hello", "world", "test"]
        self.assertEqual(tokenize_text(text), expected)
    
    def test_punctuation_separation(self):
        """Test that punctuation separates words"""
        text = "Hello, world! How are you?"
        expected = ["hello", "world", "how", "are", "you"]
        self.assertEqual(tokenize_text(text), expected)
    
    def test_numbers_included(self):
        """Test that numbers are included in tokens"""
        text = "Test123 hello world456"
        expected = ["test123", "hello", "world456"]
        self.assertEqual(tokenize_text(text), expected)
    
    def test_hyphenated_words(self):
        """Test handling of hyphenated words (should split)"""
        text = "state-of-the-art algorithm"
        expected = ["state", "of", "the", "art", "algorithm"]
        self.assertEqual(tokenize_text(text), expected)
    
    def test_apostrophes(self):
        """Test handling of apostrophes (should split)"""
        text = "don't can't won't"
        expected = ["don", "t", "can", "t", "won", "t"]
        self.assertEqual(tokenize_text(text), expected)
    
    def test_empty_string(self):
        """Test that empty string returns empty list"""
        self.assertEqual(tokenize_text(""), [])
    
    def test_none_input(self):
        """Test that None input returns empty list"""
        self.assertEqual(tokenize_text(None), [])
    
    def test_whitespace_only(self):
        """Test that whitespace-only string returns empty list"""
        self.assertEqual(tokenize_text("   \t\n  "), [])
    
    def test_special_characters_only(self):
        """Test that string with only special characters returns empty list"""
        self.assertEqual(tokenize_text("!@#$%^&*()"), [])
    
    def test_multiple_spaces(self):
        """Test handling of multiple spaces between words"""
        text = "hello     world    test"
        expected = ["hello", "world", "test"]
        self.assertEqual(tokenize_text(text), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)