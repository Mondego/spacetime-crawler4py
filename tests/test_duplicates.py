"""
Test suite for duplicate handling in extract_next_links function
"""
import unittest
from testScraper_Initilization import MockResponse, extract_next_links


class TestDuplicateHandling(unittest.TestCase):
    
    def test_duplicate_removal_basic(self):
        """Test that duplicate URLs are removed"""
        html_content = """
        <html>
        <body>
            <a href="/page">Page 1</a>
            <a href="/page">Page 2 (duplicate)</a>
            <a href="/other">Other</a>
            <a href="/page">Page 3 (duplicate)</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Should only have 2 unique links
        expected_links = [
            "http://ics.uci.edu/page",
            "http://ics.uci.edu/other"
        ]
        
        self.assertEqual(len(links), 2)
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_duplicate_fragments_removed(self):
        """Test that URLs with different fragments become duplicates and are handled"""
        html_content = """
        <html>
        <body>
            <a href="/page#intro">Introduction</a>
            <a href="/page#section1">Section 1</a>
            <a href="/page">Main Page</a>
            <a href="/page#conclusion">Conclusion</a>
            <a href="/other#top">Other Page</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # All /page#* URLs should become /page (first occurrence kept)
        expected_links = [
            "http://ics.uci.edu/page",  # First occurrence wins
            "http://ics.uci.edu/other"
        ]
        
        self.assertEqual(len(links), 2)
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_order_preservation(self):
        """Test that the order of first occurrence is preserved"""
        html_content = """
        <html>
        <body>
            <a href="/first">First</a>
            <a href="/second">Second</a>
            <a href="/first">First Duplicate</a>
            <a href="/third">Third</a>
            <a href="/second">Second Duplicate</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Order should be: first, second, third (order of first appearance)
        expected_links = [
            "http://ics.uci.edu/first",
            "http://ics.uci.edu/second", 
            "http://ics.uci.edu/third"
        ]
        
        self.assertEqual(links, expected_links)  # Order matters
    
    def test_case_sensitive_duplicates(self):
        """Test that URLs are case-sensitive for duplicate detection"""
        html_content = """
        <html>
        <body>
            <a href="/Page">Page (uppercase P)</a>
            <a href="/page">page (lowercase p)</a>
            <a href="/PAGE">PAGE (all caps)</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Should keep all three since URLs are case-sensitive
        expected_links = [
            "http://ics.uci.edu/Page",
            "http://ics.uci.edu/page",
            "http://ics.uci.edu/PAGE"
        ]
        
        self.assertEqual(len(links), 3)
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_query_parameter_duplicates(self):
        """Test that URLs with different query parameters are not considered duplicates"""
        html_content = """
        <html>
        <body>
            <a href="/search?q=test">Search test</a>
            <a href="/search?q=other">Search other</a>
            <a href="/search?q=test">Search test duplicate</a>
            <a href="/search">Search no params</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Should have 3 unique URLs (one duplicate removed)
        expected_links = [
            "http://ics.uci.edu/search?q=test",
            "http://ics.uci.edu/search?q=other",
            "http://ics.uci.edu/search"
        ]
        
        self.assertEqual(len(links), 3)
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_mixed_relative_absolute_duplicates(self):
        """Test duplicates when mixing relative and absolute URLs"""
        html_content = """
        <html>
        <body>
            <a href="/page">Relative</a>
            <a href="http://ics.uci.edu/page">Absolute</a>
            <a href="page">Relative no slash</a>
            <a href="./page">Relative with dot</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # First two should resolve to same URL, last two should resolve to same URL
        expected_unique_count = 2
        self.assertLessEqual(len(links), expected_unique_count)
        
        # Check that /page is in the results
        self.assertIn("http://ics.uci.edu/page", links)
    
    def test_empty_links_no_duplicates(self):
        """Test that empty links don't create false duplicates"""
        html_content = """
        <html>
        <body>
            <a href="">Empty 1</a>
            <a href="  ">Whitespace</a>
            <a href="">Empty 2</a>
            <a href="/valid">Valid</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Should only have the valid link (empty ones filtered out)
        self.assertIn("http://ics.uci.edu/valid", links)
        # Empty links should be filtered out by the 'if link:' check
    
    def test_large_number_of_duplicates(self):
        """Test performance with many duplicates"""
        # Generate HTML with many duplicate links
        duplicate_links = ['<a href="/page">Link</a>'] * 100
        other_links = [f'<a href="/page{i}">Page {i}</a>' for i in range(10)]
        
        html_content = f"""
        <html>
        <body>
            {''.join(duplicate_links)}
            {''.join(other_links)}
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Should have 11 unique links (1 /page + 10 /page0-page9)
        self.assertEqual(len(links), 11)
        
        # Check that all expected links are present
        self.assertIn("http://ics.uci.edu/page", links)
        for i in range(10):
            self.assertIn(f"http://ics.uci.edu/page{i}", links)
    
    def test_no_duplicates_scenario(self):
        """Test that function works correctly when there are no duplicates"""
        html_content = """
        <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="/page3">Page 3</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        expected_links = [
            "http://ics.uci.edu/page1",
            "http://ics.uci.edu/page2",
            "http://ics.uci.edu/page3"
        ]
        
        self.assertEqual(len(links), 3)
        self.assertEqual(links, expected_links)  # Order should be preserved


if __name__ == "__main__":
    unittest.main(verbosity=2)