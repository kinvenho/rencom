"""
HTTP client utilities for CLI commands
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import click
from urllib.parse import urljoin


@dataclass
class HTTPResponse:
    """Wrapper for HTTP response data"""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]
    response_time: float


class HTTPClient:
    """HTTP client with connection pooling and error handling"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None
    
    def __enter__(self):
        """Context manager entry"""
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._client:
            self._client.close()
            self._client = None
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPResponse:
        """Make HTTP request with error handling"""
        if not self._client:
            raise RuntimeError("HTTP client not initialized. Use within context manager.")
        
        # Prepare URL
        url = endpoint if endpoint.startswith('http') else f"/{endpoint.lstrip('/')}"
        
        # Prepare headers
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        try:
            import time
            start_time = time.time()
            
            response = self._client.request(
                method=method,
                url=url,
                headers=request_headers,
                json=json_data,
                params=params
            )
            
            response_time = time.time() - start_time
            
            # Parse response data
            try:
                data = response.json() if response.content else {}
            except ValueError:
                # If response is not JSON, store as text
                data = {"message": response.text}
            
            return HTTPResponse(
                status_code=response.status_code,
                data=data,
                headers=dict(response.headers),
                response_time=response_time
            )
            
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds") from e
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}") from e
        except httpx.NetworkError as e:
            raise ConnectionError(f"Network error: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {str(e)}") from e
    
    def get(
        self, 
        endpoint: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPResponse:
        """Make GET request"""
        return self._make_request("GET", endpoint, headers=headers, params=params)
    
    def post(
        self, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """Make POST request"""
        return self._make_request("POST", endpoint, headers=headers, json_data=json_data)
    
    def put(
        self, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """Make PUT request"""
        return self._make_request("PUT", endpoint, headers=headers, json_data=json_data)
    
    def delete(
        self, 
        endpoint: str, 
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """Make DELETE request"""
        return self._make_request("DELETE", endpoint, headers=headers)


def create_client(server_url: str, timeout: int = 30) -> HTTPClient:
    """Factory function to create HTTP client"""
    return HTTPClient(base_url=server_url, timeout=timeout)


def make_authenticated_request(
    client: HTTPClient,
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    **kwargs
) -> HTTPResponse:
    """Make authenticated request with token"""
    headers = kwargs.get('headers', {})
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    kwargs['headers'] = headers
    
    if method.upper() == 'GET':
        return client.get(endpoint, **kwargs)
    elif method.upper() == 'POST':
        return client.post(endpoint, **kwargs)
    elif method.upper() == 'PUT':
        return client.put(endpoint, **kwargs)
    elif method.upper() == 'DELETE':
        return client.delete(endpoint, **kwargs)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


def handle_http_error(response: HTTPResponse, operation: str = "request") -> None:
    """Handle HTTP error responses with user-friendly messages"""
    if response.status_code >= 400:
        error_msg = response.data.get('detail', response.data.get('message', 'Unknown error'))
        
        if response.status_code == 401:
            raise click.ClickException(f"Authentication failed: {error_msg}")
        elif response.status_code == 403:
            raise click.ClickException(f"Permission denied: {error_msg}")
        elif response.status_code == 404:
            raise click.ClickException(f"Resource not found: {error_msg}")
        elif response.status_code == 429:
            raise click.ClickException(f"Rate limit exceeded: {error_msg}")
        elif response.status_code >= 500:
            raise click.ClickException(f"Server error during {operation}: {error_msg}")
        else:
            raise click.ClickException(f"HTTP {response.status_code} error during {operation}: {error_msg}")