from config import WebSearchConfig


def test_config_initialization():
    config = WebSearchConfig(llm_provider="openai", planner_model="gpt-4o")
    assert config.llm_provider == "openai"
    assert config.planner_model == "gpt-4o"


def test_config_defaults():
    config = WebSearchConfig()

    assert config.llm_provider == "openai"
    assert config.planner_model == "o1"
    assert config.search_api == "tavily"
