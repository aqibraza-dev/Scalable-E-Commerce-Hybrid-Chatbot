from src.chatbot.semantic_cache import SemanticCache


def test_semantic_cache_exact_and_semantic_matching():
    cache = SemanticCache(threshold=0.75)
    cache.clear()

    # Store initial response
    query_orig = "What is the best 5G phone under 20000?"
    response_orig = "Top 5G phones under ₹20,000 include Realme P3 Pro and Vivo T3 Pro."
    cache.store(query_orig, response_orig, prompt_tokens=250, completion_tokens=100)

    # 1. Exact match test
    hit_exact = cache.lookup("What is the best 5G phone under 20000?")
    assert hit_exact is not None
    assert hit_exact["cache_hit"] is True
    assert hit_exact["cache_type"] == "exact_cache"
    assert hit_exact["similarity_score"] == 1.0
    assert hit_exact["tokens_saved"] == 350

    # 2. Semantic paraphrasing variations
    sim_query_1 = "suggest top 5g mobile below 20000"
    hit_sim_1 = cache.lookup(sim_query_1)
    assert hit_sim_1 is not None
    assert hit_sim_1["cache_hit"] is True
    assert hit_sim_1["similarity_score"] >= 0.75
    assert hit_sim_1["tokens_saved"] == 350

    sim_query_2 = "which 5g phones under 20k are best"
    hit_sim_2 = cache.lookup(sim_query_2)
    assert hit_sim_2 is not None
    assert hit_sim_2["cache_hit"] is True
    assert hit_sim_2["similarity_score"] >= 0.75

    # 3. Unrelated query (should miss)
    miss_query = "How to cook pasta carbonara at home?"
    hit_miss = cache.lookup(miss_query)
    assert hit_miss is None


def test_semantic_cache_slot_isolation_brand_and_price():
    cache = SemanticCache(threshold=0.70)
    cache.clear()

    # Store generic response
    cache.store(
        "recommend best phone under 20000", "Generic phones: Realme, Poco, Vivo"
    )

    # Query with specific brand (Apple) must NOT match the generic cached entry
    hit_apple = cache.lookup("recommend best apple phone under 20000")
    assert hit_apple is None, "Generic cache should not leak to Apple query"

    # Store Samsung response
    cache.store(
        "recommend best samsung phone under 20000",
        "Samsung phones: Galaxy A15, Galaxy M15",
    )

    # Apple query must still not match Samsung
    assert cache.lookup("recommend best apple phone under 20000") is None

    # Paraphrased Samsung query should match Samsung
    hit_sam = cache.lookup("suggest top samsung mobile below 20000")
    assert hit_sam is not None
    assert "Galaxy" in hit_sam["response"]

    # Different price bracket must NOT match
    hit_expensive = cache.lookup("suggest top samsung mobile below 60000")
    assert hit_expensive is None, "20k cache must not match 60k query"


def test_semantic_cache_battery_not_extracted_as_price():
    cache = SemanticCache()
    slots = cache.extract_slots("phone with 5000mah battery snapdragon")
    assert slots["price"] is None, (
        "5000mAh battery capacity must not be tagged as price"
    )
    assert slots["brand"] is None


def test_semantic_cache_stats():
    cache = SemanticCache()
    stats = cache.get_stats()
    assert "semantic_entries_count" in stats
    assert "threshold" in stats
