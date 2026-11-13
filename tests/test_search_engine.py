from src.search.cache import global_cache
from src.search.engine import SearchEngine


def test_search_basic():
    engine = SearchEngine()
    res = engine.search(query="samsung", limit=5)
    assert res["total_matches"] > 0
    assert len(res["products"]) <= 5
    assert all(
        "samsung" in p["name"].lower() or p["brand"] == "samsung"
        for p in res["products"]
    )


def test_search_multi_filtering():
    engine = SearchEngine()
    res = engine.search(
        brand="samsung", min_price=10000, max_price=30000, min_ram=6.0, has_5g="Yes"
    )
    assert res["total_matches"] > 0
    for p in res["products"]:
        assert p["brand"] == "samsung"
        assert 10000 <= p["price"] <= 30000
        assert p["ram"] >= 6.0
        assert p["has_5g"] == "Yes"


def test_search_sorting():
    engine = SearchEngine()
    # Price ascending
    res_asc = engine.search(brand="xiaomi", sort_by="price_asc", limit=5)
    prices_asc = [p["price"] for p in res_asc["products"]]
    assert prices_asc == sorted(prices_asc)

    # Price descending
    res_desc = engine.search(brand="xiaomi", sort_by="price_desc", limit=5)
    prices_desc = [p["price"] for p in res_desc["products"]]
    assert prices_desc == sorted(prices_desc, reverse=True)


def test_search_caching():
    global_cache.clear()
    engine = SearchEngine()
    # First call: miss
    r1 = engine.search(query="vivo", min_price=15000, max_price=25000)
    assert r1["from_cache"] is False

    # Second call: hit
    r2 = engine.search(query="vivo", min_price=15000, max_price=25000)
    assert r2["from_cache"] is True
    assert r2["total_matches"] == r1["total_matches"]
    assert (
        r2["execution_time_ms"] <= r1["execution_time_ms"]
        or r2["execution_time_ms"] < 2.0
    )


def test_search_typo_correction():
    engine = SearchEngine()
    res = engine.search(query="samusng galaxy", limit=3)
    assert res["total_matches"] > 0
    assert any(p["brand"] == "samsung" for p in res["products"])


def test_compare_products():
    engine = SearchEngine()
    comp = engine.compare_products("vivo v50", "realme p3 pro")
    assert comp["found_both"] is True
    assert comp["product_a"]["name"] == "vivo v50"
    assert comp["product_b"]["name"] == "realme p3 pro"


def test_natural_language_search_with_currency_and_specs():
    engine = SearchEngine()
    engine.cache.clear()
    # Natural language query with currency symbols and commas
    res = engine.search(query="Find 5G phones under ₹25,000 with 8GB RAM", limit=5)
    assert res["total_matches"] > 0
    assert len(res["products"]) > 0
    for p in res["products"]:
        assert p["has_5g"] == "Yes"
        assert p["price"] <= 25000
        assert p["ram"] >= 8.0


def test_negation_filters_in_search():
    engine = SearchEngine()
    res = engine.search(query="phones that are not 5g and not above 20000", limit=5)
    assert res["total_matches"] > 0
    for p in res["products"]:
        assert p["has_5g"] == "No"
        assert p["price"] <= 20000


def test_product_price_update_and_cache_invalidation():
    engine = SearchEngine()
    engine.cache.clear()

    # Get a phone by ID
    p_orig = engine.get_by_id(1)
    orig_price = p_orig["price"]
    test_price = orig_price + 500

    # Populate cache
    cached_first = engine.get_by_id(1)
    assert cached_first["price"] == orig_price

    # Update price
    success = engine.update_product_price(1, test_price)
    assert success is True

    # Lookup again - cache must be invalidated and reflect new price
    p_updated = engine.get_by_id(1)
    assert p_updated["price"] == test_price

    # Restore original price
    engine.update_product_price(1, orig_price)
