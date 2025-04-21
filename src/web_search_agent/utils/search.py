import asyncio
import os
from typing import Any, Dict, List, Optional

import requests

from ..models import SearchResponse, SearchResult

# Try importing search libraries, provide graceful fallbacks
try:
    from tavily import AsyncTavilyClient
except ImportError:
    print("Tavily not installed. Use 'pip install tavily-python' to enable.")
    AsyncTavilyClient = None

try:
    from exa_py import Exa
except ImportError:
    print("Exa not installed. Use 'pip install exa-py' to enable.")
    Exa = None


def get_search_params(
    search_api: str, search_api_config: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Extract valid parameters for a search API from a configuration dictionary."""
    params_to_pass = {}

    if not search_api_config:
        return params_to_pass

    if search_api == "exa":
        # Exa supports: max_characters, num_results, include_domains, exclude_domains, subpages
        valid_params = [
            "max_characters",
            "num_results",
            "include_domains",
            "exclude_domains",
            "subpages",
        ]
        for param in valid_params:
            if param in search_api_config:
                params_to_pass[param] = search_api_config[param]

    elif search_api == "tavily":
        # Tavily supports: max_results, search_depth, include_domains, exclude_domains, include_raw_content
        valid_params = [
            "max_results",
            "search_depth",
            "include_domains",
            "exclude_domains",
            "include_raw_content",
        ]
        for param in valid_params:
            if param in search_api_config:
                params_to_pass[param] = search_api_config[param]

    elif search_api == "perplexity":
        # Perplexity supports: max_results
        if "max_results" in search_api_config:
            params_to_pass["max_results"] = search_api_config["max_results"]

    return params_to_pass


def normalize_search_results(
    search_responses: List[Dict[str, Any]],
) -> List[SearchResponse]:
    """Normalize search responses from different APIs into a common format."""
    normalized_responses = []

    for response in search_responses:
        # Extract the query and results
        query = response.get("query", "")
        raw_results = response.get("results", [])

        # Normalize each result
        results = []
        for result in raw_results:
            search_result = SearchResult(
                title=result.get("title", "No title"),
                url=result.get("url", ""),
                content=result.get("content", ""),
                score=result.get("score", 1.0),
                raw_content=result.get("raw_content"),
            )
            results.append(search_result)

        # Create normalized response
        normalized_response = SearchResponse(query=query, results=results)
        normalized_responses.append(normalized_response)

    return normalized_responses


async def tavily_search_async(
    search_queries: List[str], **kwargs
) -> List[Dict[str, Any]]:
    """Perform concurrent web searches using the Tavily API."""
    if not AsyncTavilyClient:
        raise ImportError(
            "Tavily client not installed. Install with 'pip install tavily-python'"
        )

    tavily_async_client = AsyncTavilyClient()
    search_tasks = []

    # Set default parameters
    max_results = kwargs.get("max_results", 5)
    include_raw_content = kwargs.get("include_raw_content", True)
    search_depth = kwargs.get("search_depth", "basic")
    include_domains = kwargs.get("include_domains", None)
    exclude_domains = kwargs.get("exclude_domains", None)

    for query in search_queries:
        search_tasks.append(
            tavily_async_client.search(
                query,
                max_results=max_results,
                include_raw_content=include_raw_content,
                search_depth=search_depth,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                topic="general",
            )
        )

    # Execute all searches concurrently
    search_docs = await asyncio.gather(*search_tasks)
    return search_docs


def perplexity_search(search_queries: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Search the web using the Perplexity API."""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }

    # Set default parameters
    max_results = kwargs.get("max_results", 5)

    search_results = []

    for query in search_queries:
        url = "https://api.perplexity.ai/search"
        payload = {"query": query, "max_results": max_results}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": (
                        item.get("snippets", [""])[0] if item.get("snippets") else ""
                    ),
                    "score": 1.0,
                    "raw_content": None,
                }
                results.append(result)

            search_results.append({"query": query, "results": results})

        except Exception as e:
            print(f"Error in Perplexity search for query '{query}': {str(e)}")
            search_results.append({"query": query, "results": []})

    return search_results


async def exa_search(search_queries: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Search the web using the Exa API."""
    if not Exa:
        raise ImportError("Exa not installed. Install with 'pip install exa-py'")

    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY environment variable not set")

    exa_client = Exa(api_key=api_key)

    # Set default parameters
    num_results = kwargs.get("num_results", 5)
    include_domains = kwargs.get("include_domains")
    exclude_domains = kwargs.get("exclude_domains")
    max_characters = kwargs.get("max_characters")

    search_results = []

    for query in search_queries:
        try:
            # Configure parameters
            search_params = {"num_results": num_results}

            if include_domains:
                search_params["include_domains"] = include_domains
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains
            if max_characters:
                search_params["text"] = {"max_characters": max_characters}

            # Execute search
            response = exa_client.search(query, **search_params)

            results = []
            for result in response.results:
                results.append(
                    {
                        "title": result.title,
                        "url": result.url,
                        "content": result.text,
                        "score": 1.0,
                        "raw_content": result.text,
                    }
                )

            search_results.append({"query": query, "results": results})

            # Respect rate limits
            await asyncio.sleep(0.25)

        except Exception as e:
            print(f"Error in Exa search for query '{query}': {str(e)}")
            search_results.append({"query": query, "results": []})

    return search_results


async def select_and_execute_search(
    search_api: str, query_list: List[str], params: Dict[str, Any]
) -> List[SearchResponse]:
    """Select and execute the appropriate search API based on configuration.

    Args:
        search_api: Name of the search API to use
        query_list: List of search queries to execute
        params: Parameters to pass to the search API

    Returns:
        List of normalized search responses

    Raises:
        ValueError: If an unsupported search API is specified
    """
    if search_api == "tavily":
        search_results = await tavily_search_async(query_list, **params)
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list, **params)
    elif search_api == "exa":
        search_results = await exa_search(query_list, **params)
    else:
        raise ValueError(f"Unsupported search API: {search_api}")

    # Normalize the results into our standard format
    return normalize_search_results(search_results)
