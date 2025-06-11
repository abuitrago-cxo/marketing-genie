"""
Search Utilities for Multi-Agent System

This module provides web search capabilities and content extraction
utilities for the research agent and other components.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import re
from datetime import datetime


async def perform_web_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Perform web search using multiple search engines
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, url, snippet
    """
    
    # Try multiple search approaches
    results = []
    
    # Try DuckDuckGo first (no API key required)
    try:
        ddg_results = await search_duckduckgo(query, max_results)
        results.extend(ddg_results)
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
    
    # Try Bing if available
    try:
        bing_results = await search_bing(query, max_results)
        results.extend(bing_results)
    except Exception as e:
        print(f"Bing search failed: {e}")
    
    # Remove duplicates and limit results
    unique_results = remove_duplicate_urls(results)
    return unique_results[:max_results]


async def search_duckduckgo(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search using DuckDuckGo instant answer API
    
    Args:
        query: Search query
        max_results: Maximum results to return
        
    Returns:
        List of search results
    """
    
    results = []
    
    try:
        # DuckDuckGo instant answer API
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract results from different sections
                    if data.get('AbstractText'):
                        results.append({
                            'title': data.get('AbstractSource', 'DuckDuckGo'),
                            'url': data.get('AbstractURL', ''),
                            'snippet': data.get('AbstractText', ''),
                            'source': 'duckduckgo'
                        })
                    
                    # Related topics
                    for topic in data.get('RelatedTopics', [])[:3]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            results.append({
                                'title': topic.get('Text', '')[:100],
                                'url': topic.get('FirstURL', ''),
                                'snippet': topic.get('Text', ''),
                                'source': 'duckduckgo'
                            })
    
    except Exception as e:
        print(f"DuckDuckGo API error: {e}")
    
    # If API doesn't provide enough results, try scraping (carefully)
    if len(results) < 3:
        try:
            scrape_results = await scrape_duckduckgo_results(query, max_results - len(results))
            results.extend(scrape_results)
        except Exception as e:
            print(f"DuckDuckGo scraping failed: {e}")
    
    return results


async def scrape_duckduckgo_results(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Scrape DuckDuckGo search results (fallback method)
    
    Args:
        query: Search query
        max_results: Maximum results to return
        
    Returns:
        List of search results
    """
    
    results = []
    
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find search result elements
                    result_elements = soup.find_all('div', class_='result')
                    
                    for element in result_elements[:max_results]:
                        try:
                            title_elem = element.find('a', class_='result__a')
                            snippet_elem = element.find('a', class_='result__snippet')
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                url = title_elem.get('href', '')
                                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                                
                                if title and url:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'snippet': snippet,
                                        'source': 'duckduckgo_scrape'
                                    })
                        except Exception as e:
                            print(f"Error parsing result element: {e}")
                            continue
    
    except Exception as e:
        print(f"DuckDuckGo scraping error: {e}")
    
    return results


