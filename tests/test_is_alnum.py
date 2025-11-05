"""
Test suite for is_alnum function in scraper.py
"""
import unittest
import sys
import os

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import is_alnum


class TestIsAlnum(unittest.TestCase):
    """Test the is_alnum helper function"""
    
    def test_digits(self):
        """Test that digits return True"""
        for digit in '0123456789':
            with self.subTest(digit=digit):
                self.assertTrue(is_alnum(digit))
    
    def test_lowercase_letters(self):
        """Test that lowercase letters return True"""
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            with self.subTest(letter=letter):
                self.assertTrue(is_alnum(letter))
    
    def test_uppercase_letters(self):
        """Test that uppercase letters return True"""
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            with self.subTest(letter=letter):
                self.assertTrue(is_alnum(letter))
    
    def test_special_characters(self):
        """Test that special characters return False"""
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?/~`" \t\n'
        for char in special_chars:
            with self.subTest(char=repr(char)):
                self.assertFalse(is_alnum(char))
    
    def test_empty_string(self):
        """Test that empty string returns False"""
        self.assertFalse(is_alnum(''))
    
    def test_multiple_characters(self):
        """Test that strings with multiple characters return False"""
        self.assertFalse(is_alnum('ab'))
        self.assertFalse(is_alnum('123'))
        self.assertFalse(is_alnum('hello'))


if __name__ == "__main__":
    unittest.main(verbosity=2)