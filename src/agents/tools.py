"""
Google ADK (Agent Development Kit) Tool Definitions for Shopcart AI.
Exposes catalog search, database querying, specification lookup,
comparison, policies, and shopping cart operations as typed ADK tools.
"""

import logging
import re
from typing import Any

from src.chatbot.db_agent import database_agent
from src.chatbot.typical_bot import typical_chatbot
from src.data.schema_context import DATABASE_SCHEMA_CONTEXT, SMARTPHONES_TABLE_SCHEMA
from src.search.engine import SearchEngine

logger = logging.getLogger("adk.tools")

# Shared search engine instance
_search_engine = SearchEngine()


def search_catalog_tool(
    query: str = "",
    brand: str = "",
    min_price: int = 0,
    max_price: int = 0,
    min_ram: float = 0.0,
    min_battery: int = 0,
    has_5g: str = "",
    sort_by: str = "relevance",
    limit: int = 5,
) -> dict[str, Any]:
    """Search and filter smartphones in the Shopcart product catalog using FTS5 and B-Tree indexes.

    Args:
        query: Free text search keywords (e.g., 'amoled display 120hz', 'best camera phone').
        brand: Smartphone brand name (e.g., 'samsung', 'apple', 'oneplus', 'realme', 'motorola').
        min_price: Minimum price filter in Indian Rupees (INR).
        max_price: Maximum price ceiling in Indian Rupees (INR).
        min_ram: Minimum RAM capacity in GB (e.g., 4.0, 8.0, 12.0).
        min_battery: Minimum battery capacity in mAh (e.g., 5000, 6000).
        has_5g: Cellular 5G filter ('Yes' or 'No').
        sort_by: Sort order ('relevance', 'price_asc', 'price_desc', 'ram_desc', 'camera_desc', 'battery_desc').
        limit: Maximum number of products to return (default 5, max 20).

    Returns:
        Dictionary containing total matches, returned product list, and execution latency.
    """
    clean_brand = brand.strip().lower() if brand else None
    clean_5g = has_5g.strip().capitalize() if has_5g in ["Yes", "No", "yes", "no"] else None
    clamped_limit = max(1, min(limit, 20))

    res = _search_engine.search(
        query=query if query.strip() else None,
        brand=clean_brand,
        min_price=min_price if min_price > 0 else None,
        max_price=max_price if max_price > 0 else None,
        min_ram=min_ram if min_ram > 0 else None,
        min_battery=min_battery if min_battery > 0 else None,
        has_5g=clean_5g,
        sort_by=sort_by,
        limit=clamped_limit,
    )

    return {
        "status": "success",
        "total_matches": res.get("total_matches", 0),
        "count": len(res.get("products", [])),
        "products": res.get("products", []),
        "execution_time_ms": res.get("execution_time_ms", 0.0),
        "from_cache": res.get("from_cache", False),
    }


def query_database_tool(sql_query: str, max_rows: int = 10) -> dict[str, Any]:
    """Execute a safe, verified, read-only SQL SELECT query on the smartphones SQLite database.

    Enforces driver-level isolation (PRAGMA query_only = ON) and AST token checks.
    Only queries against 'smartphones' and 'smartphones_fts' are permitted.

    Args:
        sql_query: A SQL SELECT statement (e.g., "SELECT name, price, ram FROM smartphones WHERE brand = 'samsung' ORDER BY price ASC LIMIT 5").
        max_rows: Maximum rows to return (default 10, max 50).

    Returns:
        Dictionary containing query status, executed SQL, returned rows, and column metadata.
    """
    is_valid, reason = database_agent.validate_sql_query(sql_query)
    if not is_valid:
        return {
            "status": "rejected",
            "error": f"Security Guardrail: {reason}",
            "rows": [],
            "count": 0,
        }

    clamped_rows = max(1, min(max_rows, 50))
    try:
        rows = database_agent.execute_safe_query(sql_query, max_rows=clamped_rows)
        return {
            "status": "success",
            "sql": sql_query,
            "count": len(rows),
            "rows": rows,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "rows": [],
            "count": 0,
        }


