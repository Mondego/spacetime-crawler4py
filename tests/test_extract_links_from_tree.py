"""
Test suite for extract_links_from_tree function in scraper.py
"""
import unittest
import sys
import os
from lxml import html

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import extract_links_from_tree


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