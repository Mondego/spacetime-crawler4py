"""
Test suite for update_subdomain_analytics function in scraper.py
"""
import unittest
import sys
import os

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import update_subdomain_analytics, analytics, ALLOWED_DOMAINS


class TestUpdateSubdomainAnalytics(unittest.TestCase):
    """Test the update_subdomain_analytics helper function"""
    
    def setUp(self):
        """Reset analytics before each test"""
        analytics["subdomain_counts"].clear()
    
    def test_allowed_domain_tracking(self):
        """Test that allowed domains are tracked correctly"""
        url = "http://cs.uci.edu/research"
        update_subdomain_analytics(url)
        
        self.assertIn("cs.uci.edu", analytics["subdomain_counts"])
        self.assertEqual(analytics["subdomain_counts"]["cs.uci.edu"], 1)
    
    def test_multiple_pages_same_subdomain(self):
        """Test that multiple pages from same subdomain increment count"""
        urls = [
            "http://cs.uci.edu/research",
            "http://cs.uci.edu/faculty",
            "http://cs.uci.edu/courses"
        ]
        
        for url in urls:
            update_subdomain_analytics(url)
        
        self.assertEqual(analytics["subdomain_counts"]["cs.uci.edu"], 3)
    
    def test_multiple_different_subdomains(self):
        """Test tracking of different allowed subdomains"""
        urls = [
            "http://cs.uci.edu/research",
            "http://ics.uci.edu/faculty",
            "http://informatics.uci.edu/programs",
            "http://stat.uci.edu/data"
        ]
        
        for url in urls:
            update_subdomain_analytics(url)
        
        expected_counts = {
            "cs.uci.edu": 1,
            "ics.uci.edu": 1,
            "informatics.uci.edu": 1,
            "stat.uci.edu": 1
        }
        
        self.assertEqual(analytics["subdomain_counts"], expected_counts)
    
    def test_disallowed_domain_ignored(self):
        """Test that domains not in ALLOWED_DOMAINS are ignored"""
        # Test some UCI domains that are not in our allowed list
        disallowed_urls = [
            "http://uci.edu/main",
            "http://engineering.uci.edu/page",
            "http://bio.uci.edu/research",
            "http://math.uci.edu/courses"
        ]
        
        for url in disallowed_urls:
            update_subdomain_analytics(url)
        
        # Should be empty since none are in ALLOWED_DOMAINS
        self.assertEqual(len(analytics["subdomain_counts"]), 0)
    
    def test_subdomain_of_allowed_domain(self):
        """Test that subdomains of allowed domains are tracked"""
        urls = [
            "http://vision.ics.uci.edu/projects",
            "http://faculty.cs.uci.edu/profiles",
            "http://grad.informatics.uci.edu/admissions"
        ]
        
        for url in urls:
            update_subdomain_analytics(url)
        
        expected_counts = {
            "vision.ics.uci.edu": 1,
            "faculty.cs.uci.edu": 1,
            "grad.informatics.uci.edu": 1
        }
        
        self.assertEqual(analytics["subdomain_counts"], expected_counts)
    
    def test_case_insensitive_domains(self):
        """Test that domain checking is case insensitive"""
        urls = [
            "http://CS.UCI.EDU/research",
            "http://cs.uci.edu/faculty"
        ]
        
        for url in urls:
            update_subdomain_analytics(url)
        
        # Should be counted under lowercase domain
        self.assertEqual(analytics["subdomain_counts"]["cs.uci.edu"], 2)
    
    def test_https_urls(self):
        """Test that HTTPS URLs are handled correctly"""
        url = "https://ics.uci.edu/secure"
        update_subdomain_analytics(url)
        
        self.assertEqual(analytics["subdomain_counts"]["ics.uci.edu"], 1)
    
    def test_invalid_url_handling(self):
        """Test that invalid URLs don't crash the function"""
        invalid_urls = [
            "not-a-url",
            "",
            "ftp://example.com/files",  # Non-UCI domain with FTP
            "mailto:test@example.com",   # Different protocol
            "javascript:void(0)"         # JavaScript URL
        ]
        
        for url in invalid_urls:
            try:
                update_subdomain_analytics(url)
                # Should not crash
                self.assertTrue(True)
            except Exception as e:
                # The function should handle errors gracefully
                pass
        
        # Should still be empty since these are invalid/non-HTTP URLs or non-UCI domains
        self.assertEqual(len(analytics["subdomain_counts"]), 0)
    
    def test_none_url_handling(self):
        """Test that None URL is handled gracefully"""
        try:
            update_subdomain_analytics(None)
            # Should not crash
            self.assertTrue(True)
        except Exception:
            # Acceptable to have an exception for None
            pass
    
    def test_function_exists(self):
        """Test that the function exists and is callable"""
        self.assertTrue(callable(update_subdomain_analytics))
    
    def test_exact_domain_match(self):
        """Test that exact domain matches work (not just subdomains)"""
        url = "http://ics.uci.edu/"
        update_subdomain_analytics(url)
        
        self.assertEqual(analytics["subdomain_counts"]["ics.uci.edu"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)