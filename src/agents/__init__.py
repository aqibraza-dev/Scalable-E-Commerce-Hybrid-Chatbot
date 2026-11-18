"""
Google ADK (Agent Development Kit) Multi-Agent System Package for Shopcart AI.
Exposes root orchestrator, specialized sub-agents, and registered ADK tools.
"""

from src.agents.advisor_agent import create_advisor_agent
from src.agents.catalog_agent import create_catalog_agent
from src.agents.db_agent import create_db_agent
from src.agents.models import ShopcartADKLlm
from src.agents.orchestrator import ADKOrchestrator, adk_orchestrator
from src.agents.policy_agent import create_policy_agent
from src.agents.tools import (
    check_store_policy_tool,
    compare_smartphones_tool,
    find_catalog_extremes_tool,
    get_database_schema_tool,
    get_phone_specs_tool,
    manage_cart_tool,
    query_database_tool,
    search_catalog_tool,
)

__all__ = [
    "ADKOrchestrator",
    "adk_orchestrator",
    "create_catalog_agent",
    "create_db_agent",
    "create_policy_agent",
    "create_advisor_agent",
    "ShopcartADKLlm",
    "search_catalog_tool",
    "query_database_tool",
    "get_phone_specs_tool",
    "compare_smartphones_tool",
    "check_store_policy_tool",
    "get_database_schema_tool",
    "manage_cart_tool",
    "find_catalog_extremes_tool",
]
