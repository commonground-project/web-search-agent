from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    """Represents a search query to be sent to a search API."""
    query: str = Field(..., description="The search query text")

class SearchResult(BaseModel):
    """Represents a single search result from a search API."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    content: str = Field(..., description="Content snippet or summary")
    score: float = Field(..., description="Relevance score (if available)")
    raw_content: Optional[str] = Field(None, description="Full content if available")

class SearchResponse(BaseModel):
    """Represents the response from a search API for a single query."""
    query: str = Field(..., description="The original search query")
    results: List[SearchResult] = Field(default_list=[], description="List of search results")

class Section(BaseModel):
    """Represents a section/subtopic of the main search topic."""
    title: str = Field(..., description="Title of the section")
    description: str = Field(..., description="Description of the section")
    search_queries: List[SearchQuery] = Field(default_list=[], description="Search queries for this section")
    search_responses: List[SearchResponse] = Field(default_list=[], description="Search responses for this section")

class WebSearchResult(BaseModel):
    """Final result structure returned by WebSearchAgent."""
    title: str = Field(..., description="Original search title/topic")
    initial_queries: List[SearchQuery] = Field(default_list=[], description="Initial search queries")
    initial_responses: List[SearchResponse] = Field(default_list=[], description="Initial search responses")
    sections: List[Section] = Field(default_list=[], description="Generated sections with their search results")