"""
Test suite for helper functions in scraper.py
Tests all the refactored helper functions for analytics and text processing
"""
import unittest
import sys
import os
from lxml import html

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import (
    is_alnum, tokenize_text, extract_text_from_tree, 
    update_word_frequencies, update_longest_page, 
    analytics, extract_links_from_tree, MIN_WORDS, stopwords
)


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


class TestExtractTextFromTree(unittest.TestCase):
    """Test the extract_text_from_tree helper function"""
    
    def test_simple_html(self):
        """Test extraction from simple HTML"""
        html_content = "<html><body><p>Hello world</p></body></html>"
        tree = html.fromstring(html_content)
        text = extract_text_from_tree(tree)
        self.assertIn("Hello world", text)
    
    def test_script_removal(self):
        """Test that script tags are removed"""
        html_content = """
        <html>
        <body>
            <p>Visible text</p>
            <script>alert('hidden');</script>
            <p>More visible text</p>
        </body>
        </html>
        """
        tree = html.fromstring(html_content)
        text = extract_text_from_tree(tree)
        self.assertIn("Visible text", text)
        self.assertIn("More visible text", text)
        self.assertNotIn("alert", text)
        self.assertNotIn("hidden", text)
    
    def test_style_removal(self):
        """Test that style tags are removed"""
        html_content = """
        <html>
        <body>
            <p>Visible text</p>
            <style>body { color: red; }</style>
            <p>More visible text</p>
        </body>
        </html>
        """
        tree = html.fromstring(html_content)
        text = extract_text_from_tree(tree)
        self.assertIn("Visible text", text)
        self.assertIn("More visible text", text)
        self.assertNotIn("color", text)
        self.assertNotIn("red", text)
    
    def test_noscript_removal(self):
        """Test that noscript tags are removed"""
        html_content = """
        <html>
        <body>
            <p>Visible text</p>
            <noscript>Enable JavaScript</noscript>
            <p>More visible text</p>
        </body>
        </html>
        """
        tree = html.fromstring(html_content)
        text = extract_text_from_tree(tree)
        self.assertIn("Visible text", text)
        self.assertIn("More visible text", text)
        self.assertNotIn("Enable JavaScript", text)
    
    def test_whitespace_normalization(self):
        """Test that whitespace is normalized"""
        html_content = """
        <html>
        <body>
            <p>Hello    world</p>
            <p>
                Multiple
                lines
            </p>
        </body>
        </html>
        """
        tree = html.fromstring(html_content)
        text = extract_text_from_tree(tree)
        # Text should be normalized to single spaces
        self.assertNotIn("    ", text)  # Multiple spaces should be collapsed
        self.assertIn("Hello world", text)
        self.assertIn("Multiple lines", text)
    
    def test_empty_html(self):
        """Test with HTML that has no text content"""
        html_content = "<html><body></body></html>"
        tree = html.fromstring(html_content)
        text = extract_text_from_tree(tree)
        self.assertEqual(text.strip(), "")


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


class TestExtractLinksFromTree(unittest.TestCase):
    """Test the extract_links_from_tree helper function"""
    
    def test_simple_link_extraction(self):
        """Test extracting simple links"""
        html_content = '''
        <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </body>
        </html>
        '''
        tree = html.fromstring(html_content)
        base_url = "http://test.com"
        
        links = extract_links_from_tree(tree, base_url)
        
        expected = ["http://test.com/page1", "http://test.com/page2"]
        self.assertEqual(sorted(links), sorted(expected))
    
    def test_relative_url_conversion(self):
        """Test that relative URLs are converted to absolute"""
        html_content = '''
        <html>
        <body>
            <a href="relative.html">Relative</a>
            <a href="/absolute.html">Absolute</a>
            <a href="../parent.html">Parent</a>
        </body>
        </html>
        '''
        tree = html.fromstring(html_content)
        base_url = "http://test.com/subdir/"
        
        links = extract_links_from_tree(tree, base_url)
        
        expected = [
            "http://test.com/subdir/relative.html",
            "http://test.com/absolute.html",
            "http://test.com/parent.html"
        ]
        self.assertEqual(sorted(links), sorted(expected))
    
    def test_fragment_removal(self):
        """Test that URL fragments are removed"""
        html_content = '''
        <html>
        <body>
            <a href="/page#section1">Section 1</a>
            <a href="/page#section2">Section 2</a>
        </body>
        </html>
        '''
        tree = html.fromstring(html_content)
        base_url = "http://test.com"
        
        links = extract_links_from_tree(tree, base_url)
        
        # Both should resolve to same URL without fragment
        expected = ["http://test.com/page"]
        self.assertEqual(links, expected + expected)  # Will have duplicates
    
    def test_empty_href_handling(self):
        """Test handling of empty href attributes"""
        html_content = '''
        <html>
        <body>
            <a href="">Empty</a>
            <a href="/valid">Valid</a>
        </body>
        </html>
        '''
        tree = html.fromstring(html_content)
        base_url = "http://test.com"
        
        links = extract_links_from_tree(tree, base_url)
        
        # Empty href should resolve to base URL
        self.assertIn("http://test.com", links)
        self.assertIn("http://test.com/valid", links)
    
    def test_no_links(self):
        """Test HTML with no anchor tags"""
        html_content = '''
        <html>
        <body>
            <p>No links here</p>
        </body>
        </html>
        '''
        tree = html.fromstring(html_content)
        base_url = "http://test.com"
        
        links = extract_links_from_tree(tree, base_url)
        
        self.assertEqual(links, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)