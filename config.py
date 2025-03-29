from typing import Dict, Any, Optional, List

class WebSearchConfig:
    """Configuration for WebSearchAgent"""
    
    def __init__(
        self,
        # LLM Configuration
        llm_provider: str = "openai",
        planner_model: str = "o1",
        
        # Search Configuration
        search_api: str = "tavily",
        search_api_config: Optional[Dict[str, Any]] = {"include_raw_content": True, "max_results": 3},
        
        # Query Generation
        initial_queries_count: int = 3,
        section_queries_count: int = 2,
        
        # Control Parameters
        max_sections: int = 5,
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
            include_raw_content: Whether to include raw content in search results
        """
        self.llm_provider = llm_provider
        self.planner_model = planner_model
        self.search_api = search_api
        self.search_api_config = search_api_config or {}
        self.initial_queries_count = initial_queries_count
        self.section_queries_count = section_queries_count
        self.max_sections = max_sections
# Default configuration
DEFAULT_CONFIG = WebSearchConfig()