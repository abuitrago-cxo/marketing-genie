"""
Web Operations Tool

Provides advanced web operations including API calls, web scraping,
and external service integrations.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from .base import BaseTool, ToolResult, ToolCapability, ToolError
import logging

logger = logging.getLogger(__name__)


class WebOperationsTool(BaseTool):
    """
    Tool for web operations and API integrations.
    
    Provides HTTP requests, API calls, and web data extraction capabilities.
    """
    
    def __init__(self):
        super().__init__(
            name="web_operations",
            description="Advanced web operations including HTTP requests, API calls, and data extraction",
            category="web"
        )
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'AI-Agent-Assistant/1.0'
                }
            )
        return self.session
    
    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability(
                name="http_request",
                description="Make HTTP requests to web APIs",
                parameters={
                    "required": ["url", "method"],
                    "optional": ["headers", "data", "params", "timeout"],
                    "url": "Target URL for the request",
                    "method": "HTTP method (GET, POST, PUT, DELETE, etc.)",
                    "headers": "Request headers as dictionary",
                    "data": "Request body data",
                    "params": "URL parameters as dictionary",
                    "timeout": "Request timeout in seconds"
                },
                examples=["http_request('https://api.example.com/data', 'GET')"],
                category="http"
            ),
            ToolCapability(
                name="fetch_webpage",
                description="Fetch and extract content from a webpage",
                parameters={
                    "required": ["url"],
                    "optional": ["extract_text", "extract_links", "extract_images"],
                    "url": "URL of the webpage to fetch",
                    "extract_text": "Extract text content from the page",
                    "extract_links": "Extract all links from the page",
                    "extract_images": "Extract image URLs from the page"
                },
                examples=["fetch_webpage('https://example.com', extract_text=True)"],
                category="scraping"
            ),
            ToolCapability(
                name="check_url_status",
                description="Check the status and availability of a URL",
                parameters={
                    "required": ["url"],
                    "optional": ["follow_redirects"],
                    "url": "URL to check",
                    "follow_redirects": "Whether to follow redirects"
                },
                examples=["check_url_status('https://example.com')"],
                category="monitoring"
            ),
            ToolCapability(
                name="download_file",
                description="Download a file from a URL",
                parameters={
                    "required": ["url", "destination"],
                    "optional": ["chunk_size", "max_size"],
                    "url": "URL of the file to download",
                    "destination": "Local path to save the file",
                    "chunk_size": "Download chunk size in bytes",
                    "max_size": "Maximum file size to download in bytes"
                },
                examples=["download_file('https://example.com/file.pdf', './downloads/file.pdf')"],
                category="download"
            )
        ]
    
    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute web operation"""
        try:
            if action == "http_request":
                return await self._http_request(parameters)
            elif action == "fetch_webpage":
                return await self._fetch_webpage(parameters)
            elif action == "check_url_status":
                return await self._check_url_status(parameters)
            elif action == "download_file":
                return await self._download_file(parameters)
            else:
                raise ToolError(f"Unknown action: {action}", tool_name=self.name)
                
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Web operation failed: {str(e)}", tool_name=self.name)
    
    async def _http_request(self, parameters: Dict[str, Any]) -> ToolResult:
        """Make HTTP request"""
        url = parameters["url"]
        method = parameters["method"].upper()
        headers = parameters.get("headers", {})
        data = parameters.get("data")
        params = parameters.get("params", {})
        timeout = parameters.get("timeout", 30)
        
        session = await self._get_session()
        
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                
                # Get response data
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                result_data = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "content_type": content_type,
                    "data": response_data,
                    "url": str(response.url)
                }
                
                return ToolResult(
                    success=response.status < 400,
                    data=result_data,
                    message=f"HTTP {method} request to {url} completed with status {response.status}"
                )
                
        except asyncio.TimeoutError:
            raise ToolError(f"Request to {url} timed out after {timeout} seconds", tool_name=self.name)
        except aiohttp.ClientError as e:
            raise ToolError(f"HTTP request failed: {str(e)}", tool_name=self.name)
    
    async def _fetch_webpage(self, parameters: Dict[str, Any]) -> ToolResult:
        """Fetch and extract webpage content"""
        url = parameters["url"]
        extract_text = parameters.get("extract_text", True)
        extract_links = parameters.get("extract_links", False)
        extract_images = parameters.get("extract_images", False)
        
        session = await self._get_session()
        
        try:
            async with session.get(url) as response:
                if response.status >= 400:
                    raise ToolError(f"Failed to fetch webpage: HTTP {response.status}", tool_name=self.name)
                
                html_content = await response.text()
                
                result_data = {
                    "url": url,
                    "status_code": response.status,
                    "content_length": len(html_content)
                }
                
                # Basic text extraction (would use BeautifulSoup in production)
                if extract_text:
                    # Simple text extraction - remove HTML tags
                    import re
                    text_content = re.sub(r'<[^>]+>', '', html_content)
                    text_content = re.sub(r'\s+', ' ', text_content).strip()
                    result_data["text_content"] = text_content[:5000]  # Limit text length
                
                # Basic link extraction
                if extract_links:
                    import re
                    links = re.findall(r'href=[\'"]?([^\'" >]+)', html_content)
                    # Convert relative URLs to absolute
                    absolute_links = []
                    for link in links[:50]:  # Limit number of links
                        if link.startswith('http'):
                            absolute_links.append(link)
                        else:
                            absolute_links.append(urljoin(url, link))
                    result_data["links"] = absolute_links
                
                # Basic image extraction
                if extract_images:
                    import re
                    images = re.findall(r'src=[\'"]?([^\'" >]+)', html_content)
                    # Convert relative URLs to absolute
                    absolute_images = []
                    for img in images[:20]:  # Limit number of images
                        if img.startswith('http'):
                            absolute_images.append(img)
                        else:
                            absolute_images.append(urljoin(url, img))
                    result_data["images"] = absolute_images
                
                return ToolResult(
                    success=True,
                    data=result_data,
                    message=f"Successfully fetched webpage content from {url}"
                )
                
        except aiohttp.ClientError as e:
            raise ToolError(f"Failed to fetch webpage: {str(e)}", tool_name=self.name)
    
    async def _check_url_status(self, parameters: Dict[str, Any]) -> ToolResult:
        """Check URL status"""
        url = parameters["url"]
        follow_redirects = parameters.get("follow_redirects", True)
        
        session = await self._get_session()
        
        try:
            async with session.head(url, allow_redirects=follow_redirects) as response:
                result_data = {
                    "url": url,
                    "status_code": response.status,
                    "final_url": str(response.url),
                    "headers": dict(response.headers),
                    "is_accessible": response.status < 400,
                    "content_type": response.headers.get('content-type', ''),
                    "content_length": response.headers.get('content-length')
                }
                
                return ToolResult(
                    success=True,
                    data=result_data,
                    message=f"URL {url} status check completed: {response.status}"
                )
                
        except aiohttp.ClientError as e:
            return ToolResult(
                success=False,
                data={"url": url, "error": str(e)},
                message=f"Failed to check URL {url}: {str(e)}"
            )
    
    async def _download_file(self, parameters: Dict[str, Any]) -> ToolResult:
        """Download file from URL"""
        url = parameters["url"]
        destination = parameters["destination"]
        chunk_size = parameters.get("chunk_size", 8192)
        max_size = parameters.get("max_size", 100 * 1024 * 1024)  # 100MB default
        
        session = await self._get_session()
        
        try:
            async with session.get(url) as response:
                if response.status >= 400:
                    raise ToolError(f"Failed to download file: HTTP {response.status}", tool_name=self.name)
                
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > max_size:
                    raise ToolError(f"File too large: {content_length} bytes (max: {max_size})", tool_name=self.name)
                
                downloaded_size = 0
                
                with open(destination, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        downloaded_size += len(chunk)
                        if downloaded_size > max_size:
                            raise ToolError(f"File too large: exceeded {max_size} bytes", tool_name=self.name)
                        f.write(chunk)
                
                return ToolResult(
                    success=True,
                    data={
                        "url": url,
                        "destination": destination,
                        "size": downloaded_size,
                        "content_type": response.headers.get('content-type', '')
                    },
                    message=f"Successfully downloaded file from {url} to {destination}"
                )
                
        except aiohttp.ClientError as e:
            raise ToolError(f"Failed to download file: {str(e)}", tool_name=self.name)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and not self.session.closed:
            await self.session.close()
