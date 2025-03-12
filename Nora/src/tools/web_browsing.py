"""
Web browsing tools for Nora.
Handles web browsing, information gathering, and web scraping.
"""

import logging
import os
import json
import time
import requests
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from utils.helpers import hash_content
from utils.error_handler import WebBrowsingError, retry

logger = logging.getLogger("nora.tools.web_browsing")

class WebBrowser:
    """
    Web browser tool for Nora.
    Provides methods for web browsing, searching, and scraping.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the web browser tool.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     "data", "cache", "web")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Set up headers for requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    @retry(max_attempts=3, delay=2, backoff=2, exceptions=(Exception,))
    def search(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Perform a web search.
        
        Args:
            query (str): Search query
            use_cache (bool): Whether to use cached results
            
        Returns:
            Dict[str, Any]: Search results
        """
        logger.info(f"Performing web search for: {query}")
        
        # Check cache first if enabled
        if use_cache:
            cache_key = f"search_{hash_content(query)}.json"
            cache_path = os.path.join(self.cache_dir, cache_key)
            
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r') as f:
                        cached_results = json.load(f)
                    logger.info(f"Returning cached search results for: {query}")
                    return cached_results
                except Exception as e:
                    logger.warning(f"Error loading cached search results: {str(e)}")
        
        # Encode the query for URL
        encoded_query = requests.utils.quote(query)
        
        # Use DuckDuckGo as it's more scraping-friendly
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        response = requests.get(url, headers=self.headers)
        
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
        
        search_results = {
            "query": query,
            "results": results[:10],  # Limit to top 10 results
            "timestamp": time.time()
        }
        
        # Cache the results if enabled
        if use_cache:
            try:
                with open(cache_path, 'w') as f:
                    json.dump(search_results, f, indent=2)
            except Exception as e:
                logger.warning(f"Error caching search results: {str(e)}")
        
        return search_results
    
    @retry(max_attempts=3, delay=2, backoff=2, exceptions=(Exception,))
    def scrape(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Scrape a website.
        
        Args:
            url (str): URL to scrape
            use_cache (bool): Whether to use cached results
            
        Returns:
            Dict[str, Any]: Scraped data
        """
        logger.info(f"Scraping website: {url}")
        
        # Check cache first if enabled
        if use_cache:
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
        
        # Fetch the page
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise WebBrowsingError(f"Scraping request failed with status code: {response.status_code}")
        
        # Process the content
        processed_data = self._process_html_content(response.text, url)
        
        # Cache the results if enabled
        if use_cache:
            try:
                with open(cache_path, 'w') as f:
                    json.dump(processed_data, f, indent=2)
            except Exception as e:
                logger.warning(f"Error caching scraping results: {str(e)}")
        
        return processed_data
    
    def _process_html_content(self, content: str, url: str) -> Dict[str, Any]:
        """
        Process HTML content.
        
        Args:
            content (str): HTML content
            url (str): Source URL
            
        Returns:
            Dict[str, Any]: Processed data
        """
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
        
        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            
            if name and content:
                meta_tags[name] = content
        
        return {
            "url": url,
            "title": title,
            "meta_tags": meta_tags,
            "text_content": text_content[:10000],  # Limit text content length
            "links": links[:100],  # Limit number of links
            "images": images[:50],  # Limit number of images
            "timestamp": time.time()
        }
    
    def gather_information(self, topic: str) -> Dict[str, Any]:
        """
        Gather information on a topic.
        
        Args:
            topic (str): Topic to research
            
        Returns:
            Dict[str, Any]: Gathered information
        """
        logger.info(f"Gathering information on: {topic}")
        
        # First, search for the topic
        search_results = self.search(topic)
        
        # Then, scrape the top results
        detailed_info = []
        for result in search_results["results"][:3]:  # Limit to top 3 results
            try:
                url = result["url"]
                scraped_data = self.scrape(url)
                detailed_info.append(scraped_data)
            except Exception as e:
                logger.warning(f"Error scraping result {result['url']}: {str(e)}")
        
        return {
            "topic": topic,
            "search_results": search_results,
            "detailed_information": detailed_info,
            "timestamp": time.time()
        }