# Web Search Agent

A modular Python package for intelligent web search that processes search results into structured, section-based information.

## Overview

Web Search Agent is an infrastructure tool that performs web searches based on a given topic, processes the results using AI, and returns structured information organized into relevant sections. It helps users/developers quickly gather and organize comprehensive information on specific topics.

## Features

- Topic-based intelligent web searching
- AI-powered query generation for comprehensive coverage
- Automatic organization of search results into logical sections
- Section-specific sub-queries for in-depth analysis
- Structured JSON output for easy processing
- Configurable search parameters and model settings
- Support for multiple search APIs (Tavily, Exa)

## Installation

### Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Search API key (Tavily, Exa, etc.)

### Installation Steps

```bash
# Create and activate a virtual environment (optional but recommended)
conda create -n web-search-agent python=3.11.11
conda activate web-search-agent

# Install from PyPI
pip install web-search-agent

# Or install from source
git clone https://github.com/leepokai/web-search-agent.git
cd web-search-agent
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env file to add your API keys
```

## Usage

### Basic Usage

```python
import asyncio
from web_search_agent import WebSearchAgent, WebSearchConfig

async def main():
    # Create a default agent
    agent = WebSearchAgent()
    
    # Search for a topic
    result = await agent.search("Artificial Intelligence ethics")
    
    # Process the results
    print(f"Topic: {result.title}")
    print(f"Found {len(result.sections)} sections")
    
    for section in result.sections:
        print(f"- {section.title}: {section.description[:100]}...")

# Run the async function
asyncio.run(main())
```

### Advanced Usage

```python
import asyncio
from web_search_agent import WebSearchAgent, WebSearchConfig, search_multiple_topics

async def research_project():
    # Custom configuration
    config = WebSearchConfig(
        planner_model="o1",
        initial_queries_count=3,
        max_sections=5,
        search_api="tavily",
        search_api_config={"include_raw_content": True, "max_results": 3}
    )
    
    # Search multiple topics
    topics = [
        "Renewable energy advancements",
        "Future of remote work"
    ]
    
    results = await search_multiple_topics(
        topics,
        config=config,
        verbose=True,
        save_output=True,
        output_dir="research_output"
    )
    
    # Process results
    for result in results:
        if hasattr(result, 'title'):  # Check if valid result
            print(f"\nTopic: {result.title}")
            for section in result.sections:
                print(f"- {section.title}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(research_project())
```

### Using Additional Context

The `additional_info` parameter allows you to provide specific guidance to refine your search. This context is added to the query generation process to produce more targeted search queries.

```python
import asyncio
from web_search_agent import search_topic

async def focused_research():
    # Basic topic with additional context
    result = await search_topic(
        topic="Renewable energy",
        additional_info="Focus on developments after 2022, particularly in solar technology and battery storage. Include economic viability and government policies.",
        verbose=True
    )
    
    print(f"Topic: {result.title}")
    for section in result.sections:
        print(f"- {section.title}")

# Run the async function
asyncio.run(focused_research())
```

You can also use additional context when searching multiple topics:

```python
import asyncio
from web_search_agent import search_multiple_topics

async def multiple_focused_searches():
    # Topics with corresponding additional context for each
    topics = [
        "Artificial Intelligence in healthcare",
        "Remote work security risks"
    ]
    
    additional_infos = [
        "Focus on diagnostic applications, FDA approvals since 2021, and major hospital implementations",
        "Include zero-trust security models, risks of personal devices on home networks, and best practices for secure remote access"
    ]
    
    results = await search_multiple_topics(
        topics=topics,
        additional_infos=additional_infos,
        verbose=True
    )
    
    # Process results
    for result in results:
        if hasattr(result, 'title'):
            print(f"\nTopic: {result.title}")
            for section in result.sections:
                print(f"- {section.title}")

# Run the async function
asyncio.run(multiple_focused_searches())
```

### Command Line Usage

```bash
# Basic usage
web-search-agent

# For more options
web-search-agent --help
```

## API Reference

### Main Classes

- `WebSearchAgent`: Core class for performing searches and processing results
- `WebSearchConfig`: Configuration class for customizing search behavior
- `WebSearchResult`: Result container with all search data and sections

### Key Functions

- `search_topic(topic, config=None, verbose=False, additional_info=None)`: Search for a single topic
  - `additional_info`: Optional string providing additional context to guide the query generation
- `search_multiple_topics(topics, config=None, verbose=False, save_output=False, additional_infos=None)`: Search for multiple topics
  - `additional_infos`: Optional list of strings with additional context for each topic

## Configuration Options

The `WebSearchConfig` class provides the following configuration options:

```python
WebSearchConfig(
    # LLM Configuration
    llm_provider="openai",         # LLM provider (currently supports "openai")
    planner_model="o1",            # Model for planning and query generation
    
    # Search Configuration
    search_api="tavily",           # Search API (tavily, exa, etc.)
    search_api_config={            # Additional search API configuration
        "include_raw_content": True,
        "max_results": 3
    },
    
    # Query Generation
    initial_queries_count=3,       # Number of initial search queries
    section_queries_count=2,       # Number of search queries per section
    
    # Control Parameters
    max_sections=5,                # Maximum number of sections to generate
    must_cover_section_title="..." # Prompt for must-cover sections
)
```

## Output Format

The tool outputs structured data with the following main fields:

- `title`: Main search topic
- `initial_queries`: List of initial search queries
- `initial_responses`: Search results for each initial query
- `sections`: List of generated sections
  - Each section contains: title, description, search queries and responses

## Example Output

```json
{
  "title": "Artificial Intelligence Ethics",
  "initial_queries": [...],
  "initial_responses": [...],
  "sections": [
    {
      "title": "Privacy concerns in AI systems",
      "description": "An analysis of how AI technologies impact personal privacy...",
      "search_queries": [...],
      "search_responses": [...]
    },
    ...
  ]
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
