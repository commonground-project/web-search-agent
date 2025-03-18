# Initial query generation prompts
initial_query_system_prompt = """Generate {count} specific and effective search queries to gather information about the given title.

The queries should:
1. Be diverse to cover different aspects of the topic
2. Be specific enough to return relevant results
3. Use different phrasings to capture various sources

Format your response as a JSON list of queries.
"""

initial_query_human_prompt = "Generate search queries for the title: '{title}'"

# Section generation prompts
section_generation_system_prompt = """Based on the search results provided, identify {max_sections} key subtopics or sections for the main topic: '{title}'.

For each section, provide:
1. A clear, concise title
2. A brief description of what this section should cover (1-2 sentences)
3. cannot significantly overlap with other sections

Ensure the sections:
- Are distinct and do not significantly overlap
- Cover the most important aspects of the topic
- Are based on the information from the search results
- Are organized in a logical structure

Format your response as a JSON list of sections with 'title' and 'description' fields.
"""

section_generation_human_prompt = "Generate sections for the topic '{title}' based on these search results:\n\n{context}"

# Section-specific query generation prompts
section_query_system_prompt = """Generate {query_count} specific search queries to gather detailed information about a section of research.

Main topic: {main_title}
Section title: {section_title}
Section description: {section_description}

The queries should:
1. Be highly specific to this section's focus
2. Cover different aspects of the section topic
3. Be phrased to find detailed, authoritative information

Format your response as a JSON list of queries.
"""

section_query_human_prompt = "Generate search queries for the section '{section_title}'"