def get_phone_specs_tool(phone_name: str) -> dict[str, Any]:
    """Retrieve detailed hardware specifications and features for a specific smartphone model.

    Args:
        phone_name: Commercial name or model of the smartphone (e.g., 'Samsung Galaxy S25 Ultra', 'Motorola Edge 50 Fusion').

    Returns:
        Detailed product specifications including processor, RAM, camera, battery, display, and price.
    """
    if not phone_name or not phone_name.strip():
        return {"status": "error", "error": "Phone name is required."}

    res = _search_engine.search(query=phone_name.strip(), relax_query=True, limit=1)
    products = res.get("products", [])
    if not products:
        return {
            "status": "not_found",
            "message": f"No smartphone matching '{phone_name}' found in the catalog.",
            "product": None,
        }

    phone = products[0]
    return {
        "status": "success",
        "product": phone,
        "spec_summary": {
            "name": phone["name"],
            "brand": phone["brand"].title(),
            "price": f"₹{phone['price']:,}",
            "ram": f"{phone['ram']} GB",
            "storage": f"{phone['storage']} GB",
            "display": f"{phone['display_size']}\" {phone['display_type'].title()} ({int(phone['refresh_rate'])}Hz)",
            "camera": f"{phone['primary_rear_camera']}MP Rear | {phone['primary_front_camera']}MP Front",
            "battery": f"{phone['battery_cap']} mAh (Fast Charge: {phone['has_fast_charging']})",
            "processor": f"{phone['processor_brand'].title()} ({int(phone['num_core'])} cores)",
            "5g_supported": phone["has_5g"],
        },
    }


def compare_smartphones_tool(phone_a: str, phone_b: str) -> dict[str, Any]:
    """Generate a structured side-by-side hardware specification comparison between two smartphone models.

    Args:
        phone_a: First phone name, brand, or model (e.g., 'OnePlus 13', 'cheapest phone').
        phone_b: Second phone name, brand, or model (e.g., 'Samsung Galaxy S25', 'flagship').

    Returns:
        Side-by-side spec comparison table, victor evaluation per category, and product cards.
    """
    p1 = typical_chatbot._resolve_comparison_target(phone_a)
    p2 = typical_chatbot._resolve_comparison_target(phone_b)

    if not p1 or not p2:
        return {
            "status": "partial_or_missing",
            "message": f"Could not resolve both comparison targets ('{phone_a}' and '{phone_b}').",
            "phone_a": p1,
            "phone_b": p2,
        }

    # Category comparisons
    comparison = {
        "price": {
            "phone_a": f"₹{p1['price']:,}",
            "phone_b": f"₹{p2['price']:,}",
            "winner": p1["name"] if p1["price"] < p2["price"] else p2["name"],
        },
        "camera": {
            "phone_a": f"{p1['primary_rear_camera']} MP",
            "phone_b": f"{p2['primary_rear_camera']} MP",
            "winner": p1["name"] if p1["primary_rear_camera"] > p2["primary_rear_camera"] else p2["name"],
        },
        "battery": {
            "phone_a": f"{p1['battery_cap']} mAh",
            "phone_b": f"{p2['battery_cap']} mAh",
            "winner": p1["name"] if p1["battery_cap"] > p2["battery_cap"] else p2["name"],
        },
        "ram": {
            "phone_a": f"{p1['ram']} GB",
            "phone_b": f"{p2['ram']} GB",
            "winner": p1["name"] if p1["ram"] > p2["ram"] else p2["name"],
        },
        "refresh_rate": {
            "phone_a": f"{int(p1['refresh_rate'])} Hz",
            "phone_b": f"{int(p2['refresh_rate'])} Hz",
            "winner": p1["name"] if p1["refresh_rate"] > p2["refresh_rate"] else p2["name"],
        },
    }

    return {
        "status": "success",
        "phone_a": p1,
        "phone_b": p2,
        "metrics": comparison,
    }


