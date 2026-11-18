from src.chatbot.typical_bot import TypicalChatbot


def test_typical_bot_greeting():
    bot = TypicalChatbot()
    res = bot.process("Hello assistant!")
    assert res["intent"] == "GREETING"
    assert "Smart E-Commerce Assistant" in res["response"]
    assert res["tokens_used"] == 0


def test_typical_bot_policies():
    bot = TypicalChatbot()
    # Return policy
    res1 = bot.process("What is the return policy?")
    assert res1["intent"] == "POLICY_RETURN"
    assert "7-Day" in res1["response"]
    assert res1["tokens_used"] == 0

    # Warranty
    res2 = bot.process("Tell me about phone warranty")
    assert res2["intent"] == "POLICY_WARRANTY"
    assert "1-Year" in res2["response"]

    # Shipping
    res3 = bot.process("How long does delivery shipping take?")
    assert res3["intent"] == "POLICY_SHIPPING"
    assert "Express Delivery" in res3["response"]


def test_typical_bot_comparison():
    bot = TypicalChatbot()
    res = bot.process("Compare vivo v50 and realme p3 pro")
    assert res["intent"] == "COMPARISON"
    assert "Comparison" in res["response"]
    assert "vivo v50" in res["response"].lower()
    assert "realme p3 pro" in res["response"].lower()
    assert res["tokens_used"] == 0


def test_typical_bot_search_slot_extraction():
    bot = TypicalChatbot()
    slots = bot.extract_slots(
        "Find me samsung 5g phones under 25000 with 8gb ram and 6000mah battery"
    )
    assert slots["brand"] == "samsung"
    assert slots["has_5g"] == "Yes"
    assert slots["max_price"] == 25000
    assert slots["min_ram"] == 8.0
    assert slots["min_battery"] == 6000

    res = bot.process("Find me samsung 5g phones under 25000 with 8gb ram")
    assert res["intent"] == "PRODUCT_SEARCH"
    assert len(res["products"]) > 0
    assert res["tokens_used"] == 0


def test_typical_bot_generic_search_without_brand():
    bot = TypicalChatbot()
    # Query suggested in bot greeting
    res = bot.process("Find 5G phones under ₹25,000 with 8GB RAM")
    assert res["intent"] == "PRODUCT_SEARCH"
    assert len(res["products"]) > 0
    assert "Found" in res["response"]
    assert res["tokens_used"] == 0
    for p in res["products"]:
        assert p["has_5g"] == "Yes"
        assert p["price"] <= 25000
        assert p["ram"] >= 8.0


def test_typical_bot_negation_handling():
    bot = TypicalChatbot()
    res = bot.process("Find phones that are not 5g and not above 20000")
    assert res["intent"] == "PRODUCT_SEARCH"
    assert len(res["products"]) > 0
    for p in res["products"]:
        assert p["has_5g"] == "No"
        assert p["price"] <= 20000


def test_typical_bot_persona_faq():
    bot = TypicalChatbot()
    for q in ["who are you", "who build you", "who created you", "what can you do"]:
        res = bot.process(q)
        assert res["intent"] == "PERSONA_FAQ"
        assert "Shopcart AI" in res["response"]
        assert res["tokens_used"] == 0


def test_typical_bot_out_of_domain():
    bot = TypicalChatbot()
    for q in ["what is the capital of france", "write python script for fibonacci"]:
        res = bot.process(q)
        assert res["intent"] == "OUT_OF_DOMAIN"
        assert "specialized as a smartphone shopping assistant" in res["response"]
        assert res["tokens_used"] == 0


def test_typical_bot_concept_and_extremes_comparison():
    bot = TypicalChatbot()
    # Query with typo "priminum"
    res = bot.process("compare cheapest and priminum phones")
    assert res["intent"] in ["EXTREMES_COMPARISON", "COMPARISON"]
    assert len(res["products"]) == 2
    assert "Comparison" in res["response"]
    assert res["tokens_used"] == 0
    # One budget, one flagship
    prices = [p["price"] for p in res["products"]]
    assert min(prices) < 5000
    assert max(prices) > 50000


