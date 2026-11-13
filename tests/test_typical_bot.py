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


def test_typical_bot_extremes_comparison():
    bot = TypicalChatbot()
    res = bot.process("sabse sasta aur mahanga phone dikhao")
    assert res["intent"] == "EXTREMES_COMPARISON"
    assert len(res["products"]) == 2
    assert "Sabse Sasta" in res["response"]
    assert "Sabse Mahanga" in res["response"]
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



