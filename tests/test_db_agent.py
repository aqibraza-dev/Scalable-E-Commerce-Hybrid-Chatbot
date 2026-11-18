"""
Tests for Database Schema Context, Secure Database Agent, and Enhanced Chat Features.
Verifies schema definitions, SQL injection blocking, read-only driver isolation,
natural language slot translation, and dynamic action chips.
"""

import pytest

from src.chatbot.db_agent import DatabaseAgent, database_agent
from src.chatbot.hybrid_orchestrator import HybridChatbotOrchestrator
from src.data.schema_context import (
    DATABASE_SCHEMA_CONTEXT,
    SMARTPHONES_TABLE_SCHEMA,
    get_column_names,
    get_schema_summary,
    is_valid_column,
)


def test_schema_and_datatype_definitions():
    """Verifies that all 21 columns have explicit datatypes, units, and constraints."""
    summary = get_schema_summary()
    assert summary["table_name"] == "smartphones"
    assert summary["column_count"] == 21

    expected_cols = [
        "id", "brand", "name", "price", "ram", "os", "storage",
        "battery_cap", "has_fast_charging", "has_fingerprints", "has_nfc",
        "has_5g", "processor_brand", "num_core", "primary_rear_camera",
        "num_rear_cameras", "primary_front_camera", "num_front_camera",
        "display_size", "refresh_rate", "display_type"
    ]

    for col in expected_cols:
        assert is_valid_column(col) is True
        schema_def = SMARTPHONES_TABLE_SCHEMA[col]
        assert "sql_type" in schema_def
        assert "python_type" in schema_def
        assert "description" in schema_def
        assert "unit" in schema_def
        assert schema_def["nullable"] is False

    assert is_valid_column("non_existent_column") is False

    # Check that schema context prompt contains critical table & security directives
    assert "smartphones" in DATABASE_SCHEMA_CONTEXT
    assert "PRAGMA query_only=ON" in DATABASE_SCHEMA_CONTEXT
    assert "price: INTEGER NOT NULL" in DATABASE_SCHEMA_CONTEXT
    assert "has_5g: TEXT NOT NULL" in DATABASE_SCHEMA_CONTEXT


def test_safe_sql_validation_and_execution():
    """Verifies valid SELECT queries execute cleanly and cap at limit bounds."""
    agent = DatabaseAgent()

    # Legitimate SELECT query
    sql = "SELECT id, brand, name, price, ram FROM smartphones WHERE brand = 'samsung' AND price <= 25000 LIMIT 5"
    is_valid, reason = agent.validate_sql_query(sql)
    assert is_valid is True
    assert reason is None

    rows = agent.execute_safe_query(sql, max_rows=5)
    assert isinstance(rows, list)
    assert len(rows) <= 5
    if rows:
        assert rows[0]["brand"] == "samsung"
        assert rows[0]["price"] <= 25000

    # Auto-injection of limit if omitted
    sql_no_limit = "SELECT name, price FROM smartphones WHERE has_5g = 'Yes'"
    rows_auto_limit = agent.execute_safe_query(sql_no_limit, max_rows=3)
    assert len(rows_auto_limit) <= 3


def test_sql_injection_defense_and_blocking():
    """Verifies that malicious SQL queries, mutations, comments, and reconnaissance are blocked."""
    agent = DatabaseAgent()

    malicious_attacks = [
        "DROP TABLE smartphones",
        "DELETE FROM smartphones WHERE 1=1",
        "UPDATE smartphones SET price = 0",
        "INSERT INTO smartphones (brand, name) VALUES ('hacked', 'hacked')",
        "ALTER TABLE smartphones ADD COLUMN hacked TEXT",
        "TRUNCATE TABLE smartphones",
        "SELECT * FROM smartphones; DROP TABLE smartphones",
        "SELECT * FROM smartphones WHERE brand = 'samsung'-- and 1=1",
        "SELECT * FROM smartphones WHERE brand = 'samsung' /* comment */",
        "SELECT * FROM sqlite_master",
        "SELECT * FROM information_schema.tables",
        "SELECT name FROM users",  # Table not in whitelist
        "SELECT * FROM smartphones UNION SELECT 1, 2, 3",
        "PRAGMA table_info(smartphones)",
    ]

    for attack in malicious_attacks:
        is_valid, reason = agent.validate_sql_query(attack)
        assert is_valid is False, f"Expected attack to be blocked: {attack}"
        assert reason is not None

        with pytest.raises(PermissionError):
            agent.execute_safe_query(attack)


