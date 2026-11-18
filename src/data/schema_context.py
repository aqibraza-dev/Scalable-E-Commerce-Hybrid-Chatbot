"""
Database Schema & Datatypes Context Module for Shopcart AI.
Provides full, explicit schema documentation, data types, units,
and constraints for grounding LLM agents, SQL generation, and validation.
"""

from typing import Any

# Relational Table Schema for 'smartphones'
SMARTPHONES_TABLE_SCHEMA: dict[str, dict[str, Any]] = {
    "id": {
        "sql_type": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "python_type": "int",
        "description": "Unique smartphone product identifier",
        "unit": "id",
        "nullable": False,
        "indexed": True,
        "sample_values": [1, 105, 520],
    },
    "brand": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Canonical manufacturer brand name (lowercase)",
        "unit": "string",
        "nullable": False,
        "indexed": True,
        "sample_values": [
            "samsung", "apple", "xiaomi", "oneplus", "realme", "vivo",
            "oppo", "motorola", "google", "nothing", "iqoo", "poco",
            "tecno", "infinix", "lava", "nokia", "honor", "micromax"
        ],
    },
    "name": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Official commercial smartphone product model name",
        "unit": "string",
        "nullable": False,
        "indexed": True,
        "sample_values": [
            "Samsung Galaxy S25 Ultra 1TB",
            "Apple iPhone 15 Pro Max",
            "OnePlus 13 5G",
            "Realme P3 Pro 5G",
            "Motorola Edge 50 Fusion"
        ],
    },
    "price": {
        "sql_type": "INTEGER NOT NULL",
        "python_type": "int",
        "description": "Retail price in Indian Rupees (INR)",
        "unit": "INR (₹)",
        "nullable": False,
        "indexed": True,
        "min_value": 2500,
        "max_value": 200999,
        "sample_values": [9999, 14999, 24999, 59999, 129999],
    },
    "ram": {
        "sql_type": "REAL NOT NULL",
        "python_type": "float",
        "description": "Random Access Memory capacity in Gigabytes",
        "unit": "GB",
        "nullable": False,
        "indexed": True,
        "min_value": 0.25,
        "max_value": 24.0,
        "sample_values": [4.0, 6.0, 8.0, 12.0, 16.0, 24.0],
    },
    "os": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Mobile operating system platform",
        "unit": "category",
        "nullable": False,
        "indexed": False,
        "sample_values": ["android", "ios"],
    },
    "storage": {
        "sql_type": "REAL NOT NULL",
        "python_type": "float",
        "description": "Internal storage / ROM capacity in Gigabytes",
        "unit": "GB",
        "nullable": False,
        "indexed": False,
        "min_value": 4.0,
        "max_value": 1024.0,
        "sample_values": [32.0, 64.0, 128.0, 256.0, 512.0, 1024.0],
    },
    "battery_cap": {
        "sql_type": "INTEGER NOT NULL",
        "python_type": "int",
        "description": "Battery capacity in milliampere-hours",
        "unit": "mAh",
        "nullable": False,
        "indexed": True,
        "min_value": 1100,
        "max_value": 7000,
        "sample_values": [3000, 4500, 5000, 5500, 6000],
    },
    "has_fast_charging": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Quick charge / fast charging support",
        "unit": "boolean string",
        "nullable": False,
        "indexed": False,
        "sample_values": ["Yes", "No"],
    },
    "has_fingerprints": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Biometric fingerprint authentication scanner present",
        "unit": "boolean string",
        "nullable": False,
        "indexed": False,
        "sample_values": ["Yes", "No"],
    },
    "has_nfc": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Near Field Communication for contactless payments",
        "unit": "boolean string",
        "nullable": False,
        "indexed": False,
        "sample_values": ["Yes", "No"],
    },
    "has_5g": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "5G cellular network connectivity",
        "unit": "boolean string",
        "nullable": False,
        "indexed": True,
        "sample_values": ["Yes", "No"],
    },
    "processor_brand": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Chipset SoC processor manufacturer",
        "unit": "string",
        "nullable": False,
        "indexed": False,
        "sample_values": ["snapdragon", "mediatek", "bionic", "tensor", "exynos", "unisoc"],
    },
    "num_core": {
        "sql_type": "REAL NOT NULL",
        "python_type": "float",
        "description": "CPU processor core count",
        "unit": "cores",
        "nullable": False,
        "indexed": False,
        "sample_values": [4.0, 6.0, 8.0, 10.0],
    },
    "primary_rear_camera": {
        "sql_type": "REAL NOT NULL",
        "python_type": "float",
        "description": "Main primary rear camera sensor resolution in Megapixels",
        "unit": "MP",
        "nullable": False,
        "indexed": False,
        "min_value": 0.3,
        "max_value": 200.0,
        "sample_values": [12.0, 48.0, 50.0, 64.0, 108.0, 200.0],
    },
    "num_rear_cameras": {
        "sql_type": "INTEGER NOT NULL",
        "python_type": "int",
        "description": "Total count of rear camera lenses",
        "unit": "lenses",
        "nullable": False,
        "indexed": False,
        "sample_values": [1, 2, 3, 4],
    },
    "primary_front_camera": {
        "sql_type": "REAL NOT NULL",
        "python_type": "float",
        "description": "Front selfie camera resolution in Megapixels",
        "unit": "MP",
        "nullable": False,
        "indexed": False,
        "sample_values": [5.0, 8.0, 12.0, 16.0, 32.0, 50.0],
    },
    "num_front_camera": {
        "sql_type": "INTEGER NOT NULL",
        "python_type": "int",
        "description": "Total count of front selfie camera lenses",
        "unit": "lenses",
        "nullable": False,
        "indexed": False,
        "sample_values": [1, 2],
    },
    "display_size": {
        "sql_type": "REAL NOT NULL",
        "python_type": "float",
        "description": "Screen diagonal physical size in inches",
        "unit": "inches",
        "nullable": False,
        "indexed": False,
        "sample_values": [5.0, 6.1, 6.5, 6.67, 6.78, 6.82, 6.9],
    },
    "refresh_rate": {
        "sql_type": "REAL NOT NULL",
        "python_type": "float",
        "description": "Display refresh rate frequency in Hertz",
        "unit": "Hz",
        "nullable": False,
        "indexed": False,
        "sample_values": [60.0, 90.0, 120.0, 144.0, 165.0],
    },
    "display_type": {
        "sql_type": "TEXT NOT NULL",
        "python_type": "str",
        "description": "Screen display panel technology",
        "unit": "category",
        "nullable": False,
        "indexed": False,
        "sample_values": [
            "amoled display", "oled display", "lcd display", "tft display"
        ],
    },
}

