"""
Web Agent for Nora.
Handles web browsing, information gathering, and web scraping.
"""

import logging
import os
import json
import time
from typing import Dict, Any, List, Optional
from utils.helpers import generate_unique_id, hash_content
from utils.error_handler import WebBrowsingError, retry

logger = logging.getLogger("nora.agents.web_agent")

class WebAgent:
    """
    Web Agent for Nora.
    Responsible for web browsing, information gathering, and web scraping.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Web Agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.browser = None
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     "data", "cache", "web")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def execute(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a web browsing task.
        
        Args:
            task_description (str): Description of the task to execute
            
        Returns:
            Dict[str, Any]: Task result
        """
        logger.info(f"Web Agent executing task: {task_description}")
        
        try:
            # Determine what kind of web task this is
            if "search" in task_description.lower():
                result = self._perform_search(task_description)
            elif "scrape" in task_description.lower():
                result = self._scrape_website(task_description)
            else:
                # Default to information gathering
                result = self._gather_information(task_description)
            
            return {
                "status": "success",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error in Web Agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            # Close browser if it was opened
            self._close_browser()
    
    def _perform_search(self, query: str) -> Dict[str, Any]:
        """
        Perform a web search.
        
        Args:
            query (str): Search query
            
        Returns:
            Dict[str, Any]: Search results
        """
        # Extract the actual search query from the task description
        search_terms = query.lower().replace("search", "").replace("for", "").strip()
        
        logger.info(f"Performing web search for: {search_terms}")
        
        # Check cache first
        cache_key = f"search_{hash_content(search_terms)}.json"
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cached_results = json.load(f)
                logger.info(f"Returning cached search results for: {search_terms}")
                return cached_results
            except Exception as e:
                logger.warning(f"Error loading cached search results: {str(e)}")
        
        # Perform the search
        results = self._search_with_requests(search_terms)
        
        # Cache the results
        try:
            with open(cache_path, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.warning(f"Error caching search results: {str(e)}")
        
        return results
    
    @retry(max_attempts=3, delay=2, backoff=2, exceptions=(Exception,))
    def _search_with_requests(self, query: str) -> Dict[str, Any]:
        """
        Perform a search using the requests library.
        
        Args:
            query (str): Search query
            
        Returns:
            Dict[str, Any]: Search results
        """
        import requests
        from bs4 import BeautifulSoup
        
        # This is a simplified implementation
        # In a real implementation, this would use a proper search API or more robust scraping
        
        # Encode the query for URL
        encoded_query = requests.utils.quote(query)
        
        # Use DuckDuckGo as it's more scraping-friendly
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise WebBrowsingError(f"Search request failed with status code: {response.status_code}")
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract search results
        results = []
        for result in soup.select(".result"):
            title_elem = result.select_one(".result__title")
            link_elem = result.select_one(".result__url")
            snippet_elem = result.select_one(".result__snippet")
            
            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet
                })
        
        return {
            "query": query,
            "results": results[:10],  # Limit to top 10 results
            "timestamp": time.time()
        }
    
    def _scrape_website(self, task_description: str) -> Dict[str, Any]:
        """
        Scrape a website.
        
        Args:
            task_description (str): Description of the scraping task
            
        Returns:
            Dict[str, Any]: Scraped data
        """
        # Extract URL from task description
        import re
        url_match = re.search(r'https?://[^\s]+', task_description)
        
        if not url_match:
            raise WebBrowsingError("No URL found in task description")
        
        url = url_match.group(0)
        logger.info(f"Scraping website: {url}")
        
        # Check cache first
        cache_key = f"scrape_{hash_content(url)}.json"
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cached_results = json.load(f)
                logger.info(f"Returning cached scraping results for: {url}")
                return cached_results
            except Exception as e:
                logger.warning(f"Error loading cached scraping results: {str(e)}")
        
        # Determine if we need to use Puppeteer or simple requests
        if self.config["web_browsing"]["use_puppeteer"]:
            content = self._scrape_with_puppeteer(url)
        else:
            content = self._scrape_with_requests(url)
        
        # Process the content
        processed_data = self._process_scraped_content(content, url)
        
        # Cache the results
        try:
            with open(cache_path, 'w') as f:
                json.dump(processed_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Error caching scraping results: {str(e)}")
        
        return processed_data
    
    @retry(max_attempts=3, delay=2, backoff=2, exceptions=(Exception,))
    def _scrape_with_requests(self, url: str) -> str:
        """
        Scrape a website using the requests library.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            str: HTML content
        """
        import requests
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise WebBrowsingError(f"Scraping request failed with status code: {response.status_code}")
        
        return response.text
    
    def _scrape_with_puppeteer(self, url: str) -> str:
        """
        Scrape a website using Puppeteer.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            str: HTML content
        """
        # This is a placeholder for the Puppeteer implementation
        # In a real implementation, this would use pyppeteer or a Node.js bridge
        
        logger.warning("Puppeteer scraping not implemented, falling back to requests")
        return self._scrape_with_requests(url)
    
    def _process_scraped_content(self, content: str, url: str) -> Dict[str, Any]:
        """
        Process scraped content.
        
        Args:
            content (str): HTML content
            url (str): Source URL
            
        Returns:
            Dict[str, Any]: Processed data
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "No title"
        
        # Extract main text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Handle relative URLs
            if href.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                href = base_url + href
            
            links.append({
                "url": href,
                "text": text
            })
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            
            # Handle relative URLs
            if src.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                src = base_url + src
            
            images.append({
                "src": src,
                "alt": alt
            })
        
        return {
            "url": url,
            "title": title,
            "text_content": text_content[:10000],  # Limit text content length
            "links": links[:100],  # Limit number of links
            "images": images[:50],  # Limit number of images
            "timestamp": time.time()
        }
    
    def _gather_information(self, topic: str) -> Dict[str, Any]:
        """
        Gather information on a topic.
        
        Args:
            topic (str): Topic to research
            
        Returns:
            Dict[str, Any]: Gathered information
        """
        # Extract the actual topic from the task description
        search_topic = topic.lower().replace("gather information", "").replace("about", "").replace("on", "").strip()
        
        logger.info(f"Gathering information on: {search_topic}")
        
        # First, search for the topic
        search_results = self._perform_search(search_topic)
        
        # Then, scrape the top results
        detailed_info = []
        for result in search_results["results"][:3]:  # Limit to top 3 results
            try:
                url = result["url"]
                scraped_data = self._scrape_website(f"scrape {url}")
                detailed_info.append(scraped_data)
            except Exception as e:
                logger.warning(f"Error scraping result {result['url']}: {str(e)}")
        
        return {
            "topic": search_topic,
            "search_results": search_results,
            "detailed_information": detailed_info,
            "timestamp": time.time()
        }
    
    def _initialize_browser(self):
        """Initialize the browser for web scraping."""
        # This is a placeholder for browser initialization
        # In a real implementation, this would initialize Puppeteer or Selenium
        pass
    
    def _close_browser(self):
        """Close the browser if it's open."""
        if self.browser:
            # Close the browser
            self.browser = None