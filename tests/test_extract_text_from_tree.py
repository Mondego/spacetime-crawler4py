"""
Test suite for extract_text_from_tree function in scraper.py
"""
import unittest
import sys
import os
from lxml import html

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import extract_text_from_tree


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


if __name__ == "__main__":
    unittest.main(verbosity=2)