# Full-Text Search Virtual Table
FTS_TABLE_SCHEMA: dict[str, Any] = {
    "table_name": "smartphones_fts",
    "engine": "FTS5",
    "indexed_columns": ["brand", "name", "processor_brand", "display_type"],
    "unindexed_columns": ["id"],
    "content_table": "smartphones",
    "content_rowid": "id",
    "scoring_algorithm": "BM25",
}

# Standardized formatted context block for LLM prompts and agent documentation
DATABASE_SCHEMA_CONTEXT: str = """
=== RELATIONAL DATABASE SCHEMA: `smartphones` ===
Table: smartphones (SQLite 3 with WAL Mode and PRAGMA query_only=ON)
Primary Key: id (INTEGER)

COLUMNS AND DATATYPES:
- id: INTEGER PRIMARY KEY (Product ID)
- brand: TEXT NOT NULL (Manufacturer brand in lowercase, e.g. 'samsung', 'apple', 'oneplus', 'realme', 'xiaomi', 'vivo', 'oppo', 'motorola', 'google', 'nothing', 'iqoo', 'poco')
- name: TEXT NOT NULL (Official model name, e.g. 'Samsung Galaxy S25 Ultra 1TB')
- price: INTEGER NOT NULL (Price in Indian Rupees, INR ₹, e.g. 19999, 129999)
- ram: REAL NOT NULL (RAM memory in GB, e.g. 4.0, 6.0, 8.0, 12.0, 16.0, 24.0)
- os: TEXT NOT NULL (Operating system, e.g. 'android', 'ios')
- storage: REAL NOT NULL (Storage in GB, e.g. 64.0, 128.0, 256.0, 512.0, 1024.0)
- battery_cap: INTEGER NOT NULL (Battery capacity in mAh, e.g. 4500, 5000, 6000)
- has_fast_charging: TEXT NOT NULL ('Yes' or 'No')
- has_fingerprints: TEXT NOT NULL ('Yes' or 'No')
- has_nfc: TEXT NOT NULL ('Yes' or 'No')
- has_5g: TEXT NOT NULL ('Yes' or 'No')
- processor_brand: TEXT NOT NULL (e.g. 'snapdragon', 'mediatek', 'bionic', 'tensor', 'exynos', 'unisoc')
- num_core: REAL NOT NULL (CPU cores, e.g. 8.0)
- primary_rear_camera: REAL NOT NULL (Main rear camera in MP, e.g. 50.0, 108.0, 200.0)
- num_rear_cameras: INTEGER NOT NULL (1 to 4)
- primary_front_camera: REAL NOT NULL (Selfie camera in MP, e.g. 16.0, 32.0, 50.0)
- num_front_camera: INTEGER NOT NULL (1 or 2)
- display_size: REAL NOT NULL (Screen diagonal in inches, e.g. 6.67, 6.78, 6.9)
- refresh_rate: REAL NOT NULL (Screen refresh rate in Hz, e.g. 60.0, 90.0, 120.0, 144.0)
- display_type: TEXT NOT NULL (e.g. 'amoled display', 'oled display', 'lcd display')

INDEXES:
- idx_brand_price on (brand, price)
- idx_price on (price)
- idx_price_ram_5g on (price, ram, has_5g)
- idx_battery on (battery_cap)
- idx_name on (name)
- FTS5 virtual table: smartphones_fts (BM25 full-text search)

SECURITY & QUERY EXECUTION RULES:
1. ONLY read-only SELECT queries are allowed. PRAGMA query_only=ON is physically enforced.
2. Mutation statements (INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE) are strictly blocked and rejected.
3. No comments (-- or /* */), no multi-statement semicolons (;), and no sqlite_master access.
4. Always apply LIMIT (maximum 50, default 3-10).
5. All prices are in INR (₹). '5G' requires `has_5g = 'Yes'`.
=================================================
""".strip()


def get_schema_summary() -> dict[str, Any]:
    """Returns structured summary of database schema."""
    return {
        "table_name": "smartphones",
        "column_count": len(SMARTPHONES_TABLE_SCHEMA),
        "columns": SMARTPHONES_TABLE_SCHEMA,
        "fts_virtual_table": FTS_TABLE_SCHEMA,
    }


def get_column_names() -> list[str]:
    """Returns list of valid column names in the smartphones table."""
    return list(SMARTPHONES_TABLE_SCHEMA.keys())


def is_valid_column(col_name: str) -> bool:
    """Checks whether a column exists in the smartphones schema."""
    return col_name.lower().strip() in SMARTPHONES_TABLE_SCHEMA
