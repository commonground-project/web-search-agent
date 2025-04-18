import pytest

from config import WebSearchConfig


@pytest.fixture
def test_config():
    return WebSearchConfig(
        llm_provider="openai",
        planner_model="o1",
        search_api="tavily",
        initial_queries_count=1,
    )
