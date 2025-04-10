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
section_generation_system_prompt = """Based on the search results provided, identify key subtopics or sections for the main topic: '{title}'.

Your response MUST include the following mandatory sections:
{must_cover_section_title}

IMPORTANT INSTRUCTIONS:
1. For each mandatory section above, extract and synthesize relevant information directly from the search results.
2. If the search results don't contain enough information for a mandatory section, note this explicitly but still include the section.
3. Use concrete examples, data points, and facts from the search results to support each mandatory section.

In addition to these mandatory sections, add more sections (up to a total of {max_sections} sections) that cover other important aspects found in the search results.

For each section (both mandatory and additional), provide:
1. A clear, concise title that reflects the content
2. A brief description of what this section will cover (1-2 sentences), referencing specific information from the search results

Ensure all sections:
- Are based on substantive information found in the search results
- Are distinct and do not significantly overlap
- Cover the most important aspects of the topic
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

must_cover_section_prompt = "1. Identify all key individuals, organizations, government agencies, or entities involved in the topic 2. Outline the different perspectives and viewpoints on the issue without making value judgments 3. Present important statistics, official data, or research findings that provide factual context"
