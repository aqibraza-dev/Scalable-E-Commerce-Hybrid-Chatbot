"""
Google ADK Database & Schema Specialist Agent.
Translates user questions into verified read-only SQL queries grounded
in the smartphones relational schema and data types.
"""

from google.adk.agents import Agent

from src.agents.guardrails import ADKGuardrails
from src.agents.tools import get_database_schema_tool, query_database_tool
from src.data.schema_context import DATABASE_SCHEMA_CONTEXT

DB_AGENT_INSTRUCTION = f"""
You are the **Database & Schema Specialist** for Shopcart AI.
Your role is to execute verified, read-only SQL queries on the SQLite database and explain table schemas.

{DATABASE_SCHEMA_CONTEXT}

Capabilities:
1. Execute safe, read-only SELECT queries on the `smartphones` or `smartphones_fts` tables using `query_database_tool`.
2. Inspect table structures, columns, datatypes, and constraints using `get_database_schema_tool`.

Strict Security Rules:
- ONLY SELECT queries are permitted. Any mutation (DROP, DELETE, UPDATE, ALTER, INSERT) is strictly forbidden.
- The SQLite database operates with PRAGMA query_only = ON; write operations physically fail at the C driver level.
- Always cap SELECT queries with a LIMIT clause (default 5 to 10 rows).
- Output your verified answer enclosed within `<AnswerToUser>...</AnswerToUser>` tags without leaking internal reasoning.
"""

def create_db_agent(model: str = "shopcart-gemini-agent") -> Agent:
    """Creates a new instance of the Google ADK Database & Schema Agent."""
    return Agent(
        name="database_schema_specialist",
        model=model,
        description="Specialist in relational database queries, schema inspection, and read-only catalog analytics.",
        instruction=DB_AGENT_INSTRUCTION,
        before_agent_callback=ADKGuardrails.before_agent_guardrail,
        tools=[
            query_database_tool,
            get_database_schema_tool,
        ],
    )
