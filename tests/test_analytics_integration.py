"""
Test suite for analytics integration functions in scraper.py
Tests the higher-level analytics processing functions
"""
import unittest
import sys
import os
from lxml import html

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import (
    process_page_analytics, analytics, MIN_WORDS, stopwords,
    update_subdomain_analytics
)


class TestProcessPageAnalytics(unittest.TestCase):
    """Test the process_page_analytics integration function"""
    
    def setUp(self):
        """Reset analytics before each test"""
        analytics["unique_pages"].clear()
        analytics["word_frequencies"].clear()
        analytics["longest_page_url"] = None
        analytics["longest_page_word_count"] = 0
        analytics["subdomain_counts"].clear()
    
    def test_sufficient_content_processing(self):
        """Test processing a page with sufficient content"""
        # Create HTML with enough words (MIN_WORDS = 100)
        words = ["word"] * (MIN_WORDS + 10)  # 110 words
        text_content = " ".join(words)
        html_content = f"<html><body><p>{text_content}</p></body></html>"
        
        tree = html.fromstring(html_content)
        url = "http://test.com/page"
        
        result = process_page_analytics(url, tree)
        
        self.assertTrue(result)  # Should return True for successful processing
        self.assertIn(url, analytics["unique_pages"])
        self.assertGreater(analytics["word_frequencies"]["word"], 0)
        self.assertEqual(analytics["longest_page_url"], url)
        self.assertEqual(analytics["longest_page_word_count"], MIN_WORDS + 10)
    
    def test_insufficient_content_skipped(self):
        """Test that pages with insufficient content are skipped"""
        # Create HTML with too few words
        words = ["word"] * (MIN_WORDS - 10)  # 90 words
        text_content = " ".join(words)
        html_content = f"<html><body><p>{text_content}</p></body></html>"
        
        tree = html.fromstring(html_content)
        url = "http://test.com/page"
        
        result = process_page_analytics(url, tree)
        
        self.assertFalse(result)  # Should return False for insufficient content
        # Analytics should not be updated
        self.assertEqual(len(analytics["word_frequencies"]), 0)
        self.assertIsNone(analytics["longest_page_url"])
    
    def test_stopwords_excluded(self):
        """Test that stopwords are excluded from analytics"""
        # Create content with mix of stopwords and regular words
        content_words = ["computer", "science"] * 30  # 60 meaningful words
        stop_words = ["the", "and", "or"] * 20  # 60 stopwords
        all_words = content_words + stop_words  # 120 total words
        
        text_content = " ".join(all_words)
        html_content = f"<html><body><p>{text_content}</p></body></html>"
        
        tree = html.fromstring(html_content)
        url = "http://test.com/page"
        
        result = process_page_analytics(url, tree)
        
        self.assertTrue(result)
        # Should have meaningful words but not stopwords
        self.assertIn("computer", analytics["word_frequencies"])
        self.assertIn("science", analytics["word_frequencies"])
        self.assertNotIn("the", analytics["word_frequencies"])
        self.assertNotIn("and", analytics["word_frequencies"])
        self.assertEqual(analytics["word_frequencies"]["computer"], 30)
        self.assertEqual(analytics["word_frequencies"]["science"], 30)
    
    def test_longest_page_tracking(self):
        """Test that longest page is tracked correctly"""
        # Process first page
        words1 = ["word"] * (MIN_WORDS + 5)
        html1 = f"<html><body><p>{' '.join(words1)}</p></body></html>"
        tree1 = html.fromstring(html1)
        url1 = "http://test.com/page1"
        
        process_page_analytics(url1, tree1)
        
        self.assertEqual(analytics["longest_page_url"], url1)
        self.assertEqual(analytics["longest_page_word_count"], MIN_WORDS + 5)
        
        # Process longer page
        words2 = ["word"] * (MIN_WORDS + 20)
        html2 = f"<html><body><p>{' '.join(words2)}</p></body></html>"
        tree2 = html.fromstring(html2)
        url2 = "http://test.com/page2"
        
        process_page_analytics(url2, tree2)
        
        self.assertEqual(analytics["longest_page_url"], url2)
        self.assertEqual(analytics["longest_page_word_count"], MIN_WORDS + 20)
        
        # Process shorter page - should not replace longest
        words3 = ["word"] * (MIN_WORDS + 10)
        html3 = f"<html><body><p>{' '.join(words3)}</p></body></html>"
        tree3 = html.fromstring(html3)
        url3 = "http://test.com/page3"
        
        process_page_analytics(url3, tree3)
        
        # Should still have page2 as longest
        self.assertEqual(analytics["longest_page_url"], url2)
        self.assertEqual(analytics["longest_page_word_count"], MIN_WORDS + 20)
    
    def test_script_style_removal(self):
        """Test that script and style content is excluded from word count"""
        meaningful_words = ["research", "computer"] * 60  # 120 meaningful words
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ color: red; font-size: 12px; background: blue; }}
                .class {{ margin: 10px; padding: 5px; }}
            </style>
        </head>
        <body>
            <p>{' '.join(meaningful_words)}</p>
            <script>
                var x = 100;
                function test() {{ alert('hello world test function'); }}
                console.log('debugging message with words');
            </script>
        </body>
        </html>
        """
        
        tree = html.fromstring(html_content)
        url = "http://test.com/page"
        
        result = process_page_analytics(url, tree)
        
        self.assertTrue(result)
        # Should only count meaningful words, not CSS/JS
        self.assertIn("research", analytics["word_frequencies"])
        self.assertIn("computer", analytics["word_frequencies"])
        self.assertNotIn("color", analytics["word_frequencies"])
        self.assertNotIn("red", analytics["word_frequencies"])
        self.assertNotIn("function", analytics["word_frequencies"])
        self.assertNotIn("alert", analytics["word_frequencies"])
        
        # Word count should reflect only meaningful content
        self.assertEqual(analytics["longest_page_word_count"], 120)
    
    def test_error_handling(self):
        """Test error handling with malformed input"""
        # Test with None tree
        result = process_page_analytics("http://test.com", None)
        self.assertFalse(result)
        
        # Analytics should remain unchanged
        self.assertEqual(len(analytics["word_frequencies"]), 0)


class TestUpdateSubdomainAnalytics(unittest.TestCase):
    """Test the update_subdomain_analytics helper function (TODO implementation)"""
    
    def setUp(self):
        """Reset analytics before each test"""
        analytics["subdomain_counts"].clear()
    
    def test_subdomain_analytics_implemented(self):
        """Test that the subdomain analytics function is implemented and working"""
        url = "http://cs.uci.edu/research"
        
        # Should not crash when called
        try:
            update_subdomain_analytics(url)
            # Should work without error since it's implemented
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"update_subdomain_analytics raised an exception: {e}")
        
        # Should modify analytics since it's now implemented
        self.assertEqual(len(analytics["subdomain_counts"]), 1)
        self.assertIn("cs.uci.edu", analytics["subdomain_counts"])
        self.assertEqual(analytics["subdomain_counts"]["cs.uci.edu"], 1)


class TestAnalyticsGlobals(unittest.TestCase):
    """Test the analytics global variables and constants"""
    
    def test_min_words_constant(self):
        """Test that MIN_WORDS is set correctly"""
        self.assertEqual(MIN_WORDS, 50)
        self.assertIsInstance(MIN_WORDS, int)
    
    def test_stopwords_set(self):
        """Test that stopwords is properly configured"""
        self.assertIsInstance(stopwords, set)
        self.assertGreater(len(stopwords), 50)  # Should have many stopwords
        
        # Test some common stopwords are included
        common_stopwords = ["the", "and", "or", "but", "in", "on", "at", "to"]
        for word in common_stopwords:
            self.assertIn(word, stopwords)
    
    def test_analytics_structure(self):
        """Test that analytics dictionary has correct structure"""
        expected_keys = [
            "unique_pages", "longest_page_url", "longest_page_word_count",
            "word_frequencies", "subdomain_counts"
        ]
        
        for key in expected_keys:
            self.assertIn(key, analytics)
        
        # Test types
        self.assertIsInstance(analytics["unique_pages"], set)
        self.assertIsInstance(analytics["word_frequencies"], dict)
        self.assertIsInstance(analytics["subdomain_counts"], dict)
        self.assertIsInstance(analytics["longest_page_word_count"], int)


if __name__ == "__main__":
    unittest.main(verbosity=2)