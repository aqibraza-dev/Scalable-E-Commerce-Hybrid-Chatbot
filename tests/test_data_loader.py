from src.data.loader import DataLoader, get_db_connection


def test_csv_reading_and_cleaning():
    loader = DataLoader()
    df = loader.get_dataframe()
    assert df is not None
    assert len(df) > 3000
    assert "brand" in df.columns
    assert "price" in df.columns
    assert "ram" in df.columns
    assert "has_5g" in df.columns

    # Null checks
    assert df["has_5g"].isnull().sum() == 0
    assert df["refresh_rate"].isnull().sum() == 0
    assert df["num_core"].isnull().sum() == 0

    # Value constraints
    assert (df["price"] >= 0).all()
    assert set(df["has_5g"].unique()).issubset({"Yes", "No"})


def test_database_initialization_and_indexes():
    loader = DataLoader()
    loader.initialize_database(force_reload=False)

    conn = get_db_connection()
    cur = conn.cursor()

    # Verify tables
    cur.execute("SELECT count(*) FROM smartphones")
    count = cur.fetchone()[0]
    assert count > 3000

    # Verify FTS table
    cur.execute("SELECT count(*) FROM smartphones_fts")
    fts_count = cur.fetchone()[0]
    assert fts_count == count

    # Verify indexes
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    index_names = [r[0] for r in cur.fetchall()]
    assert "idx_brand_price" in index_names
    assert "idx_price_ram_5g" in index_names
    assert "idx_battery" in index_names

    conn.close()