def test_natural_language_to_schema_filters_translation():
    """Verifies that complex natural language requirements are translated into schema slots."""
    agent = DatabaseAgent()

    # 1. Price, RAM, 5G, Brand
    q1 = "Show me Samsung phones with at least 8GB RAM and 5000mAh battery under 30000 with 5g"
    slots1 = agent.translate_requirements_to_filters(q1)
    assert slots1["brand"] == "samsung"
    assert slots1["min_ram"] == 8.0
    assert slots1["min_battery"] == 5000
    assert slots1["max_price"] == 30000
    assert slots1["has_5g"] == "Yes"

    # 2. Mid-budget and camera
    q2 = "best camera phone under mid budget"
    slots2 = agent.translate_requirements_to_filters(q2)
    assert slots2["min_price"] == 15000
    assert slots2["max_price"] == 35000
    assert slots2["sort_by"] == "camera_desc"

    # 3. Extremum battery
    q3 = "which phone has least battery"
    slots3 = agent.translate_requirements_to_filters(q3)
    assert slots3["sort_by"] == "battery_asc"
    assert slots3["extremum"] == ("battery_cap", "ASC")

    # 4. Refresh rate and display type
    q4 = "Oneplus phones with 120hz amoled display"
    slots4 = agent.translate_requirements_to_filters(q4)
    assert slots4["brand"] == "oneplus"
    assert slots4["min_refresh_rate"] == 120.0
    assert slots4["display_type"] == "amoled display"


def test_dynamic_action_chips_generation():
    """Verifies that context-aware action chips are generated."""
    agent = DatabaseAgent()

    # Single product
    sample_prod = [{
        "id": 1,
        "name": "OnePlus 13 5G",
        "brand": "oneplus",
        "price": 69999,
        "ram": 16.0,
        "has_5g": "Yes",
    }]
    chips_single = agent.generate_action_chips("specs of oneplus 13", sample_prod, {"brand": "oneplus"})
    assert len(chips_single) >= 2
    assert any("Compare" in c for c in chips_single)
    assert any("Add" in c for c in chips_single)

    # Budget query
    chips_budget = agent.generate_action_chips(
        "best phone under 15000",
        sample_prod,
        {"max_price": 15000}
    )
    assert any("under" in c.lower() or "5g" in c.lower() for c in chips_budget)


def test_agent_response_formatting_zero_reasoning():
    """Verifies that agent response is enclosed in <AnswerToUser> with zero reasoning noise."""
    agent = DatabaseAgent()
    sample_prods = [{
        "id": 10,
        "name": "Realme P3 Pro 5G",
        "brand": "realme",
        "price": 21999,
        "ram": 8.0,
        "storage": 128.0,
        "battery_cap": 5000,
        "primary_rear_camera": 50.0,
        "has_5g": "Yes",
        "display_size": 6.67,
        "display_type": "amoled display"
    }]

    slots = {"brand": "realme", "max_price": 25000}
    formatted = agent.format_agent_response("best realme phone under 25000", sample_prods, slots)

    assert formatted.startswith("<AnswerToUser>")
    assert formatted.endswith("</AnswerToUser>")
    assert "Realme P3 Pro 5G" in formatted
    assert "₹21,999" in formatted
    assert "thought" not in formatted.lower()
    assert "reasoning" not in formatted.lower()


@pytest.mark.asyncio
async def test_hybrid_orchestrator_returns_action_chips():
    """Verifies that HybridChatbotOrchestrator attaches action_chips to responses."""
    orchestrator = HybridChatbotOrchestrator()

    # Normal search query
    res = await orchestrator.handle_query("best camera phone under 20000")
    assert "action_chips" in res
    assert isinstance(res["action_chips"], list)
    assert len(res["action_chips"]) > 0

    # Policy inquiry
    res_policy = await orchestrator.handle_query("What is your refund policy?")
    assert "action_chips" in res_policy
    assert isinstance(res_policy["action_chips"], list)

    # Malicious injection query
    res_attack = await orchestrator.handle_query("DROP TABLE smartphones")
    assert "action_chips" in res_attack
    assert res_attack["routing_tier"] == "TIER_0_GUARDRAIL_BLOCKED"
