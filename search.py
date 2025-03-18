import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model # 這個有點小問題
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .config import WebSearchConfig, DEFAULT_CONFIG
from .models import SearchQuery, SearchResponse, Section, WebSearchResult
from .utils import select_and_execute_search, get_search_params
from .prompt import (
    initial_query_system_prompt, 
    initial_query_human_prompt,
    section_generation_system_prompt,
    section_generation_human_prompt,
    section_query_system_prompt,
    section_query_human_prompt
)
import dotenv
dotenv.load_dotenv()
class QueryList(BaseModel):
    """List of search queries."""
    queries: List[str] = Field(..., description="List of search queries")

class SectionList(BaseModel):
    """List of sections for a report."""
    sections: List[Section] = Field(..., description="List of sections")

class WebSearchAgent:
    """Agent that performs multi-step web search and organizes results into sections."""
    
    def __init__(self, config: Optional[WebSearchConfig] = None):
        """Initialize the WebSearchAgent."""
        self.config = config or DEFAULT_CONFIG
        self.llm = self._init_llm()
        
    def _init_llm(self):
        """Initialize the language model based on configuration."""
        if self.config.llm_provider.lower() == "openai":
            return ChatOpenAI(
                model=self.config.planner_model,
                verbose=True
            )
        else:
            raise ValueError(f"LLM provider '{self.config.llm_provider}' not supported. Use 'openai'.")
    
    async def _generate_queries(self, title: str, count: int) -> List[SearchQuery]:
        """Generate search queries based on a title."""
        # Use prompts from prompt.py
        system_prompt = initial_query_system_prompt.format(count=count)
        human_prompt = initial_query_human_prompt.format(title=title)
        
        structured_llm = self.llm.with_structured_output(QueryList)
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        
        return [SearchQuery(query=q) for q in response.queries]
    
    async def _generate_sections(self, title: str, search_responses: List[SearchResponse]) -> List[Section]:
        """Generate sections based on search responses."""
        # Prepare context from search responses
        context = self._format_search_responses(search_responses)
        
        # Use prompts from prompt.py
        system_prompt = section_generation_system_prompt.format(
            max_sections=min(self.config.max_sections, 5),
            title=title
        )
        
        human_prompt = section_generation_human_prompt.format(
            title=title,
            context=context
        )
        
        structured_llm = self.llm.with_structured_output(SectionList)
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        
        # Convert to Section objects
        sections = []
        print(response, response.sections)
        for section_data in response.sections:
            print(section_data)
            section = Section(
                title=section_data.title,
                description=section_data.description,
                search_queries=[],  # 添加空列表
                search_responses=[]  # 添加空列表
            )
            sections.append(section)
            
        return sections
    
    async def _generate_section_queries(self, section: Section, main_title: str) -> List[SearchQuery]:
        """Generate search queries specific to a section."""
        # Use prompts from prompt.py
        system_prompt = section_query_system_prompt.format(
            query_count=self.config.section_queries_count,
            main_title=main_title,
            section_title=section.title,
            section_description=section.description
        )
        
        human_prompt = section_query_human_prompt.format(
            section_title=section.title
        )
        
        structured_llm = self.llm.with_structured_output(QueryList)
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        
        return [SearchQuery(query=q) for q in response.queries]
    
    def _format_search_responses(self, search_responses: List[SearchResponse]) -> str:
        """Format search responses into a readable context string."""
        result = []
        
        for response in search_responses:
            result.append(f"SEARCH QUERY: {response.query}")
            
            for i, res in enumerate(response.results, 1):
                result.append(f"Result {i}:")
                result.append(f"Title: {res.title}")
                result.append(f"URL: {res.url}")
                result.append(f"Content: {res.content}")
                result.append("")
            
            result.append("-" * 40)
            
        return "\n".join(result)
    
    async def search(self, title: str) -> WebSearchResult:
        """Execute the full search process for a given title."""
        # Implementation remains the same as before
        search_api = self.config.search_api
        search_params = get_search_params(search_api, self.config.search_api_config)
        
        # Step 1: Generate initial queries
        print(f"Generating initial queries for: {title}")
        initial_queries = await self._generate_queries(title, self.config.initial_queries_count)
        
        # Step 2: Execute initial searches
        print(f"Executing {len(initial_queries)} initial searches...")
        query_strings = [q.query for q in initial_queries]
        initial_responses = await select_and_execute_search(search_api, query_strings, search_params)
        
        # Step 3: Generate sections based on search results
        print("Generating sections based on initial search results...")
        sections = await self._generate_sections(title, initial_responses)
        print(f"Generated {len(sections)} sections")
        
        # Step 4: For each section, generate and execute specific searches
        for i, section in enumerate(sections):
            print(f"Processing section {i+1}/{len(sections)}: {section.title}")
            
            # Generate section-specific queries
            section_queries = await self._generate_section_queries(section, title)
            section.search_queries = section_queries
            
            # Execute searches for this section
            query_strings = [q.query for q in section_queries]
            section_responses = await select_and_execute_search(search_api, query_strings, search_params)
            section.search_responses = section_responses
        
        # Step 5: Return the complete WebSearchResult
        return WebSearchResult(
            title=title,
            initial_queries=initial_queries,
            initial_responses=initial_responses,
            sections=sections
        )

# Simple example usage - remains the same
async def main():
    # Code remains the same as before
    
    
    config = WebSearchConfig(
        llm_provider="openai",
        planner_model="o1",
        search_api="tavily",
        search_api_config={"include_raw_content": True, "max_results": 3},
        initial_queries_count=2,
        section_queries_count=2,
        max_sections=4
    )
    
    agent = WebSearchAgent(config)
    result = await agent.search("Advances in quantum computing algorithms")
    
    print(f"\nSearch results for: {result.title}")
    print(f"Initial queries: {[q.query for q in result.initial_queries]}")
    print("\nSections:")
    for i, section in enumerate(result.sections, 1):
        print(f"{i}. {section.title}")
        print(f"   Description: {section.description}")
        print(f"   Queries: {[q.query for q in section.search_queries]}")
        # print search responses
        print(f"   Found {section.search_responses} results")
        print(f"   Found {sum(len(r.results) for r in section.search_responses)} results")
    
if __name__ == "__main__":
    asyncio.run(main())