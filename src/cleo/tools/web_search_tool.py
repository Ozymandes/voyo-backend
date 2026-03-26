"""
Web Search Tool for CLEO
Current events and latest information
"""

import requests
from typing import List, Dict
import os
import logging

logger = logging.getLogger(__name__)

class WebSearchTool:
    """Search web for current information"""

    def __init__(self):
        """Initialize web search tool"""
        self.api_key = os.getenv("SEARCH_API_KEY", "")
        self.provider = os.getenv("SEARCH_PROVIDER", "tavily")

        if self.api_key:
            logger.info(f"Web search tool initialized with {self.provider}")
        else:
            logger.warning("SEARCH_API_KEY not found - web search disabled")

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search the web

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search result dictionaries
        """
        if not self.api_key:
            return [{"error": "Search API not configured"}]

        if self.provider == "tavily":
            return self._tavily_search(query, num_results)

        logger.warning(f"Unknown search provider: {self.provider}")
        return [{"error": f"Unknown search provider: {self.provider}"}]

    def _tavily_search(self, query: str, num_results: int) -> List[Dict]:
        """
        Search using Tavily API

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of search results
        """
        try:
            url = "https://api.tavily.com/search"
            params = {
                "api_key": self.api_key,
                "query": query,
                "max_results": num_results,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False
            }

            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            return [
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", "")
                }
                for result in data.get("results", [])
            ]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error in Tavily search: {e}")
            return [{"error": str(e)}]
        except Exception as e:
            logger.error(f"Unexpected error in web search: {e}")
            return [{"error": str(e)}]

    def find_current_events(self, location: str, dates: str = None) -> List[Dict]:
        """
        Find current events in location

        Args:
            location: Location name
            dates: Optional date range

        Returns:
            List of event information
        """
        query = f"events {location} Egypt 2024"
        if dates:
            query += f" {dates}"

        return self.search(query, num_results=5)

    def search_news(self, query: str) -> List[Dict]:
        """
        Search news articles

        Args:
            query: News search query

        Returns:
            List of news results
        """
        if not self.api_key:
            return [{"error": "Search API not configured"}]

        try:
            url = "https://api.tavily.com/search"
            params = {
                "api_key": self.api_key,
                "query": query,
                "max_results": 5,
                "search_depth": "basic",
                "topic": "news"
            }

            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            return [
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", ""),
                    "date": result.get("publishedDate", "")
                }
                for result in data.get("results", [])
            ]

        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return [{"error": str(e)}]
