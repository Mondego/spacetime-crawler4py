"""
Test suite for process_page_analytics function in scraper.py
"""
import unittest
import sys
import os
from lxml import html

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import process_page_analytics, analytics, MIN_WORDS


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


if __name__ == "__main__":
    unittest.main(verbosity=2)