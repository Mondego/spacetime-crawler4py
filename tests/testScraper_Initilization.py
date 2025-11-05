"""
Test suite for extract_next_links function in scraper.py
"""
import unittest
import sys
import os

# Add parent directory to path so we can import scraper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import extract_next_links


class MockRawResponse:
    """Mock object to simulate requests.Response"""
    def __init__(self, content, url="http://ics.uci.edu/test"):
        self.content = content.encode() if isinstance(content, str) else content
        self.url = url
        self.text = content if isinstance(content, str) else content.decode()


class MockResponse:
    """Mock object to simulate utils.response.Response"""
    def __init__(self, status=200, content="", url="http://ics.uci.edu/test"):
        self.status = status
        self.url = url
        self.raw_response = MockRawResponse(content, url) if status == 200 and content else None
        self.error = None

