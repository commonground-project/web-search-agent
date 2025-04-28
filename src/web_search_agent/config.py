"""Configuration for WebSearchAgent."""

from typing import Any, Dict, Optional

from .prompts import must_cover_section_prompt


class WebSearchConfig:
    """Configuration for WebSearchAgent."""

    def __init__(
        self,
        # LLM Configuration
        llm_provider: str = "openai",
        planner_model: str = "o1",
        # Search Configuration
        search_api: str = "tavily",
        search_api_config: Optional[Dict[str, Any]] = None,
        # Query Generation
        initial_queries_count: int = 3,
        section_queries_count: int = 2,
        # Control Parameters
        max_sections: int = 5,
        # Must cover section title prompt
        must_cover_section_title: str = must_cover_section_prompt,
    ):
        """Initialize WebSearchAgent configuration.

        Args:
            llm_provider: Provider for LLM (together, openai, anthropic, etc.)
            planner_model: Model name for planning and query generation
            search_api: Search API to use (tavily, perplexity, exa, etc.)
            search_api_config: Additional configuration for search API
            initial_queries_count: Number of initial search queries to generate
            section_queries_count: Number of search queries per section
            max_sections: Maximum number of sections to generate
            must_cover_section_title: Prompt for must-cover sections
        """
        self.llm_provider = llm_provider
        self.planner_model = planner_model
        self.search_api = search_api
        self.search_api_config = search_api_config or {
            "include_raw_content": True,
            "max_results": 3,
        }
        self.initial_queries_count = initial_queries_count
        self.section_queries_count = section_queries_count
        self.max_sections = max_sections
        self.must_cover_section_title = must_cover_section_title


DEFAULT_CONFIG = WebSearchConfig()
