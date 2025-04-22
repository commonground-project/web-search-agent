def test_config_from_fixture(test_config):
    """Test that the fixture provides correct configuration."""
    assert test_config.llm_provider == "openai"
    assert test_config.planner_model == "o1"
    assert test_config.search_api == "tavily"
    assert test_config.initial_queries_count == 1
