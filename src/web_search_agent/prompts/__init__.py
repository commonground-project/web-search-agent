"""Prompt templates for WebSearchAgent."""

from .initial import (
    initial_query_human_prompt,
    initial_query_system_prompt,
)
from .section import (
    must_cover_section_prompt,
    section_generation_human_prompt,
    section_generation_system_prompt,
    section_query_human_prompt,
    section_query_system_prompt,
)

__all__ = [
    "initial_query_system_prompt",
    "initial_query_human_prompt",
    "section_generation_system_prompt",
    "section_generation_human_prompt",
    "section_query_system_prompt",
    "section_query_human_prompt",
    "must_cover_section_prompt",
]
