"""Web Search Agent - A modular web search and analysis tool."""

__version__ = "0.1.0"

from .agent import WebSearchAgent
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
    "process_title",
    "process_all_titles",
]
