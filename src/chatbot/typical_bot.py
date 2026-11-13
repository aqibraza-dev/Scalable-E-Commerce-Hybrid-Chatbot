import re
import time
from typing import Any

from src.search.engine import SearchEngine


class TypicalChatbot:
    """
    Deterministic E-Commerce Chatbot (Rule / Intent / SQL-Driven).
    Executes in < 3ms with ZERO LLM token consumption ($0.00 cost).
    Handles structured product search, spec lookups, comparisons, and policy FAQs.
    """
    POLICIES = {
        "return": (
            "📦 **Return & Refund Policy**:\n"
            "- 7-Day Hassle-Free Replacement/Return for all mobile phones.\n"
            "- Device must be returned in original box with all accessories and IMEI intact.\n"
            "- Refunds are initiated to original payment method within 3-5 business days."
        ),
        "warranty": (
            "🛡️ **Warranty Coverage**:\n"
            "- 1-Year Comprehensive Manufacturer Warranty on all new smartphones.\n"
            "- 6-Month In-Box Accessories Warranty (charger, cable, earphones).\n"
            "- Serviceable at any authorized brand service center pan-India."
        ),
        "shipping": (
            "🚚 **Shipping & Delivery**:\n"
            "- Free Express Delivery on orders above ₹499.\n"
            "- Standard delivery within 24 to 48 hours in metro cities; 3-4 days nationwide.\n"
            "- Real-time SMS and email tracking updates provided."
        ),
        "emi": (
            "💳 **Payment & EMI Options**:\n"
            "- No-Cost EMI available for 3, 6, and 9 months on major credit cards and Bajaj Finserv.\n"
            "- Up to ₹3,000 instant bank discount on select credit/debit card transactions."
        )
    }

    BRANDS = [
        "samsung", "apple", "xiaomi", "vivo", "oppo", "oneplus",
        "realme", "motorola", "iqoo", "poco", "tecno", "lava",
        "infinix", "google", "nothing"
    ]

    def __init__(self, search_engine: SearchEngine | None = None):
        self.search_engine = search_engine or SearchEngine()

    def extract_slots(self, text: str) -> dict[str, Any]:
        """Extracts structured search parameters (brand, budget, RAM, 5G, battery) from text."""
        slots, _ = self.search_engine.parse_query_slots(text)
        return slots

    def classify_intent(self, text: str) -> str:
        """Classifies query into high-level intent."""
        t = text.lower().strip()

        # Persona & Bot Identity FAQ
        persona_patterns = [
            r"\bwho\s+are\s+you\b",
            r"\bwho\s+(?:built|build|created|made|developed)\s+you\b",
            r"\bwhat\s+(?:are\s+you|is\s+your\s+name)\b",
            r"\btell\s+me\s+about\s+yourself\b",
            r"\bwhat\s+can\s+you\s+do\b",
            r"\bwho\s+is\s+your\s+creator\b",
            r"\bwho\s+owns\s+you\b",
        ]
        if any(re.search(p, t) for p in persona_patterns):
            return "PERSONA_FAQ"

        # General Trivia / Out-of-Domain questions
        out_of_domain_patterns = [
            r"\bcapital\s+of\b",
            r"\bpresident\s+of\b",
            r"\bprime\s+minister\b",
            r"\bpoem\s+about\b",
            r"\bwrite\s+(?:python|code|script|essay|story)\b",
            r"\bsolve\s+(?:math|equation)\b",
            r"\bweather\s+in\b",
            r"\bwho\s+won\s+the\s+world\s+cup\b",
        ]
        if any(re.search(p, t) for p in out_of_domain_patterns):
            return "OUT_OF_DOMAIN"

        # Hinglish / English Dual Extremes ("sabse sasta aur mahanga")
        if re.search(
            r"\b(?:sabse\s+)?sasta\s+aur\s+(?:sabse\s+)?mahanga\b|\bcheapest\s+and\s+most\s+expensive\b|\bsasta\s+aur\s+mahanga\b",
            t,
        ):
            return "EXTREMES_COMPARISON"

        # Greeting intent
        if re.match(r"^(hi|hello|hey|greetings|howdy)\b", t):
            return "GREETING"

        # Policy FAQs
        if any(w in t for w in ["return", "refund", "exchange", "replace"]):
            return "POLICY_RETURN"
        if any(w in t for w in ["warranty", "guarantee"]):
            return "POLICY_WARRANTY"
        if any(w in t for w in ["delivery", "shipping", "courier", "track"]):
            return "POLICY_SHIPPING"
        if any(w in t for w in ["emi", "installment", "finance", "discount"]):
            return "POLICY_EMI"

        # Comparison intent ("compare X and Y", "X vs Y", "chart comparing X and Y")
        if (
            "compare" in t
            or " vs " in t
            or " versus " in t
            or "comparison" in t
            or (("chart" in t or "charts" in t) and (" and " in t or " vs " in t))
        ):
            return "COMPARISON"

        # Check if query is a catalog search query
        is_search_intent = any(
            w in t
            for w in [
                "phones",
                "mobiles",
                "devices",
                "under",
                "below",
                "between",
                "less than",
                "cheapest",
                "find me",
                "show me",
                "suggest",
                "recommend",
            ]
        )

        if not is_search_intent:
            # Spec inquiry ("what is the battery of X", "camera of Y", "specs of Z", "details of W")
            spec_terms = [
                "battery",
                "camera",
                "display",
                "screen",
                "processor",
                "spec",
                "specs",
                "specification",
                "specifications",
            ]
            has_spec_term = any(w in t for w in spec_terms)
            has_inquiry_starter = any(
                t.startswith(prefix)
                for prefix in [
                    "what is the",
                    "what are the",
                    "what is its",
                    "what is",
                    "how is the",
                    "how is its",
                    "how is",
                    "display of",
                    "spec of",
                    "specs of",
                    "tell me about",
                    "details of",
                    "camera of",
                    "battery of",
                    "price of",
                ]
            )
            has_brand = any(b in t for b in self.BRANDS)

            if (
                (has_spec_term and has_brand)
                or (has_inquiry_starter and has_brand)
                or any(
                    t.startswith(prefix)
                    for prefix in [
                        "what is the battery",
                        "what is the camera",
                        "display of",
                        "spec of",
                        "specs of",
                    ]
                )
            ):
                return "SPEC_INQUIRY"

        # Default to product search
        return "PRODUCT_SEARCH"

    def process(self, query: str) -> dict[str, Any]:
        """Processes query deterministically, returning structured answer with zero LLM tokens."""
        start_time = time.perf_counter()
        intent = self.classify_intent(query)
        response_text = ""
        products = []

        if intent == "PERSONA_FAQ":
            response_text = (
                "👋 I am **Shopcart AI**, your intelligent e-commerce shopping advisor!\n\n"
                "I was built by the Shopcart Engineering team to help you discover, compare, and find "
                "the perfect smartphone at the best price.\n\n"
                "**Here is what I can do for you:**\n"
                "- ⚡ **Instant Search**: Find phones by budget, RAM, camera, battery, or 5G.\n"
                "- ⚖️ **Side-by-Side Comparison**: Compare specs of any two smartphones.\n"
                "- 🛒 **Shopping & Cart**: Add recommendations directly to your cart with one tap.\n"
                "- 📦 **Policies & FAQs**: Answer queries about warranties, 7-day returns, and EMI options."
            )

        elif intent == "OUT_OF_DOMAIN":
            response_text = (
                "I am specialized as a smartphone shopping assistant for Shopcart. "
                "I cannot answer general trivia outside of smartphones, tech specifications, and e-commerce shopping.\n\n"
                "Would you like me to help you find the best smartphone for your budget or camera needs?"
            )

        elif intent == "EXTREMES_COMPARISON":
            cheap_res = self.search_engine.search(sort_by="price_asc", limit=1)
            flag_res = self.search_engine.search(sort_by="price_desc", limit=1)
            p_cheap = cheap_res["products"][0] if cheap_res["products"] else None
            p_flag = flag_res["products"][0] if flag_res["products"] else None
            products = [p for p in [p_cheap, p_flag] if p]
            if p_cheap and p_flag:
                response_text = (
                    "📊 **Sabse Sasta (Cheapest) vs Sabse Mahanga (Ultra Flagship) Phone**:\n\n"
                    f"**1. Sabse Sasta**: **{p_cheap['name'].title()}** — **₹{p_cheap['price']:,}**\n"
                    f"   - {int(p_cheap['ram'])}GB RAM | {p_cheap['battery_cap']}mAh | {int(p_cheap['primary_rear_camera'])}MP Camera | 5G: {p_cheap['has_5g']}\n\n"
                    f"**2. Sabse Mahanga**: **{p_flag['name'].title()}** — **₹{p_flag['price']:,}**\n"
                    f"   - {int(p_flag['ram'])}GB RAM | {p_flag['battery_cap']}mAh | {int(p_flag['primary_rear_camera'])}MP Camera | 5G: {p_flag['has_5g']}\n\n"
                    "Both smartphones are available with instant checkout and 7-day return guarantee!"
                )
            else:
                response_text = "Catalog currently does not contain matching smartphones."

        elif intent == "GREETING":
            response_text = (
                "👋 Hello! I am your Smart E-Commerce Assistant. I can help you find smartphones, "
                "compare models, check specifications, or answer policy questions.\n\n"
                "**Try asking:**\n"
                "- *'Find 5G phones under ₹25,000 with 8GB RAM'*\n"
                "- *'Compare Samsung Galaxy S25 Ultra and OnePlus 13'*\n"
                "- *'What is your return policy?'*"
            )

        elif intent.startswith("POLICY_"):
            policy_key = intent.replace("POLICY_", "").lower()
            response_text = self.POLICIES.get(policy_key, self.POLICIES["return"])

        elif intent == "COMPARISON":
            # Extract models separated by "and", "vs", "versus"
            cleaned = query.lower()
            cleaned = re.sub(
                r"^(?:show\s+)?(?:direct\s+)?(?:comparison\s+)?(?:spec\s+)?(?:hardware\s+)?(?:chart\s+)?(?:for\s+|of\s+|comparing\s+|between\s+)?",
                "",
                cleaned,
            )
            cleaned = (
                cleaned.replace("compare", "")
                .replace("comparison", "")
                .replace("chart", "")
                .strip()
            )
            parts = re.split(r"\s+(?:vs|versus|and|with|to)\s+", cleaned)
            if len(parts) >= 2:
                name_a, name_b = parts[0].strip(), parts[1].strip()
                comp = self.search_engine.compare_products(name_a, name_b)
                p_a, p_b = comp["product_a"], comp["product_b"]
                if p_a and p_b:
                    products = [p_a, p_b]
                    response_text = (
                        f"⚖️ **Comparison: {p_a['name'].title()} vs {p_b['name'].title()}**\n\n"
                        f"| Feature | {p_a['name'].title()} | {p_b['name'].title()} |\n"
                        f"|---|---|---|\n"
                        f"| **Price** | ₹{p_a['price']:,} | ₹{p_b['price']:,} |\n"
                        f"| **RAM** | {int(p_a['ram'])} GB | {int(p_b['ram'])} GB |\n"
                        f"| **Storage** | {int(p_a['storage'])} GB | {int(p_b['storage'])} GB |\n"
                        f"| **Battery** | {p_a['battery_cap']} mAh | {p_b['battery_cap']} mAh |\n"
                        f"| **Primary Camera** | {int(p_a['primary_rear_camera'])} MP | {int(p_b['primary_rear_camera'])} MP |\n"
                        f"| **5G Support** | {p_a['has_5g']} | {p_b['has_5g']} |\n"
                        f"| **Display** | {p_a['display_size']}\" {p_a['display_type'].title()} ({int(p_a['refresh_rate'])}Hz) | {p_b['display_size']}\" {p_b['display_type'].title()} ({int(p_b['refresh_rate'])}Hz) |\n"
                        f"| **Processor** | {p_a['processor_brand'].title()} | {p_b['processor_brand'].title()} |\n"
                    )
                else:
                    response_text = f"Could not find exact matches for both '{name_a}' and '{name_b}'. Please check model names."
            else:
                response_text = "Please specify two phones to compare, e.g. *'Compare Vivo V50 and Realme P3 Pro'*."

        elif intent == "SPEC_INQUIRY":
            res = self.search_engine.search(query=query, limit=1)
            if res["products"]:
                p = res["products"][0]
                products = [p]
                response_text = (
                    f"📱 **{p['name'].title()} Specifications**:\n"
                    f"- **Price**: ₹{p['price']:,}\n"
                    f"- **RAM & Storage**: {int(p['ram'])}GB RAM | {int(p['storage'])}GB Storage\n"
                    f"- **Battery**: {p['battery_cap']} mAh (Fast Charging: {p['has_fast_charging']})\n"
                    f"- **Camera**: {int(p['primary_rear_camera'])} MP Main | {int(p['primary_front_camera'])} MP Front\n"
                    f"- **Display**: {p['display_size']}\" {p['display_type'].title()} @ {int(p['refresh_rate'])}Hz\n"
                    f"- **Processor**: {p['processor_brand'].title()} ({int(p['num_core'])}-core)\n"
                    f"- **5G Ready**: {p['has_5g']}"
                )
            else:
                response_text = "No matching smartphone found for spec inquiry."

        else:  # PRODUCT_SEARCH
            slots, residual_tokens = self.search_engine.parse_query_slots(query)
            sort_by = slots.get("sort_by") or "relevance"
            search_res = self.search_engine.search(
                query=" ".join(residual_tokens) if residual_tokens else None,
                brand=slots["brand"],
                min_price=slots["min_price"],
                max_price=slots["max_price"],
                min_ram=slots["min_ram"],
                has_5g=slots["has_5g"],
                min_battery=slots["min_battery"],
                display_type=slots["display_type"],
                min_refresh_rate=slots["min_refresh_rate"],
                processor_brand=slots["processor_brand"],
                sort_by=sort_by,
                limit=4,
            )
            products = search_res["products"]
            if products:
                title_emoji = "📸" if sort_by == "camera_desc" else "🔍"
                category_desc = "camera " if sort_by == "camera_desc" else ""
                lines = [
                    f"{title_emoji} Found **{search_res['total_matches']}** matching {category_desc}smartphones. Here are top recommendations:\n"
                ]
                for i, p in enumerate(products, 1):
                    lines.append(
                        f"**{i}. {p['name'].title()}** — **₹{p['price']:,}**\n"
                        f"   - {int(p['ram'])}GB RAM / {int(p['storage'])}GB | {p['battery_cap']}mAh | "
                        f"{int(p['primary_rear_camera'])}MP Camera | 5G: {p['has_5g']}"
                    )
                response_text = "\n".join(lines)
            else:
                response_text = "Sorry, no smartphones matched your exact filters. Try relaxing price or specification limits."

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return {
            "intent": intent,
            "response": response_text,
            "products": products,
            "tokens_used": 0,
            "execution_time_ms": elapsed_ms,
            "bot_type": "typical_deterministic"
        }

typical_chatbot = TypicalChatbot()
