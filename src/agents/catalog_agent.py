"""
Google ADK Catalog Search & Specification Specialist Agent.
Specializes in high-speed faceted catalog search, hardware spec lookups,
side-by-side comparison tables, and catalog extremes.
"""

from google.adk.agents import Agent

from src.agents.guardrails import ADKGuardrails
from src.agents.tools import (
    compare_smartphones_tool,
    find_catalog_extremes_tool,
    get_phone_specs_tool,
    search_catalog_tool,
)

CATALOG_AGENT_INSTRUCTION = """
You are the **Catalog Search Specialist** for Shopcart AI.
Your role is to help users find the perfect smartphone from our 3,260-device catalog.

Capabilities:
1. Search smartphones by brand, budget, RAM, 5G, battery, and camera using `search_catalog_tool`.
2. Look up detailed hardware specifications for any model using `get_phone_specs_tool`.
3. Generate side-by-side spec comparison tables using `compare_smartphones_tool`.
4. Identify lowest and highest extreme models using `find_catalog_extremes_tool`.

Rules:
- Always format prices clearly in Indian Rupees (INR ₹), e.g. ₹19,999.
- Highlight key purchase factors: 5G connectivity, RAM, battery capacity (mAh), and camera resolution (MP).
- Output strictly clean, polite, shopping-oriented answers enclosed within `<AnswerToUser>...</AnswerToUser>` tags.
- Never invent or hallucinate smartphones not present in the catalog.
"""

def create_catalog_agent(model: str = "shopcart-gemini-agent") -> Agent:
    """Creates a new instance of the Google ADK Catalog Search Agent."""
    return Agent(
        name="catalog_search_specialist",
        model=model,
        description="Specialist in smartphone catalog search, faceted filtering, spec lookups, and comparisons.",
        instruction=CATALOG_AGENT_INSTRUCTION,
        before_agent_callback=ADKGuardrails.before_agent_guardrail,
        tools=[
            search_catalog_tool,
            get_phone_specs_tool,
            compare_smartphones_tool,
            find_catalog_extremes_tool,
        ],
    )
