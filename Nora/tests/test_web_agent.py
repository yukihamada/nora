"""
Tests for the Web Agent.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.web_agent import WebAgent

class TestWebAgent(unittest.TestCase):
    """Tests for the Web Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "web_browsing": {
                "use_puppeteer": False,
                "headless": True
            }
        }
        
        # Initialize the agent
        self.agent = WebAgent(self.config)
    
    @patch('src.agents.web_agent.WebAgent._perform_search')
    def test_execute_search(self, mock_perform_search):
        """Test executing a search task."""
        # Set up the mock
        mock_perform_search.return_value = {
            "query": "test query",
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "snippet": "This is a test result"
                }
            ],
            "timestamp": 1234567890
        }
        
        # Execute the task
        result = self.agent.execute("search for test query")
        
        # Check that the search was performed
        mock_perform_search.assert_called_once()
        
        # Check the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["query"], "test query")
        self.assertEqual(len(result["data"]["results"]), 1)
    
    @patch('src.agents.web_agent.WebAgent._scrape_website')
    def test_execute_scrape(self, mock_scrape_website):
        """Test executing a scraping task."""
        # Set up the mock
        mock_scrape_website.return_value = {
            "url": "https://example.com",
            "title": "Example Website",
            "text_content": "This is an example website",
            "links": [],
            "images": [],
            "timestamp": 1234567890
        }
        
        # Execute the task
        result = self.agent.execute("scrape https://example.com")
        
        # Check that the website was scraped
        mock_scrape_website.assert_called_once()
        
        # Check the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["url"], "https://example.com")
        self.assertEqual(result["data"]["title"], "Example Website")
    
    @patch('src.agents.web_agent.WebAgent._gather_information')
    def test_execute_gather_information(self, mock_gather_information):
        """Test executing an information gathering task."""
        # Set up the mock
        mock_gather_information.return_value = {
            "topic": "test topic",
            "search_results": {
                "query": "test topic",
                "results": []
            },
            "detailed_information": [],
            "timestamp": 1234567890
        }
        
        # Execute the task
        result = self.agent.execute("gather information about test topic")
        
        # Check that information was gathered
        mock_gather_information.assert_called_once()
        
        # Check the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["topic"], "test topic")
    
    def test_execute_error(self):
        """Test executing a task that raises an error."""
        # Create a mock method that raises an exception
        def mock_method(*args, **kwargs):
            raise ValueError("Test error")
        
        # Patch the _perform_search method to raise an exception
        with patch.object(self.agent, '_perform_search', mock_method):
            # Execute the task
            result = self.agent.execute("search for test query")
            
            # Check the result
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error"], "Test error")

if __name__ == '__main__':
    unittest.main()