def test_typical_bot_used_phone_return_policy():
    bot = TypicalChatbot()
    # Query with typo "weather" for "whether" and asking about returning after 7 days
    res = bot.process("weather i can give back if is used the phone for more than 7 days")
    assert res["intent"] == "POLICY_RETURN_DAYS"
    assert "7-Day" in res["response"]
    assert "1-Year" in res["response"]
    assert "Manufacturer Warranty" in res["response"]
    assert res["tokens_used"] == 0


def test_typical_bot_benefits_inquiry():
    bot = TypicalChatbot()
    # Query with typo "moto edgee 50"
    res = bot.process("benefits of moto edgee 50")
    assert res["intent"] == "BENEFITS_INQUIRY"
    assert len(res["products"]) == 1
    assert "Motorola Edge 50" in res["response"]
    assert "Key Benefits" in res["response"]
    assert res["tokens_used"] == 0


def test_typical_bot_camera_phone_ranking():
    bot = TypicalChatbot()
    res = bot.process("best camera phone under 10k rupees")
    assert res["intent"] == "PRODUCT_SEARCH"
    assert len(res["products"]) > 0
    first_phone = res["products"][0]
    # Under 10k, top camera phones should have >= 50MP, not 5MP!
    assert first_phone["primary_rear_camera"] >= 50.0
    assert first_phone["price"] <= 10000


def test_typical_bot_small_talk():
    bot = TypicalChatbot()
    for q in ["how are you", "thank you so much", "good morning", "thanks"]:
        res = bot.process(q)
        assert res["intent"] == "SMALL_TALK"
        assert res["tokens_used"] == 0
        assert len(res["products"]) == 0


def test_typical_bot_out_of_domain_expanded():
    bot = TypicalChatbot()
    for q in [
        "what is the capital of france",
        "write python script for fibonacci",
        "tell me a joke",
        "what is the weather today",
    ]:
        res = bot.process(q)
        assert res["intent"] == "OUT_OF_DOMAIN"
        assert "specialized" in res["response"]
        assert len(res["products"]) == 0


def test_typical_bot_hinglish_price_queries():
    bot = TypicalChatbot()
    for q in [
        "10000 me best camera phone",
        "10 hazar me sabse accha camera phone",
        "10k ke andar best camera phone",
    ]:
        res = bot.process(q)
        assert res["intent"] == "PRODUCT_SEARCH"
        assert len(res["products"]) > 0
        first_phone = res["products"][0]
        assert first_phone["price"] <= 10000
        assert first_phone["primary_rear_camera"] >= 50.0


def test_typical_bot_mid_budget_camera():
    bot = TypicalChatbot()
    res = bot.process("best camera phone under mid budget")
    assert res["intent"] == "PRODUCT_SEARCH"
    assert len(res["products"]) > 0
    first_phone = res["products"][0]
    assert 15000 <= first_phone["price"] <= 35000
    assert first_phone["primary_rear_camera"] >= 100.0


def test_typical_bot_subjective_advisory():
    bot = TypicalChatbot()
    queries = [
        "I am a college student who loves night photography and vlogging, recommend a phone under 35000.",
        "Need a durable smartphone for outdoor construction work with maximum battery life.",
        "Which phone has the cleanest software UI and best gaming performance under 40000?",
        "Suggest a gift phone for my mother who needs simple interface and big screen under 15k.",
    ]
    for q in queries:
        assert bot.classify_intent(q) == "SUBJECTIVE_ADVISORY"
        res = bot.process(q)
        assert len(res["products"]) > 0


