"""
Test suite for extract_next_links function in scraper.py
"""
import unittest
from testScraper_Initilization import MockResponse, extract_next_links
class TestExtractNextLinks(unittest.TestCase):
    
    def test_basic_link_extraction(self):
        """Test extracting simple links from HTML"""
        html_content = """
        <html>
        <body>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        expected_links = [
            "http://ics.uci.edu/about",
            "http://ics.uci.edu/contact"
        ]
        
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_relative_url_conversion(self):
        """Test that relative URLs are converted to absolute URLs"""
        html_content = """
        <html>
        <body>
            <a href="about.html">About</a>
            <a href="/contact.html">Contact</a>
            <a href="../parent.html">Parent</a>
            <a href="subdir/page.html">Subdirectory</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/current/")
        links = extract_next_links("http://ics.uci.edu/current/", mock_resp)
        
        expected_links = [
            "http://ics.uci.edu/current/about.html",
            "http://ics.uci.edu/contact.html",
            "http://ics.uci.edu/parent.html",
            "http://ics.uci.edu/current/subdir/page.html"
        ]
        
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_fragment_removal(self):
        """Test that URL fragments (#) are properly removed"""
        html_content = """
        <html>
        <body>
            <a href="/page#section1">Section 1</a>
            <a href="/page#section2">Section 2</a>
            <a href="/other.html#top">Other Page</a>
            <a href="/normal">Normal Link</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        expected_links = [
            "http://ics.uci.edu/page",  # Only one instance (duplicates removed)
            "http://ics.uci.edu/other.html",
            "http://ics.uci.edu/normal"
        ]
        
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_absolute_urls(self):
        """Test handling of absolute URLs in links"""
        html_content = """
        <html>
        <body>
            <a href="http://cs.uci.edu/research">External CS</a>
            <a href="https://informatics.uci.edu/about">HTTPS Link</a>
            <a href="/local">Local Link</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        expected_links = [
            "http://cs.uci.edu/research",
            "https://informatics.uci.edu/about",
            "http://ics.uci.edu/local"
        ]
        
        self.assertEqual(sorted(links), sorted(expected_links))
    
    def test_empty_and_invalid_links(self):
        """Test handling of empty, whitespace, and missing href attributes"""
        html_content = """
        <html>
        <body>
            <a href="">Empty href</a>
            <a href="   ">Whitespace href</a>
            <a>No href attribute</a>
            <a href="/valid">Valid link</a>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Should only get the valid link (empty ones should be skipped)
        self.assertIn("http://ics.uci.edu/valid", links)
        # Empty href becomes base URL - this might be included
        # Whitespace href becomes base URL - this might be included
    
    def test_non_200_status(self):
        """Test that non-200 status codes return empty list"""
        html_content = "<html><body><a href='/test'>Test</a></body></html>"
        
        mock_resp = MockResponse(status=404, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        self.assertEqual(links, [])
    
    def test_no_raw_response(self):
        """Test handling when raw_response is None"""
        mock_resp = MockResponse(status=200, content="", url="http://ics.uci.edu/")
        mock_resp.raw_response = None
        
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        self.assertEqual(links, [])
    
    def test_no_content(self):
        """Test handling when raw_response.content is None"""
        mock_resp = MockResponse(status=200, content="test", url="http://ics.uci.edu/")
        # Simulate content being None after creation
        if mock_resp.raw_response:
            mock_resp.raw_response.content = None
        
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        self.assertEqual(links, [])
    
    def test_malformed_html(self):
        """Test handling of malformed HTML"""
        html_content = """
        <html>
        <body>
            <a href="/valid1">Valid 1</a>
            <a href="/valid2">Valid 2</a>
            <p>Some other content</p>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        # Should extract both valid links
        self.assertIn("http://ics.uci.edu/valid1", links)
        self.assertIn("http://ics.uci.edu/valid2", links)
    
    def test_no_links_in_html(self):
        """Test HTML with no anchor tags"""
        html_content = """
        <html>
        <body>
            <h1>Title</h1>
            <p>Some text content</p>
        </body>
        </html>
        """
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        links = extract_next_links("http://ics.uci.edu/", mock_resp)
        
        self.assertEqual(links, [])
    
    def test_base_url_fallback(self):
        """Test that function uses url parameter when resp.url is None"""
        html_content = '<html><body><a href="/test">Test</a></body></html>'
        
        mock_resp = MockResponse(status=200, content=html_content, url="http://ics.uci.edu/")
        mock_resp.url = None  # Simulate case where resp.url is None
        
        links = extract_next_links("http://ics.uci.edu/fallback", mock_resp)
        
        self.assertEqual(links, ["http://ics.uci.edu/test"])


if __name__ == "__main__":
    unittest.main(verbosity=2)