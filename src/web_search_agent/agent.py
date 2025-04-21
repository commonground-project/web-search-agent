import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .config import DEFAULT_CONFIG, WebSearchConfig
from .models import (
    QueryList,
    SearchQuery,
    SearchResponse,
    Section,
    SectionList,
    WebSearchResult,
)
from .prompts import (
    initial_query_human_prompt,
    initial_query_system_prompt,
    section_generation_human_prompt,
    section_generation_system_prompt,
    section_query_human_prompt,
    section_query_system_prompt,
)
from .utils import get_search_params, select_and_execute_search

dotenv.load_dotenv()


class WebSearchAgent:
    """Agent that performs multi-step web search and organizes results into sections."""

    def __init__(self, config: Optional[WebSearchConfig] = None):
        """Initialize the WebSearchAgent.

        Args:
            config: Configuration for the search agent. If None, uses default config.
        """
        self.config = config or DEFAULT_CONFIG
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize the language model based on configuration."""
        if self.config.llm_provider.lower() == "openai":
            return ChatOpenAI(model=self.config.planner_model, verbose=True)
        else:
            raise ValueError(
                f"LLM provider '{self.config.llm_provider}' not supported. Use 'openai'."
            )

    async def _generate_queries(self, title: str, count: int) -> List[SearchQuery]:
        """Generate search queries based on a title."""
        # Use prompts from prompt.py
        system_prompt = initial_query_system_prompt.format(count=count)
        human_prompt = initial_query_human_prompt.format(title=title)

        structured_llm = self.llm.with_structured_output(QueryList)
        response = structured_llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
        )

        return response.queries

    async def _generate_sections(
        self, title: str, search_responses: List[SearchResponse]
    ) -> List[Section]:
        """Generate sections based on search responses."""
        # Prepare context from search responses
        context = self._format_search_responses(search_responses)

        # Use prompts from prompt.py
        system_prompt = section_generation_system_prompt.format(
            max_sections=min(self.config.max_sections, 5),
            title=title,
            must_cover_section_title=self.config.must_cover_section_title,
        )

        human_prompt = section_generation_human_prompt.format(
            title=title, context=context
        )

        structured_llm = self.llm.with_structured_output(SectionList)
        response = structured_llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
        )

        # Convert to Section objects
        sections = []
        # print(response, response.sections)
        for section_data in response.sections:
            # print(section_data)
            section = Section(
                title=section_data.title,
                description=section_data.description,
                search_queries=[],  # add empty list
                search_responses=[],  # add empty list
            )
            sections.append(section)

        return sections

    async def _generate_section_queries(
        self, section: Section, main_title: str
    ) -> List[SearchQuery]:
        """Generate search queries specific to a section."""
        # Use prompts from prompt.py
        system_prompt = section_query_system_prompt.format(
            query_count=self.config.section_queries_count,
            main_title=main_title,
            section_title=section.title,
            section_description=section.description,
        )

        human_prompt = section_query_human_prompt.format(section_title=section.title)

        structured_llm = self.llm.with_structured_output(QueryList)
        response = structured_llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
        )

        return response.queries

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

    async def search(self, title: str, verbose: bool = False) -> WebSearchResult:
        """Execute the full search process for a given title.

        Args:
            title: The topic/title to research
            verbose: Whether to print progress messages

        Returns:
            WebSearchResult object containing all search results and sections
        """
        search_api = self.config.search_api
        search_params = get_search_params(search_api, self.config.search_api_config)

        # Step 1: Generate initial queries
        if verbose:
            print(f"Generating initial queries for: {title}")
        initial_queries = await self._generate_queries(
            title, self.config.initial_queries_count
        )

        # Step 2: Execute initial searches
        if verbose:
            print(f"Executing {len(initial_queries)} initial searches...")
        query_strings = [q.query for q in initial_queries]
        initial_responses = await select_and_execute_search(
            search_api, query_strings, search_params
        )

        # Step 3: Generate sections based on search results
        if verbose:
            print("Generating sections based on initial search results...")
        sections = await self._generate_sections(title, initial_responses)
        if verbose:
            print(f"Generated {len(sections)} sections")

        # Step 4: For each section, generate and execute specific searches
        for i, section in enumerate(sections):
            if verbose:
                print(f"Processing section {i + 1}/{len(sections)}: {section.title}")

            # Generate section-specific queries
            section_queries = await self._generate_section_queries(section, title)
            section.search_queries = section_queries

            # Execute searches for this section
            query_strings = [q.query for q in section_queries]
            section_responses = await select_and_execute_search(
                search_api, query_strings, search_params
            )
            section.search_responses = section_responses

        # Step 5: Return the complete WebSearchResult
        return WebSearchResult(
            title=title,
            initial_queries=initial_queries,
            initial_responses=initial_responses,
            sections=sections,
        )


async def search_topic(
    topic: str, config: Optional[WebSearchConfig] = None, verbose: bool = False
) -> WebSearchResult:
    """Search for a single topic.

    Args:
        topic: The topic to research
        config: Optional custom configuration
        verbose: Whether to print progress information

    Returns:
        WebSearchResult containing the research results
    """
    agent = WebSearchAgent(config or DEFAULT_CONFIG)
    return await agent.search(topic, verbose=verbose)


async def search_multiple_topics(
    topics: List[str],
    config: Optional[WebSearchConfig] = None,
    verbose: bool = False,
    save_output: bool = False,
    output_dir: str = "output",
) -> List[Union[WebSearchResult, Dict[str, Any]]]:
    """Search for multiple topics.

    Args:
        topics: List of topics to research
        config: Optional custom configuration
        verbose: Whether to print progress information
        save_output: Whether to save results to files
        output_dir: Directory to save output files in

    Returns:
        List of WebSearchResult objects or error dictionaries
    """
    agent = WebSearchAgent(config or DEFAULT_CONFIG)
    results = []

    for i, topic in enumerate(topics):
        if verbose:
            print(f"\nResearching topic {i + 1}/{len(topics)}: {topic}")
        try:
            result = await agent.search(topic, verbose=verbose)

            if save_output:
                filename = save_result_to_file(result, output_dir)
                if verbose:
                    print(f"Saved result to: {filename}")

            results.append(result)

            if verbose:
                print(f"Completed: {topic}")

        except Exception as e:
            error_info = {"topic": topic, "error": str(e)}
            results.append(error_info)
            if verbose:
                print(f"Error researching '{topic}': {str(e)}")

    return results


def save_result_to_file(result: WebSearchResult, output_dir: str = "output") -> str:
    """Save search result to file (optional utility).

    Args:
        result: The WebSearchResult to save
        output_dir: Directory to save the file in

    Returns:
        Path to the saved file
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    safe_title = "".join(
        [c if c.isalnum() or c in [" ", "_"] else "_" for c in result.title]
    )
    safe_title = safe_title[:50]
    filename = f"{output_dir}/{safe_title}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)

    return filename


async def example_usage():
    """Example showing how to use the WebSearchAgent."""
    # Example 1: Basic usage with default configuration
    result = await search_topic("Artificial Intelligence ethics", verbose=True)
    print(f"Found {len(result.sections)} sections about AI ethics")

    # Example 2: Custom configuration
    custom_config = WebSearchConfig(
        planner_model="o1", initial_queries_count=3, max_sections=5
    )
    topics = ["Renewable energy advancements", "Future of remote work"]
    results = await search_multiple_topics(
        topics,
        config=custom_config,
        verbose=True,
        save_output=True,
        output_dir="custom_output",
    )
    # Example 3: Processing results
    for result in results:
        if isinstance(result, WebSearchResult):
            print(f"\nTopic: {result.title}")
            for section in result.sections:
                print(f"- {section.title}")


def main():
    asyncio.run(example_usage())