def test_typical_bot_extremum_queries_and_concept_comparisons():
    bot = TypicalChatbot()

    # 1. Compare best samsung phone with best iphhone (typo + concept comparison)
    res_comp = bot.process("compare best samsung phone with best iphhone")
    assert res_comp["intent"] == "COMPARISON"
    assert len(res_comp["products"]) == 2
    names = [p["brand"] for p in res_comp["products"]]
    assert "samsung" in names
    assert "apple" in names

    # 2. Which phone has least battery
    res_bat = bot.process("which phone has least battery")
    assert res_bat["intent"] == "PRODUCT_SEARCH"
    assert len(res_bat["products"]) > 0
    assert res_bat["products"][0]["battery_cap"] <= 1200

    # 3. Which phone has least mp camera
    res_cam = bot.process("which phone has least mp camera")
    assert res_cam["intent"] == "PRODUCT_SEARCH"
    assert len(res_cam["products"]) > 0
    assert res_cam["products"][0]["primary_rear_camera"] <= 2.0

    # 4. Lowest ram phone
    res_ram_low = bot.process("lowest ram phone")
    assert res_ram_low["intent"] == "PRODUCT_SEARCH"
    assert len(res_ram_low["products"]) > 0
    assert res_ram_low["products"][0]["ram"] <= 1.0

    # 5. Hight ram phone (typo 'hight' for highest)
    res_ram_high = bot.process("hight ram phone")
    assert res_ram_high["intent"] == "PRODUCT_SEARCH"
    assert len(res_ram_high["products"]) > 0
    assert res_ram_high["products"][0]["ram"] >= 18.0

    # 6. Least battery oneplus phone
    res_oneplus = bot.process("least battery oneplus phone")
    assert len(res_oneplus["products"]) > 0
    assert res_oneplus["products"][0]["brand"] == "oneplus"
    assert res_oneplus["products"][0]["battery_cap"] <= 3500


def test_typical_bot_longest_battery_life_stopword():
    bot = TypicalChatbot()
    res = bot.process("longest battery life phone")
    assert len(res["products"]) > 0
    # Must return top battery phone (>= 20,000 mAh), NOT stk life plus s (2800 mAh)!
    assert res["products"][0]["battery_cap"] >= 20000


def test_typical_bot_memory_query():
    bot = TypicalChatbot()
    res = bot.process("lowest memory phone")
    assert len(res["products"]) > 0
    assert res["products"][0]["ram"] <= 1.0


def test_typical_bot_nothing_phone_comparison():
    bot = TypicalChatbot()
    res = bot.process("compare Nothing Phone 2 with Google Pixel 8")
    assert res["intent"] == "COMPARISON"
    assert len(res["products"]) == 2
    brands = [p["brand"] for p in res["products"]]
    assert "nothing" in brands
    assert "google" in brands


def test_typical_bot_extremum_answer_clarity():
    bot = TypicalChatbot()
    res = bot.process("which phone has least battery")
    assert "lowest battery capacity" in res["response"].lower()
    assert "karbonn" in res["response"].lower()
    assert "1100" in res["response"]


def test_typical_bot_spec_inquiry_pixel_8():
    bot = TypicalChatbot()
    intent = bot.classify_intent("what is the price of pixel 8")
    assert intent == "SPEC_INQUIRY"
    res = bot.process("what is the price of pixel 8")
    assert len(res["products"]) == 1
    assert "pixel 8" in res["products"][0]["name"].lower()
    assert "Specifications" in res["response"]


def test_typical_bot_spec_inquiry_iphone_15_battery():
    bot = TypicalChatbot()
    intent = bot.classify_intent("battery of iphone 15")
    assert intent == "SPEC_INQUIRY"
    res = bot.process("battery of iphone 15")
    assert len(res["products"]) == 1
    assert res["products"][0]["name"].lower() == "apple iphone 15"
    assert res["products"][0]["battery_cap"] == 3349


def test_typical_bot_spec_inquiry_nonexistent_returns_empty_products():
    bot = TypicalChatbot()
    intent = bot.classify_intent("what is the battery of nokia 3310")
    assert intent == "SPEC_INQUIRY"
    res = bot.process("what is the battery of nokia 3310")
    # Must report empty products so orchestrator falls back to LLM instead of returning wrong phone
    assert len(res["products"]) == 0
    assert "Could not find specifications" in res["response"]