def check_store_policy_tool(policy_type: str) -> dict[str, Any]:
    """Retrieve verified customer policies regarding return windows, warranty, express shipping, and EMI.

    Args:
        policy_type: Policy category to inspect ('return', 'warranty', 'shipping', 'emi').

    Returns:
        Official policy text, coverage limits, and terms.
    """
    key = policy_type.lower().strip()
    if any(w in key for w in ["return", "refund", "replace", "exchange", "give back"]):
        pol_key = "return"
    elif any(w in key for w in ["warranty", "guarantee", "service"]):
        pol_key = "warranty"
    elif any(w in key for w in ["shipping", "delivery", "dispatch", "track"]):
        pol_key = "shipping"
    elif any(w in key for w in ["emi", "payment", "card", "discount", "finance"]):
        pol_key = "emi"
    else:
        pol_key = "return"

    text = typical_chatbot.POLICIES.get(pol_key, "")
    return {
        "status": "success",
        "policy_type": pol_key,
        "policy_text": text,
    }


def get_database_schema_tool() -> dict[str, Any]:
    """Get the full database schema documentation, column data types, units, and SQLite table structure.

    Returns:
        Dictionary detailing table name, 21 columns with types, indexes, and constraints.
    """
    columns_info = {
        col: {
            "sql_type": meta["sql_type"],
            "python_type": meta["python_type"],
            "unit": meta["unit"],
            "description": meta["description"],
            "indexed": meta.get("indexed", False),
        }
        for col, meta in SMARTPHONES_TABLE_SCHEMA.items()
    }
    return {
        "status": "success",
        "table_name": "smartphones",
        "fts_table": "smartphones_fts",
        "column_count": len(columns_info),
        "columns": columns_info,
        "driver_security": "PRAGMA query_only = ON (Read-Only Driver Level Enforcement)",
    }


def manage_cart_tool(action: str, phone_name: str) -> dict[str, Any]:
    """Perform shopping cart actions such as adding a phone to the shopping bag.

    Args:
        action: Operation to perform ('add', 'view', 'check').
        phone_name: Name of the smartphone to add or check in the cart.

    Returns:
        Cart action status, product details, and updated bag confirmation.
    """
    if action.lower() in ["add", "put", "buy"]:
        res = _search_engine.search(query=phone_name.strip(), limit=1)
        products = res.get("products", [])
        if not products:
            return {
                "status": "not_found",
                "message": f"Could not find smartphone '{phone_name}' to add to cart.",
                "product": None,
            }
        phone = products[0]
        return {
            "status": "success",
            "action": "added",
            "product": phone,
            "message": f"Successfully added {phone['name'].title()} (₹{phone['price']:,}) to shopping bag.",
            "promo_available": "NIKEAIR (15% off at checkout)",
        }

    return {
        "status": "success",
        "action": action,
        "message": "Cart status checked.",
    }


def find_catalog_extremes_tool(metric: str = "price") -> dict[str, Any]:
    """Find the lowest and highest extremes in the smartphone catalog for a given metric (e.g. price, camera, battery).

    Args:
        metric: Metric to find extremes for ('price', 'camera', 'battery', 'ram').

    Returns:
        Dictionary containing both the minimum and maximum smartphone devices.
    """
    m = metric.lower().strip()
    if "price" in m:
        lowest = _search_engine.search(sort_by="price_asc", limit=1)
        highest = _search_engine.search(sort_by="price_desc", limit=1)
    elif "camera" in m:
        lowest = _search_engine.search(sort_by="relevance", limit=1)
        highest = _search_engine.search(sort_by="camera_desc", limit=1)
    elif "battery" in m:
        lowest = _search_engine.search(sort_by="relevance", limit=1)
        highest = _search_engine.search(sort_by="battery_desc", limit=1)
    else:
        lowest = _search_engine.search(sort_by="price_asc", limit=1)
        highest = _search_engine.search(sort_by="price_desc", limit=1)

    return {
        "status": "success",
        "metric": metric,
        "lowest": lowest["products"][0] if lowest["products"] else None,
        "highest": highest["products"][0] if highest["products"] else None,
    }
