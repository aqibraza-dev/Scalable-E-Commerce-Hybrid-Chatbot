import sqlite3
from pathlib import Path

import pandas as pd

from src.config import settings


class DataLoader:
    def __init__(self, csv_path: str | None = None, db_path: str | None = None):
        self.csv_path = Path(csv_path or settings.csv_path)
        self.db_path = Path(db_path or settings.sqlite_db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._df: pd.DataFrame | None = None

    def clean_dataset(self) -> pd.DataFrame:
        """Reads raw CSV, standardizes column names, cleans types and fills nulls."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found at {self.csv_path}")

        df = pd.read_csv(self.csv_path)

        # Standardize column names
        rename_map = {
            "brand_name": "brand",
            "Name": "name",
            "Price": "price",
            "RAM": "ram",
            "OS": "os",
            "storage": "storage",
            "Battery_cap": "battery_cap",
            "has_fast_charging": "has_fast_charging",
            "has_fingerprints": "has_fingerprints",
            "has_nfc": "has_nfc",
            "has_5g": "has_5g",
            "processor_brand": "processor_brand",
            "num_core": "num_core",
            "primery_rear_camera": "primary_rear_camera",
            "Num_Rear_Cameras": "num_rear_cameras",
            "primery_front_camera": "primary_front_camera",
            "num_front_camera": "num_front_camera",
            "display_size(inch)": "display_size",
            "refresh_rate(hz)": "refresh_rate",
            "display_types": "display_type",
        }
        df = df.rename(columns=rename_map)

        # String cleaning
        string_cols = ["brand", "name", "os", "processor_brand", "display_type"]
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()

        # Normalize brand names
        brand_corrections = {
            "moto": "motorola",
        }
        df["brand"] = df["brand"].replace(brand_corrections)
        df.loc[df["name"].str.startswith("nothing"), "brand"] = "nothing"

        # Fill missing values with business defaults
        df["has_5g"] = (
            df["has_5g"].fillna("No").astype(str).str.strip().str.capitalize()
        )
        df["has_fingerprints"] = (
            df["has_fingerprints"].fillna("No").astype(str).str.strip().str.capitalize()
        )
        df["has_nfc"] = (
            df["has_nfc"].fillna("No").astype(str).str.strip().str.capitalize()
        )
        df["has_fast_charging"] = (
            df["has_fast_charging"]
            .fillna("No")
            .astype(str)
            .str.strip()
            .str.capitalize()
        )

        df["refresh_rate"] = df["refresh_rate"].fillna(60.0).astype(float)
        df["num_core"] = df["num_core"].fillna(8.0).astype(float)

        # Numeric conversions
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).astype(int)
        df["ram"] = pd.to_numeric(df["ram"], errors="coerce").fillna(4.0).astype(float)
        df["storage"] = (
            pd.to_numeric(df["storage"], errors="coerce").fillna(64.0).astype(float)
        )
        df["battery_cap"] = (
            pd.to_numeric(df["battery_cap"], errors="coerce").fillna(5000).astype(int)
        )
        df["primary_rear_camera"] = (
            pd.to_numeric(df["primary_rear_camera"], errors="coerce")
            .fillna(12.0)
            .astype(float)
        )
        df["primary_front_camera"] = (
            pd.to_numeric(df["primary_front_camera"], errors="coerce")
            .fillna(8.0)
            .astype(float)
        )
        df["display_size"] = (
            pd.to_numeric(df["display_size"], errors="coerce").fillna(6.5).astype(float)
        )

        # Reset index to create unique integer ID
        df = df.reset_index(drop=True)
        df["id"] = df.index + 1

        self._df = df
        return df

    def initialize_database(self, force_reload: bool = False) -> None:
        """Initializes SQLite schema, B-tree indexes, and FTS5 full-text search table."""
        df = self.clean_dataset()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if table already exists with data
        cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='smartphones'"
        )
        table_exists = cursor.fetchone()[0] > 0

        if table_exists and not force_reload:
            cursor.execute("SELECT count(*) FROM smartphones")
            count = cursor.fetchone()[0]
            if count > 0:
                conn.close()
                return

        # Drop tables if force reloading
        cursor.execute("DROP TABLE IF EXISTS smartphones_fts")
        cursor.execute("DROP TABLE IF EXISTS smartphones")

        # Create structured relational table with constraints
        cursor.execute("""
            CREATE TABLE smartphones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                ram REAL NOT NULL,
                os TEXT NOT NULL,
                storage REAL NOT NULL,
                battery_cap INTEGER NOT NULL,
                has_fast_charging TEXT NOT NULL,
                has_fingerprints TEXT NOT NULL,
                has_nfc TEXT NOT NULL,
                has_5g TEXT NOT NULL,
                processor_brand TEXT NOT NULL,
                num_core REAL NOT NULL,
                primary_rear_camera REAL NOT NULL,
                num_rear_cameras INTEGER NOT NULL,
                primary_front_camera REAL NOT NULL,
                num_front_camera INTEGER NOT NULL,
                display_size REAL NOT NULL,
                refresh_rate REAL NOT NULL,
                display_type TEXT NOT NULL
            )
        """)

        # Insert cleaned records
        cols = [
            "id",
            "brand",
            "name",
            "price",
            "ram",
            "os",
            "storage",
            "battery_cap",
            "has_fast_charging",
            "has_fingerprints",
            "has_nfc",
            "has_5g",
            "processor_brand",
            "num_core",
            "primary_rear_camera",
            "num_rear_cameras",
            "primary_front_camera",
            "num_front_camera",
            "display_size",
            "refresh_rate",
            "display_type",
        ]
        records = df[cols].values.tolist()
        placeholders = ",".join(["?"] * len(cols))
        cursor.executemany(
            f"INSERT INTO smartphones ({','.join(cols)}) VALUES ({placeholders})",
            records,
        )

        # High-performance B-Tree indexes for fast OLTP search queries
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_brand_price ON smartphones(brand, price)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price ON smartphones(price)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_price_ram_5g ON smartphones(price, ram, has_5g)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_battery ON smartphones(battery_cap)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON smartphones(name)")

        # Create SQLite FTS5 (Full-Text Search) virtual table for BM25 ranking
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS smartphones_fts USING fts5(
                id UNINDEXED,
                brand,
                name,
                processor_brand,
                display_type,
                content='smartphones',
                content_rowid='id'
            )
        """)
        cursor.execute("""
            INSERT INTO smartphones_fts(id, brand, name, processor_brand, display_type)
            SELECT id, brand, name, processor_brand, display_type FROM smartphones
        """)

        conn.commit()
        conn.close()

    def get_dataframe(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.clean_dataset()
        return self._df


def get_db_connection(
    db_path: str | None = None,
    read_only: bool = True
) -> sqlite3.Connection:
    """
    Returns thread-safe SQLite connection configured for high-concurrency (WAL mode).
    Enforces driver-level read-only protection (PRAGMA query_only = ON) by default
    to physically prevent SQL injection mutations (DROP, DELETE, UPDATE, ALTER).
    """
    target_path = db_path or settings.sqlite_db_path
    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    if read_only:
        conn.execute("PRAGMA query_only = ON")
    return conn
