"""
Test suite for update_longest_page function in scraper.py
"""
import unittest
import sys
import os

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import update_longest_page, analytics


class TestUpdateLongestPage(unittest.TestCase):
    """Test the update_longest_page helper function"""
    
    def setUp(self):
        """Reset analytics before each test"""
        analytics["longest_page_url"] = None
        analytics["longest_page_word_count"] = 0
    
    def test_first_page(self):
        """Test setting the first page as longest"""
        url = "http://test.com/page1"
        word_count = 100
        
        update_longest_page(url, word_count)
        
        self.assertEqual(analytics["longest_page_url"], url)
        self.assertEqual(analytics["longest_page_word_count"], word_count)
    
    def test_longer_page_replaces(self):
        """Test that longer page replaces current longest"""
        # Set initial page
        update_longest_page("http://test.com/page1", 100)
        
        # Add longer page
        longer_url = "http://test.com/page2"
        longer_count = 200
        update_longest_page(longer_url, longer_count)
        
        self.assertEqual(analytics["longest_page_url"], longer_url)
        self.assertEqual(analytics["longest_page_word_count"], longer_count)
    
    def test_shorter_page_ignored(self):
        """Test that shorter page doesn't replace current longest"""
        # Set initial page
        original_url = "http://test.com/page1"
        original_count = 200
        update_longest_page(original_url, original_count)
        
        # Try to add shorter page
        update_longest_page("http://test.com/page2", 100)
        
        # Should still have original page
        self.assertEqual(analytics["longest_page_url"], original_url)
        self.assertEqual(analytics["longest_page_word_count"], original_count)
    
    def test_equal_length_ignored(self):
        """Test that page with equal length doesn't replace current longest"""
        # Set initial page
        original_url = "http://test.com/page1"
        original_count = 200
        update_longest_page(original_url, original_count)
        
        # Try to add page with same length
        update_longest_page("http://test.com/page2", 200)
        
        # Should still have original page
        self.assertEqual(analytics["longest_page_url"], original_url)
        self.assertEqual(analytics["longest_page_word_count"], original_count)


if __name__ == "__main__":
    unittest.main(verbosity=2)