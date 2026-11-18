"""
Secure Database & Schema Query Agent for Shopcart.
Translates user natural language requirements into verified, safe, read-only
catalog queries grounded in the smartphones database schema and datatypes.
Enforces multi-layer SQL security, query_only isolation, and structured product delivery.
"""

import logging
import re
import sqlite3
import time
from typing import Any

from src.config import settings
from src.data.loader import get_db_connection
from src.data.schema_context import (
    DATABASE_SCHEMA_CONTEXT,
    SMARTPHONES_TABLE_SCHEMA,
    get_column_names,
    is_valid_column,
)
from src.guardrails.security import security_guardrails
from src.search.engine import SearchEngine

logger = logging.getLogger(__name__)


class DatabaseAgent:
    """
    Enterprise Schema-Aware Agent for E-Commerce Catalog Operations.
    Features:
    - Grounded in exact database schema and datatypes
    - Secure AST and token validation for read-only SQL queries
    - Driver-level query isolation (PRAGMA query_only = ON)
    - Natural language slot extraction & intelligent query synthesis
    - Dynamic follow-up action chips generation
    - Structured product card delivery with zero reasoning leakage
    """

    ALLOWED_SORT_COLUMNS = {
        "price": "price",
        "ram": "ram",
        "battery_cap": "battery_cap",
        "battery": "battery_cap",
        "primary_rear_camera": "primary_rear_camera",
        "camera": "primary_rear_camera",
        "display_size": "display_size",
        "refresh_rate": "refresh_rate",
        "storage": "storage",
    }

    ALLOWED_SORT_DIRECTIONS = {"ASC", "DESC"}

    def __init__(
        self,
        search_engine: SearchEngine | None = None,
        db_path: str | None = None,
    ):
        self.search_engine = search_engine or SearchEngine()
        self.db_path = db_path or settings.sqlite_db_path
        self.schema_context = DATABASE_SCHEMA_CONTEXT
        self.columns = get_column_names()

    def get_schema_context(self) -> str:
        """Returns the formal schema context string for prompt injection."""
        return self.schema_context

    def validate_sql_query(self, sql: str) -> tuple[bool, str | None]:
        """
        Validates that an SQL query strictly conforms to read-only security requirements.
        Returns: (is_valid, rejection_reason)
        """
        if not sql or not sql.strip():
            return False, "Empty query string provided."

        normalized = sql.strip()

        # 1. Multi-layer guardrail check on input
        guard_res = security_guardrails.inspect_input(normalized)
        if not guard_res["is_safe"]:
            return False, guard_res["rejection_reason"]

        # 2. Query must strictly start with SELECT
        if not re.match(r"(?i)^\s*SELECT\b", normalized):
            return False, "Security Violation: Only SELECT queries are permitted."

        # 3. Stacked queries / multi-statements check
        if ";" in normalized.rstrip(";"):
            return False, "Security Violation: Stacked queries with semicolons are forbidden."

        # 4. Prohibited keywords and expressions
        forbidden_patterns = [
            r"(?i)\b(?:insert|update|delete|drop|alter|truncate|create|replace)\b",
            r"(?i)\b(?:pragma|load_extension|vacuum|reindex|attach|detach)\b",
            r"(?i)\b(?:sqlite_master|sqlite_temp_master|sqlite_schema|information_schema)\b",
            r"(?i)\bunion\s+(?:all\s+)?select\b",
            r"(?:--|/\*|\*/)",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, normalized):
                return False, f"Security Violation: Query contains prohibited token matching {pattern}."

        # 5. Table whitelist check: Must target 'smartphones' or 'smartphones_fts'
        table_matches = re.findall(r"(?i)\bfrom\s+([a-zA-Z0-9_]+)\b", normalized)
        if not table_matches:
            return False, "Security Violation: Query must specify a FROM clause."

        allowed_tables = {"smartphones", "smartphones_fts"}
        for tbl in table_matches:
            if tbl.lower() not in allowed_tables:
                return False, f"Security Violation: Access to table '{tbl}' is forbidden."

        return True, None

    def execute_safe_query(
        self,
        sql: str,
        params: tuple | list | None = None,
        max_rows: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Executes a validated read-only SQL query with PRAGMA query_only = ON
        and caps results with an enforced LIMIT.
        """
        is_valid, reason = self.validate_sql_query(sql)
        if not is_valid:
            logger.warning(f"DatabaseAgent blocked query: {sql} - Reason: {reason}")
            raise PermissionError(f"Query rejected by DatabaseAgent security guardrails: {reason}")

        # Ensure query has a LIMIT clause; inject or clamp if needed
        clean_sql = sql.rstrip("; \t\n")
        limit_match = re.search(r"(?i)\blimit\s+(\d+)\b", clean_sql)
        if limit_match:
            existing_limit = int(limit_match.group(1))
            if existing_limit > 50:
                clean_sql = re.sub(
                    r"(?i)\blimit\s+\d+\b", f"LIMIT {min(existing_limit, 50)}", clean_sql
                )
        else:
            clean_sql = f"{clean_sql} LIMIT {min(max_rows, 50)}"

        # Enforce C-driver read-only execution
        conn = get_db_connection(self.db_path, read_only=True)
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(clean_sql, params)
            else:
                cursor.execute(clean_sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def translate_requirements_to_filters(self, query: str) -> dict[str, Any]:
        """
        Translates natural language user requirements into typed schema slots.
        Grounded in smartphones datatypes and bounds.
        """
        q_l = query.lower()
        slots: dict[str, Any] = {
            "brand": None,
            "min_price": None,
            "max_price": None,
            "min_ram": None,
            "min_storage": None,
            "min_battery": None,
            "min_camera": None,
            "has_5g": None,
            "display_type": None,
            "min_refresh_rate": None,
            "processor_brand": None,
            "sort_by": "relevance",
            "search_term": None,
            "is_comparison": False,
            "extremum": None,
        }

        # 1. Brand extraction
        known_brands = [
            "samsung", "apple", "xiaomi", "oneplus", "realme", "vivo", "oppo",
            "motorola", "google", "nothing", "iqoo", "poco", "tecno", "infinix",
            "lava", "nokia", "honor", "micromax"
        ]
        for b in known_brands:
            if re.search(r"\b" + re.escape(b) + r"\b", q_l):
                slots["brand"] = "xiaomi" if b == "redmi" else b
                break

        # 2. Price extraction (INR ₹)
        price_norm = re.sub(r"₹|rs\.?|inr", " rupees ", q_l)
        price_norm = re.sub(r"\b(\d+)k\b", r"\g<1>000", price_norm)

        # Under / Below / Less than / Max price
        max_p_match = re.search(
            r"(?:under|below|not\s+above|less\s+than|upto|up\s+to|within|budget\s+of|<=|<)\s*(?:rupees)?\s*(\d{4,6})",
            price_norm,
        )
        if max_p_match:
            slots["max_price"] = int(max_p_match.group(1))

        # Above / Over / More than / Min price
        min_p_match = re.search(
            r"(?:above|over|more\s+than|min|minimum|starting\s+from|>=|>)\s*(?:rupees)?\s*(\d{4,6})",
            price_norm,
        )
        if min_p_match:
            slots["min_price"] = int(min_p_match.group(1))

        # Mid-budget heuristic
        if "mid budget" in q_l or "mid range" in q_l:
            slots["min_price"] = 15000
            slots["max_price"] = 35000

        # 3. RAM extraction (GB)
        ram_match = re.search(r"\b(\d{1,2})\s*(?:gb|gigs?)\s*(?:ram|memory)\b", q_l)
        if ram_match:
            slots["min_ram"] = float(ram_match.group(1))
        elif re.search(r"\b(?:8gb|12gb|16gb|24gb)\b", q_l):
            r_val = re.search(r"\b(\d{1,2})gb\b", q_l)
            if r_val:
                slots["min_ram"] = float(r_val.group(1))

        # 4. Storage extraction (GB)
        rom_match = re.search(r"\b(\d{2,4})\s*(?:gb|tb)\s*(?:storage|rom)\b", q_l)
        if rom_match:
            val = float(rom_match.group(1))
            slots["min_storage"] = val * 1024 if "tb" in rom_match.group(0) else val

        # 5. Battery extraction (mAh)
        bat_match = re.search(r"\b(\d{4})\s*(?:mah|battery)\b", q_l)
        if bat_match:
            slots["min_battery"] = int(bat_match.group(1))

        # 6. Camera extraction (MP)
        cam_match = re.search(r"\b(\d{2,3})\s*(?:mp|megapixel)\b", q_l)
        if cam_match:
            slots["min_camera"] = float(cam_match.group(1))

        # 7. 5G Network
        if re.search(r"\b5g\b", q_l) and not re.search(r"\b(non\s*5g|no\s*5g|4g\s*only)\b", q_l):
            slots["has_5g"] = "Yes"
        elif re.search(r"\b4g\b", q_l) and not re.search(r"\b5g\b", q_l):
            slots["has_5g"] = "No"

        # 8. Display & Refresh Rate
        if "amoled" in q_l:
            slots["display_type"] = "amoled display"
        elif "oled" in q_l:
            slots["display_type"] = "oled display"

        hz_match = re.search(r"\b(\d{2,3})\s*hz\b", q_l)
        if hz_match:
            slots["min_refresh_rate"] = float(hz_match.group(1))

        # 9. Processor Brand
        processors = ["snapdragon", "mediatek", "bionic", "tensor", "exynos", "unisoc"]
        for p in processors:
            if p in q_l:
                slots["processor_brand"] = p
                break

        # 10. Extremums & Sorting
        if any(w in q_l for w in ["least battery", "lowest battery", "min battery", "smallest battery"]):
            slots["sort_by"] = "battery_asc"
            slots["extremum"] = ("battery_cap", "ASC")
        elif any(w in q_l for w in ["highest battery", "longest battery", "max battery", "biggest battery"]):
            slots["sort_by"] = "battery_desc"
            slots["extremum"] = ("battery_cap", "DESC")
        elif any(w in q_l for w in ["least camera", "lowest camera", "least mp", "lowest mp"]):
            slots["sort_by"] = "camera_asc"
            slots["extremum"] = ("primary_rear_camera", "ASC")
        elif any(w in q_l for w in ["best camera", "highest camera", "top camera", "highest mp"]):
            slots["sort_by"] = "camera_desc"
            slots["extremum"] = ("primary_rear_camera", "DESC")
        elif any(w in q_l for w in ["lowest ram", "least ram", "min ram"]):
            slots["sort_by"] = "ram_asc"
            slots["extremum"] = ("ram", "ASC")
        elif any(w in q_l for w in ["highest ram", "hight ram", "max ram", "maximum ram", "most ram"]):
            slots["sort_by"] = "ram_desc"
            slots["extremum"] = ("ram", "DESC")
        elif any(w in q_l for w in ["cheapest", "lowest price", "least price", "sasta"]):
            slots["sort_by"] = "price_asc"
            slots["extremum"] = ("price", "ASC")
        elif any(w in q_l for w in ["most expensive", "costliest", "highest price", "flagship", "mahanga"]):
            slots["sort_by"] = "price_desc"
            slots["extremum"] = ("price", "DESC")

        # 11. Comparison check
        if any(w in q_l for w in ["compare", " vs ", "versus", "comparison", "difference"]):
            slots["is_comparison"] = True

        return slots

    def execute_agent_search(
        self,
        query: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Translates query requirements into schema-grounded SQL or SearchEngine parameters
        and returns matching products with schema telemetry.
        """
        slots = self.translate_requirements_to_filters(query)

        # Baseline modern RAM filter (4GB) for general advisory searches
        ram_filter = slots["min_ram"]
        is_lowest_extremum = (
            slots["sort_by"] in ["ram_asc", "battery_asc", "camera_asc", "price_asc"]
        )
        if (
            ram_filter is None
            and not is_lowest_extremum
            and (slots["max_price"] is None or slots["max_price"] >= 10000)
        ):
            ram_filter = 4.0

        # Execute search via SearchEngine
        search_res = self.search_engine.search(
            brand=slots["brand"],
            min_price=slots["min_price"],
            max_price=slots["max_price"],
            min_ram=ram_filter,
            min_battery=slots["min_battery"],
            min_camera=slots["min_camera"],
            has_5g=slots["has_5g"],
            sort_by=slots["sort_by"],
            limit=limit,
        )

        products = search_res.get("products", [])

        # If zero products found, try relaxed search by lifting RAM/Battery constraints
        relaxation_applied = False
        if not products and (ram_filter is not None or slots["min_battery"] is not None):
            relaxed_res = self.search_engine.search(
                brand=slots["brand"],
                min_price=slots["min_price"],
                max_price=slots["max_price"],
                has_5g=slots["has_5g"],
                sort_by=slots["sort_by"],
                limit=limit,
            )
            if relaxed_res.get("products"):
                products = relaxed_res["products"]
                relaxation_applied = True

        return {
            "products": products,
            "slots": slots,
            "total_matches": search_res.get("total_matches", len(products)),
            "relaxation_applied": relaxation_applied,
        }

    def generate_action_chips(
        self,
        query: str,
        products: list[dict[str, Any]],
        slots: dict[str, Any],
    ) -> list[str]:
        """
        Generates contextually intelligent follow-up recommendation chips
        for user interaction in the chat UI.
        """
        chips: list[str] = []
        q_l = query.lower()

        # 1. Product-specific comparison or detail chips
        if len(products) == 1:
            prod_name = products[0]["name"].title()
            chips.append(f"Compare {prod_name} with Galaxy S25")
            chips.append(f"Add {prod_name} to Cart")
            if products[0].get("has_5g") == "Yes":
                chips.append(f"Specs of {prod_name}")
        elif len(products) >= 2:
            chips.append(f"Compare {products[0]['name'].title()} vs {products[1]['name'].title()}")
            chips.append(f"Add {products[0]['name'].title()} to Cart")

        # 2. Budget exploration chips
        if slots.get("max_price"):
            current_max = slots["max_price"]
            if current_max <= 15000:
                chips.append("Best phones under ₹20,000")
                chips.append("5G phones under ₹15,000")
            elif current_max <= 30000:
                chips.append("Best camera phone under ₹25,000")
                chips.append("Top gaming phone under ₹30,000")
            else:
                chips.append("Compare flagship phones")
        else:
            chips.append("Under ₹20,000")
            chips.append("Best Camera Phone")

        # 3. Brand & Feature exploration chips
        if slots.get("brand"):
            brand_name = slots["brand"].title()
            chips.append(f"Top 5G {brand_name} phones")
            chips.append(f"Cheapest {brand_name} phone")
        else:
            if not any("5g" in c.lower() for c in chips):
                chips.append("5G Smartphones Only")

        # 4. Standard policy exploration chip if general inquiry
        if any(w in q_l for w in ["policy", "return", "warranty", "refund", "shipping"]):
            chips.append("7-day return policy details")
            chips.append("Check warranty coverage")
            chips.append("View payment & EMI options")

        # Deduplicate and return top 4
        unique_chips = []
        for c in chips:
            if c not in unique_chips and len(unique_chips) < 4:
                unique_chips.append(c)

        return unique_chips

    def format_agent_response(
        self,
        query: str,
        products: list[dict[str, Any]],
        slots: dict[str, Any],
        relaxation_applied: bool = False,
    ) -> str:
        """
        Formats user-facing answer enclosed strictly within <AnswerToUser> tags
        with clear, professional specifications and zero reasoning noise.
        """
        if not products:
            return (
                "<AnswerToUser>\n"
                f"I searched our catalog for **'{query}'**, but no smartphones matched all specified criteria. "
                "Try relaxing specific price limits or RAM requirements, or choose one of the recommended options below.\n"
                "</AnswerToUser>"
            )

        # Dual Extremes Comparison
        if len(products) >= 2 and (
            slots.get("is_comparison")
            or any(w in query.lower() for w in ["cheapest and most expensive", "sasta aur mahanga", "cheapest and priminum"])
        ):
            p1, p2 = products[0], products[1]
            return (
                "<AnswerToUser>\n"
                f"⚖️ Here is the comparison for your request:\n\n"
                f"1. **{p1['name'].title()}** — **₹{p1['price']:,}**\n"
                f"   - **Specs**: {p1['display_size']}\" {p1['display_type'].title()} | {int(p1['ram'])}GB RAM | "
                f"{p1['battery_cap']}mAh | {int(p1['primary_rear_camera'])}MP Camera | 5G: {p1['has_5g']}\n\n"
                f"2. **{p2['name'].title()}** — **₹{p2['price']:,}**\n"
                f"   - **Specs**: {p2['display_size']}\" {p2['display_type'].title()} | {int(p2['ram'])}GB RAM | "
                f"{p2['battery_cap']}mAh | {int(p2['primary_rear_camera'])}MP Camera | 5G: {p2['has_5g']}\n\n"
                "Both products are eligible for 7-day hassle-free replacement and manufacturer warranty."
                "\n</AnswerToUser>"
            )

        # Single or Multi-Product Recommendation
        top_p = products[0]
        ram_str = f"{top_p['ram']}GB RAM" if top_p["ram"] < 1 else f"{int(top_p['ram'])}GB RAM"
        cam_str = f"{int(top_p['primary_rear_camera'])}MP"

        intro = f"Found **{len(products)}** top smartphone{'s' if len(products) > 1 else ''} matching your requirements:"
        if relaxation_applied:
            intro = f"We adjusted strict filters slightly to bring you the best available option matching your budget:"

        lines = [f"<AnswerToUser>\n{intro}\n"]
        for idx, p in enumerate(products[:3], 1):
            p_ram = f"{p['ram']}GB RAM" if p["ram"] < 1 else f"{int(p['ram'])}GB RAM"
            p_cam = f"{int(p['primary_rear_camera'])}MP"
            lines.append(
                f"**{idx}. {p['name'].title()}** — **₹{p['price']:,}**\n"
                f"   - {p_ram} | {int(p['storage'])}GB Storage | {p['battery_cap']}mAh Battery | {p_cam} Camera | 5G: {p['has_5g']}"
            )

        lines.append("\nYou can add any of these models directly to your bag or tap a quick chip below to refine.")
        lines.append("</AnswerToUser>")
        return "\n".join(lines)


# Singleton agent instance
database_agent = DatabaseAgent()
