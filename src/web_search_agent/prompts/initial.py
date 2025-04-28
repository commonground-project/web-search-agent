# Initial query generation prompts
initial_query_system_prompt = """Generate {count} specific and effective search queries to gather information about the given title.

The queries should:
1. Be diverse to cover different aspects of the topic
2. Be specific enough to return relevant results
3. Use different phrasings to capture various sources
{additional_info_prompt}

Format your response as a JSON list of queries.
"""

initial_query_human_prompt = "Generate search queries for the title: '{title}'"