async def search_bing(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search using Bing Web Search API (if API key available)
    
    Args:
        query: Search query
        max_results: Maximum results to return
        
    Returns:
        List of search results
    """
    
    import os
    
    api_key = os.getenv('BING_SEARCH_API_KEY')
    if not api_key:
        return []
    
    results = []
    
    try:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            'Ocp-Apim-Subscription-Key': api_key,
            'Content-Type': 'application/json'
        }
        params = {
            'q': query,
            'count': max_results,
            'responseFilter': 'Webpages'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('webPages', {}).get('value', []):
                        results.append({
                            'title': item.get('name', ''),
                            'url': item.get('url', ''),
                            'snippet': item.get('snippet', ''),
                            'source': 'bing'
                        })
    
    except Exception as e:
        print(f"Bing search error: {e}")
    
    return results


async def extract_content_from_urls(urls: List[str]) -> List[str]:
    """
    Extract text content from web pages
    
    Args:
        urls: List of URLs to extract content from
        
    Returns:
        List of extracted text content
    """
    
    contents = []
    
    for url in urls:
        try:
            content = await extract_single_url_content(url)
            if content:
                contents.append(content)
        except Exception as e:
            print(f"Failed to extract content from {url}: {e}")
            contents.append("")
    
    return contents


async def extract_single_url_content(url: str) -> str:
    """
    Extract text content from a single URL
    
    Args:
        url: URL to extract content from
        
    Returns:
        Extracted text content
    """
    
    if not url or not url.startswith(('http://', 'https://')):
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    return extract_text_from_html(html)
    
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
    
    return ""


def extract_text_from_html(html: str) -> str:
    """
    Extract clean text from HTML content
    
    Args:
        html: HTML content string
        
    Returns:
        Clean text content
    """
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit text length
        return text[:3000]  # Limit to 3000 characters
    
    except Exception as e:
        print(f"Error extracting text from HTML: {e}")
        return ""


def remove_duplicate_urls(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate URLs from search results
    
    Args:
        results: List of search results
        
    Returns:
        List with duplicates removed
    """
    
    seen_urls = set()
    unique_results = []
    
    for result in results:
        url = result.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    
    return unique_results


def clean_search_query(query: str) -> str:
    """
    Clean and optimize search query
    
    Args:
        query: Raw search query
        
    Returns:
        Cleaned search query
    """
    
    # Remove special characters that might interfere with search
    query = re.sub(r'[^\w\s\-\+\"\']', ' ', query)
    
    # Normalize whitespace
    query = ' '.join(query.split())
    
    # Limit length
    if len(query) > 200:
        query = query[:200]
    
    return query.strip()


async def search_academic_sources(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search academic and scholarly sources
    
    Args:
        query: Search query
        max_results: Maximum results to return
        
    Returns:
        List of academic search results
    """
    
    results = []
    
    # Search arXiv for academic papers
    try:
        arxiv_results = await search_arxiv(query, max_results // 2)
        results.extend(arxiv_results)
    except Exception as e:
        print(f"arXiv search failed: {e}")
    
    # Search Google Scholar (limited without API)
    try:
        scholar_results = await search_google_scholar(query, max_results // 2)
        results.extend(scholar_results)
    except Exception as e:
        print(f"Google Scholar search failed: {e}")
    
    return results


async def search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search arXiv for academic papers
    
    Args:
        query: Search query
        max_results: Maximum results to return
        
    Returns:
        List of arXiv search results
    """
    
    results = []
    
    try:
        # arXiv API
        url = f"http://export.arxiv.org/api/query?search_query=all:{quote_plus(query)}&start=0&max_results={max_results}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    
                    # Parse XML (simplified)
                    # In a real implementation, you'd use proper XML parsing
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(xml_content)
                    
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                        summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                        id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                        
                        if title_elem is not None and id_elem is not None:
                            results.append({
                                'title': title_elem.text.strip(),
                                'url': id_elem.text.strip(),
                                'snippet': summary_elem.text.strip() if summary_elem is not None else '',
                                'source': 'arxiv'
                            })
    
    except Exception as e:
        print(f"arXiv search error: {e}")
    
    return results


async def search_google_scholar(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search Google Scholar (limited functionality without API)
    
    Args:
        query: Search query
        max_results: Maximum results to return
        
    Returns:
        List of Google Scholar results
    """
    
    # Note: Google Scholar doesn't have a public API
    # This is a placeholder for potential future implementation
    # In practice, you might use services like Semantic Scholar API
    
    return []


def calculate_search_relevance(result: Dict[str, Any], query: str) -> float:
    """
    Calculate relevance score for a search result
    
    Args:
        result: Search result dictionary
        query: Original search query
        
    Returns:
        Relevance score between 0 and 1
    """
    
    title = result.get('title', '').lower()
    snippet = result.get('snippet', '').lower()
    query_terms = query.lower().split()
    
    if not query_terms:
        return 0.5
    
    score = 0.0
    total_terms = len(query_terms)
    
    # Title relevance (weighted more heavily)
    title_matches = sum(1 for term in query_terms if term in title)
    score += (title_matches / total_terms) * 0.6
    
    # Snippet relevance
    snippet_matches = sum(1 for term in query_terms if term in snippet)
    score += (snippet_matches / total_terms) * 0.4
    
    return min(score, 1.0)


def rank_search_results(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Rank search results by relevance
    
    Args:
        results: List of search results
        query: Original search query
        
    Returns:
        Ranked list of search results
    """
    
    # Calculate relevance scores
    for result in results:
        result['relevance_score'] = calculate_search_relevance(result, query)
    
    # Sort by relevance score (descending)
    ranked_results = sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return ranked_results


async def get_search_suggestions(query: str) -> List[str]:
    """
    Get search suggestions for query expansion
    
    Args:
        query: Original search query
        
    Returns:
        List of suggested search queries
    """
    
    suggestions = []
    
    # Generate variations of the query
    base_terms = query.split()
    
    if len(base_terms) > 1:
        # Add individual terms
        suggestions.extend(base_terms)
        
        # Add combinations
        for i in range(len(base_terms)):
            for j in range(i + 2, len(base_terms) + 1):
                suggestions.append(' '.join(base_terms[i:j]))
    
    # Add common modifiers
    modifiers = ['how to', 'what is', 'best practices', 'tutorial', 'guide', 'examples']
    for modifier in modifiers:
        suggestions.append(f"{modifier} {query}")
    
    # Remove duplicates and limit
    unique_suggestions = list(set(suggestions))
    return unique_suggestions[:10]
