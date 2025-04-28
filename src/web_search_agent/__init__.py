"""Web Search Agent - A modular web search and analysis tool."""

from .agent import WebSearchAgent, search_multiple_topics, search_topic
from .config import WebSearchConfig
from .models import (
    SearchQuery,
    SearchResponse,
    Section,
    WebSearchResult,
)

# 定義公開 API
__all__ = [
    "WebSearchAgent",
    "WebSearchConfig",
    "SearchQuery",
    "SearchResponse",
    "Section",
    "WebSearchResult",
    "search_topic",
    "search_multiple_topics",
]
