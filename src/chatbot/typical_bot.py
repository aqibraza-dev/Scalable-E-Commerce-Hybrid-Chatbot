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
        "infinix", "google", "nothing", "nokia", "honor", "micromax"
    ]

    def __init__(self, search_engine: SearchEngine | None = None):
        self.search_engine = search_engine or SearchEngine()

    def _resolve_comparison_target(self, name: str) -> dict[str, Any] | None:
        """Resolves model name, brand flagship, or concept target for comparisons."""
        if not name:
            return None
        # 1. Direct search (no relaxation to avoid returning wrong models for fictional names)
        direct_res = self.search_engine.search(query=name, relax_query=False, limit=1)
        if direct_res["products"]:
            return direct_res["products"][0]

        # 2. Concept / Brand fallback
        na = self.search_engine._normalize_query(name)
        brand = next((b for b in self.BRANDS if b in na), None)

        if any(w in na for w in ["cheap", "lowest", "least price", "sasta", "budget", "affordable"]):
            res = self.search_engine.search(brand=brand, sort_by="price_asc", limit=1)
            return res["products"][0] if res["products"] else None

        if any(w in na for w in ["camera", "photo", "selfie", "mp"]):
            res = self.search_engine.search(brand=brand, sort_by="camera_desc", limit=1)
            return res["products"][0] if res["products"] else None

        if any(w in na for w in ["battery", "backup", "power", "mah"]):
            res = self.search_engine.search(brand=brand, sort_by="battery_desc", limit=1)
            return res["products"][0] if res["products"] else None

        if any(w in na for w in ["ram", "memory", "gaming", "performance", "fastest"]):
            res = self.search_engine.search(brand=brand, sort_by="ram_desc", limit=1)
            return res["products"][0] if res["products"] else None

        # If a known brand is present OR query is explicitly asking for best/flagship/top/premium
        has_flagship_term = any(w in na for w in ["best", "flagship", "premium", "top", "expensive", "costliest", "ultra", "mahanga"])
        if brand or has_flagship_term:
            flag_res = self.search_engine.search(brand=brand, min_price=50000, sort_by="price_desc", limit=1)
            if not flag_res["products"]:
                flag_res = self.search_engine.search(brand=brand, sort_by="price_desc", limit=1)
            return flag_res["products"][0] if flag_res["products"] else None

        return None

    def extract_slots(self, text: str) -> dict[str, Any]:
        """Extracts structured search parameters (brand, budget, RAM, 5G, battery) from text."""
        slots, _ = self.search_engine.parse_query_slots(text)
        return slots

    def classify_intent(self, text: str) -> str:
        """Classifies query into high-level intent."""
        t = text.lower().strip()

        # Typo normalizations for common phonetics and misspellings
        t = re.sub(r"\bweather\b(?=\s+(?:i|we|can|could|if|you|they|a|the|it|is|was|one)\b)", "whether", t)
        t = re.sub(r"\bpriminum\b|\bprimum\b|\bpremiun\b|\bpreimum\b", "premium", t)
        t = re.sub(r"\bedgee\b|\bedg\b", "edge", t)

        # Persona & Bot Identity FAQ
        persona_patterns = [
            r"\bwho\s+are\s+you\b",
            r"\bwho\s+(?:built|build|created|made|developed|founded)\s+you\b",
            r"\bwhat\s+(?:are\s+you|is\s+your\s+name)\b",
            r"\btell\s+me\s+about\s+yourself\b",
            r"\bwhat\s+can\s+you\s+do(?:\s+for\s+me)?\b",
            r"\bwho\s+is\s+your\s+creator\b",
            r"\bwho\s+owns\s+you\b",
            r"\bare\s+you\s+(?:a\s+bot|an\s+ai|human|real)\b",
            r"\bwhat\s+is\s+this\s+(?:website|bot|store|shop)\b",
            r"\bwho\s+made\s+this\b",
        ]
        if any(re.search(p, t) for p in persona_patterns):
            return "PERSONA_FAQ"

        # Small Talk & Polite Chit-Chat
        small_talk_patterns = [
            r"\b(how\s+are\s+you|how\s+r\s+u|how\'s\s+it\s+going|how\s+do\s+you\s+do|how\s+are\s+things)\b",
            r"\b(thank\s+you|thanks|thx|thank\s+u|dhanyawad|shukriya|thanks\s+a\s+lot|thank\s+you\s+so\s+much)\b",
            r"\b(good\s+(?:morning|afternoon|evening|night))\b",
            r"\b(bye|goodbye|see\s+you|take\s+care|have\s+a\s+nice\s+day)\b",
            r"\b(nice\s+to\s+meet\s+you|pleased\s+to\s+meet\s+you)\b",
        ]
        if any(re.search(p, t) for p in small_talk_patterns):
            return "SMALL_TALK"

        # Hinglish / English Dual Extremes ("compare cheapest and priminum phones", "sabse sasta aur mahanga")
        is_cheap_term = bool(re.search(r"\b(cheapest|cheepest|lowest\s+price|most\s+affordable|sasta|sabse\s+sasta|budget\s+phone)\b", t))
        is_premium_term = bool(re.search(r"\b(premium|priminum|primum|premiun|preimum|most\s+expensive|costliest|flagship|highest\s+price|mahanga|sabse\s+mahanga|ultra\s+flagship)\b", t))
        if is_cheap_term and is_premium_term:
            return "EXTREMES_COMPARISON"

        if re.search(
            r"(?:sabse\s+)?sasta.*(?:aur|and).*(?:sabse\s+)?mahanga|(?:cheapest|lowest\s+price|most\s+affordable).*(?:and|aur).*(?:most\s+expensive|costliest|flagship|highest\s+price)|(?:most\s+expensive|costliest|highest\s+price).*(?:and|aur).*(?:cheapest|lowest\s+price|sasta)|(?:sabse\s+)?mahanga.*(?:aur|and).*(?:sabse\s+)?sasta",
            t,
        ):
            return "EXTREMES_COMPARISON"

        # Policy FAQs (Prioritized before out-of-domain to avoid false negatives on customer service inquiries)
        is_return_inquiry = bool(re.search(r"\b(return|refund|exchange|replace|give\s+back|send\s+back|take\s+back|money\s+back|return\s+policy|return\s+days|return\s+window)\b", t))
        is_7_days_return = bool(re.search(r"\b(?:more\s+than|after|past|exceeding|over|used\s+for)\s+(?:7|seven)\s+days\b|\b(?:7|seven)\s+days\s+(?:later|over|past|used)\b", t))

        if is_return_inquiry or (("give back" in t or "return" in t or "send back" in t) and ("phone" in t or "device" in t or "days" in t)):
            if is_7_days_return or ("7 days" in t and ("used" in t or "more" in t or "after" in t)):
                return "POLICY_RETURN_DAYS"
            return "POLICY_RETURN"

        if any(w in t for w in ["warranty", "guarantee"]):
            return "POLICY_WARRANTY"
        if any(w in t for w in ["delivery", "shipping", "courier", "track"]):
            return "POLICY_SHIPPING"
        if any(w in t for w in ["emi", "installment", "finance", "discount"]):
            return "POLICY_EMI"

        # General Trivia / Out-of-Domain questions (Protected by e-commerce context check)
        has_ecommerce_context = any(
            w in t
            for w in [
                "phone", "phones", "mobile", "mobiles", "smartphone", "buy", "price",
                "order", "delivery", "warranty", "return", "refund", "give back",
                "send back", "cart", "shopcart", "camera", "battery", "specs", "specification"
            ]
        )
        if not has_ecommerce_context:
            out_of_domain_patterns = [
                r"\b(joke|jokes|make\s+me\s+laugh|tell\s+me\s+something\s+funny)\b",
                r"\b(weather|forecast|temperature|rain|humidity)\b",
                r"\b(capital\s+of|president\s+of|prime\s+minister|population\s+of|who\s+won)\b",
                r"\b(poem|poetry|song|sing|dance|story|essay)\b",
                r"\b(write\s+(?:python|code|script|essay|story|program)|solve\s+(?:math|equation))\b",
                r"\b(calculate\s+\d|\d+\s*[\+\-\*\/]\s*\d+)\b",
                r"\b(recipe|cooking|movie|celebrity|news\s+today|horoscope)\b",
            ]
            if any(re.search(p, t) for p in out_of_domain_patterns):
                return "OUT_OF_DOMAIN"

        # Greeting intent
        if re.match(r"^(hi|hello|hey|greetings|howdy)\b", t):
            return "GREETING"

        # Product Benefits Inquiry ("benefits of moto edge 50", "advantages of samsung galaxy s24")
        if re.search(
            r"\b(benefit|benefits|advantage|advantages|pros\s+and\s+cons|why\s+buy|why\s+should\s+i\s+buy|highlights\s+of|features\s+and\s+benefits)\b",
            t,
        ):
            return "BENEFITS_INQUIRY"

        # Comparison intent ("compare X and Y", "X vs Y", "chart comparing X and Y")
        if (
            "compare" in t
            or " vs " in t
            or " versus " in t
            or "comparison" in t
            or (("chart" in t or "charts" in t) and (" and " in t or " vs " in t))
        ):
            return "COMPARISON"

        # Subjective & Lifestyle Advisory intent (requires Tier 4 LLM RAG)
        advisory_patterns = [
            r"\b(student|college|university)\b.*\b(phone|smartphone|recommend|suggest|need|looking)\b",
            r"\b(phone|smartphone|recommend|suggest|need|looking)\b.*\b(student|college|university)\b",
            r"\b(construction|outdoor|rugged|durable|tough)\b.*\b(phone|smartphone|device|work)\b",
            r"\b(mother|father|mom|dad|parents|elderly|grandfather|grandmother|kid|child|wife|husband|friend)\b.*\b(phone|gift|recommend|suggest)\b",
            r"\b(gift|present)\b.*\b(?:for\s+)?(?:my\s+)?(?:mother|father|mom|dad|parents|friend|brother|sister|wife|husband|kid|someone)\b",
            r"\b(cleanest\s+(?:software|ui)|clean\s+ui|stock\s+android|simple\s+interface|easy\s+to\s+use)\b",
            r"\b(night\s+photography|vlog|vlogging|content\s+creation)\b.*\b(phone|recommend|suggest)\b",
            r"\b(recommend\s+a\s+phone\s+for|suggest\s+a\s+(?:gift\s+)?phone\s+for|help\s+me\s+choose\s+a\s+phone|which\s+phone\s+should\s+i\s+buy\s+for)\b",
            r"\bwhich\s+phone\s+(?:has\s+the\s+best|has\s+the\s+cleanest|is\s+best\s+for)\b",
        ]
        if any(re.search(p, t) for p in advisory_patterns):
            return "SUBJECTIVE_ADVISORY"

        # Check if query is an inquiry about a specific phone's specs
        is_extremum_query = any(
            w in t
            for w in [
                "least", "lowest", "highest", "hight", "cheapest", "costliest",
                "best", "top", "kam", "sabse", "which phone", "which mobile"
            ]
        )
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
            "price",
            "cost",
            "ram",
            "storage",
        ]
        has_spec_term = any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in spec_terms)
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
                "cost of",
                "ram of",
                "storage of",
            ]
        )
        has_brand = any(re.search(r"\b" + re.escape(b) + r"\b", t) for b in self.BRANDS) or any(
            re.search(r"\b" + re.escape(m) + r"\b", t) for m in ["iphone", "pixel", "galaxy", "redmi", "nord", "edge"]
        )

        if not is_extremum_query and (
            (has_inquiry_starter and (has_brand or has_spec_term))
            or (has_spec_term and has_brand and any(w in t for w in [" of ", " for "]))
            or any(
                t.startswith(prefix)
                for prefix in [
                    "what is the battery",
                    "what is the camera",
                    "what is the price",
                    "what is the ram",
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

        elif intent == "SMALL_TALK":
            q_lower = query.lower()
            if any(w in q_lower for w in ["thank", "thx", "shukriya", "dhanyawad"]):
                response_text = (
                    "You're very welcome! 😊 Feel free to ask if you want to explore more smartphones, "
                    "compare specs, or add recommendations to your shopping cart. Happy shopping on Shopcart! 🛍️"
                )
            elif any(w in q_lower for w in ["bye", "goodbye", "see you", "night"]):
                response_text = (
                    "Goodbye! 👋 Have a wonderful day, and come back whenever you need smartphone recommendations or deals on Shopcart!"
                )
            else:
                response_text = (
                    "I'm doing great, thank you for asking! 😊 I'm ready to help you explore our 1,376+ smartphones, "
                    "compare hardware specs, find top camera or gaming phones, or answer policy questions.\n\n"
                    "What kind of phone are you looking for today?"
                )

        elif intent == "OUT_OF_DOMAIN":
            response_text = (
                "I am specialized as a smartphone shopping assistant for Shopcart. "
                "I cannot answer general trivia outside of smartphones, tech specifications, and e-commerce shopping.\n\n"
                "Would you like me to help you find the best smartphone for your budget or camera needs?"
            )

        elif intent == "EXTREMES_COMPARISON":
            cheap_res = self.search_engine.search(sort_by="price_asc", limit=1)
            flag_res = self.search_engine.search(min_price=50000, sort_by="price_desc", limit=1)
            if not flag_res["products"]:
                flag_res = self.search_engine.search(sort_by="price_desc", limit=1)
            p_cheap = cheap_res["products"][0] if cheap_res["products"] else None
            p_flag = flag_res["products"][0] if flag_res["products"] else None
            products = [p for p in [p_cheap, p_flag] if p]
            if p_cheap and p_flag:
                response_text = (
                    "📊 **Comparison: Most Affordable (Sabse Sasta) vs Ultra-Flagship (Sabse Mahanga)**\n\n"
                    f"| Feature | 🏷️ {p_cheap['name'].title()} (Budget) | 👑 {p_flag['name'].title()} (Flagship) |\n"
                    f"|---|---|---|\n"
                    f"| **Price** | ₹{p_cheap['price']:,} | ₹{p_flag['price']:,} |\n"
                    f"| **RAM / Storage** | {int(p_cheap['ram'])}GB / {int(p_cheap['storage'])}GB | {int(p_flag['ram'])}GB / {int(p_flag['storage'])}GB |\n"
                    f"| **Camera** | {int(p_cheap['primary_rear_camera'])}MP Rear | {int(p_flag['primary_rear_camera'])}MP Rear |\n"
                    f"| **Battery** | {p_cheap['battery_cap']} mAh | {p_flag['battery_cap']} mAh |\n"
                    f"| **5G Support** | {p_cheap['has_5g']} | {p_flag['has_5g']} |\n"
                    f"| **Display** | {p_cheap['display_size']}\" {p_cheap['display_type'].title()} | {p_flag['display_size']}\" {p_flag['display_type'].title()} ({int(p_flag['refresh_rate'])}Hz) |\n"
                    f"| **Processor** | {p_cheap['processor_brand'].title()} | {p_flag['processor_brand'].title()} |\n\n"
                    f"💡 **Recommendation**: Choose the **{p_cheap['name'].title()}** for basic calls, messaging, and maximum affordability. "
                    f"Choose the **{p_flag['name'].title()}** for top-tier photography, gaming, and premium multitasking.\n\n"
                    "Both smartphones are available with instant checkout, 7-day replacement, and express delivery!"
                )
            else:
                response_text = "Catalog currently does not contain matching smartphones."

        elif intent == "POLICY_RETURN_DAYS":
            response_text = (
                "📦 **Return Policy for Phones Used More than 7 Days**:\n\n"
                "- ⏱️ **7-Day Standard Return Window**: Shopcart offers a hassle-free 7-day replacement or 100% money-back return for smartphones in original condition with box and IMEI intact.\n"
                "- ⚠️ **Used for More than 7 Days**: Once the 7-day delivery window has passed, standard retail returns or refunds cannot be accepted through the store.\n"
                "- 🛡️ **1-Year Manufacturer Warranty**: Even though the 7-day store return period has ended, your smartphone is fully covered under the **1-Year Comprehensive Manufacturer Warranty**! If you experience any hardware issues, battery degradation, or defects, authorized brand service centers pan-India will repair or replace parts free of charge.\n\n"
                "Would you like me to help check authorized service center details for your phone brand?"
            )

        elif intent == "BENEFITS_INQUIRY":
            # Extract clean phone name
            cleaned_name = re.sub(
                r"\b(?:benefits?|advantages?|pros\s+and\s+cons|why\s+(?:should\s+i\s+)?buy|highlights?|features?\s+and\s+benefits?|of|for|about|the)\b",
                " ",
                query,
                flags=re.IGNORECASE,
            ).strip()
            res = self.search_engine.search(query=cleaned_name, limit=1)
            if res["products"]:
                p = res["products"][0]
                products = [p]
                response_text = (
                    f"✨ **Key Benefits of the {p['name'].title()}** (₹{p['price']:,}):\n\n"
                    f"- 🚀 **Performance & Multitasking**: Powered by {p['processor_brand'].title()} ({int(p['num_core'])}-core) with {int(p['ram'])}GB RAM and {int(p['storage'])}GB storage for responsive everyday speed and multitasking.\n"
                    f"- 📸 **Camera Clarity**: Features a {int(p['primary_rear_camera'])}MP main camera and {int(p['primary_front_camera'])}MP front camera for crisp photos and 4K recording.\n"
                    f"- 🔋 **All-Day Battery**: Long-lasting {p['battery_cap']} mAh battery equipped with {p['has_fast_charging']} fast charging support.\n"
                    f"- 📱 **Display Experience**: {p['display_size']}\" {p['display_type'].title()} screen with {int(p['refresh_rate'])}Hz refresh rate for fluid scrolling.\n"
                    f"- ⚡ **5G Ready**: {'Yes, supports ultra-fast 5G networks across India' if p['has_5g'] == 'Yes' else 'Reliable 4G LTE network support'}.\n\n"
                    f"Click below to add the **{p['name'].title()}** to your bag with instant checkout!"
                )
            else:
                response_text = f"Could not find model details for '{cleaned_name}'. Please verify the model name or ask for recommendations."

        elif intent == "SUBJECTIVE_ADVISORY":
            slots = self.extract_slots(query)
            min_p = slots.get("min_price")
            max_p = slots.get("max_price")
            res = self.search_engine.search(
                brand=slots.get("brand"),
                min_price=min_p,
                max_price=max_p,
                min_ram=slots.get("min_ram") or (4.0 if not slots.get("brand") and not max_p else None),
                min_camera=slots.get("min_camera"),
                min_battery=slots.get("min_battery"),
                has_5g=slots.get("has_5g"),
                sort_by=slots.get("sort_by") or "relevance",
                limit=4,
            )
            products = res["products"]
            if products:
                response_text = (
                    "💡 Based on your requirements, here are our top smartphone recommendations:\n\n"
                )
                for idx, p in enumerate(products[:3], 1):
                    response_text += (
                        f"**{idx}. {p['name'].title()}** — **₹{p['price']:,}**\n"
                        f"   - {int(p['ram'])}GB RAM | {p['battery_cap']}mAh | "
                        f"{int(p['primary_rear_camera'])}MP Camera | 5G: {p['has_5g']}\n"
                    )
            else:
                response_text = "I recommend checking our featured smartphones or refining your budget range."

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
                p_a = self._resolve_comparison_target(name_a)
                p_b = self._resolve_comparison_target(name_b)

                if p_a and p_b:
                    products = [p_a, p_b]
                    ram_a = f"{p_a['ram']} GB" if p_a["ram"] < 1 else f"{int(p_a['ram'])} GB"
                    ram_b = f"{p_b['ram']} GB" if p_b["ram"] < 1 else f"{int(p_b['ram'])} GB"
                    cam_a = f"{p_a['primary_rear_camera']} MP" if p_a["primary_rear_camera"] < 1 else f"{int(p_a['primary_rear_camera'])} MP"
                    cam_b = f"{p_b['primary_rear_camera']} MP" if p_b["primary_rear_camera"] < 1 else f"{int(p_b['primary_rear_camera'])} MP"
                    response_text = (
                        f"⚖️ **Comparison: {p_a['name'].title()} vs {p_b['name'].title()}**\n\n"
                        f"| Feature | {p_a['name'].title()} | {p_b['name'].title()} |\n"
                        f"|---|---|---|\n"
                        f"| **Price** | ₹{p_a['price']:,} | ₹{p_b['price']:,} |\n"
                        f"| **RAM** | {ram_a} | {ram_b} |\n"
                        f"| **Storage** | {int(p_a['storage'])} GB | {int(p_b['storage'])} GB |\n"
                        f"| **Battery** | {p_a['battery_cap']} mAh | {p_b['battery_cap']} mAh |\n"
                        f"| **Primary Camera** | {cam_a} | {cam_b} |\n"
                        f"| **5G Support** | {p_a['has_5g']} | {p_b['has_5g']} |\n"
                        f"| **Display** | {p_a['display_size']}\" {p_a['display_type'].title()} ({int(p_a['refresh_rate'])}Hz) | {p_b['display_size']}\" {p_b['display_type'].title()} ({int(p_b['refresh_rate'])}Hz) |\n"
                        f"| **Processor** | {p_a['processor_brand'].title()} | {p_b['processor_brand'].title()} |\n"
                    )
                else:
                    products = []
                    response_text = f"Could not find exact matches for both '{name_a}' and '{name_b}'. Please check model names."
            else:
                response_text = "Please specify two phones to compare, e.g. *'Compare Vivo V50 and Realme P3 Pro'*."

        elif intent == "SPEC_INQUIRY":
            cleaned_target = re.sub(
                r"\b(?:what\s+is\s+(?:the\s+)?|what\s+are\s+(?:the\s+)?|how\s+is\s+(?:the\s+)?|specs?\s+of|specifications?\s+of|details\s+of|features\s+of|tell\s+me\s+about|price\s+of|cost\s+of|battery\s+of|camera\s+of|ram\s+of|display\s+of|screen\s+of|processor\s+of)\b",
                " ",
                query,
                flags=re.IGNORECASE,
            )
            cleaned_target = re.sub(
                r"\b(?:phone|phones|mobile|mobiles|smartphone|smartphones)\b",
                " ",
                cleaned_target,
                flags=re.IGNORECASE,
            ).strip()
            res = self.search_engine.search(query=cleaned_target or query, relax_query=False, limit=1)
            if res["products"]:
                p = res["products"][0]
                products = [p]
                ram_str = f"{p['ram']}GB RAM" if p["ram"] < 1 else f"{int(p['ram'])}GB RAM"
                cam_str = f"{p['primary_rear_camera']} MP Main" if p["primary_rear_camera"] < 1 else f"{int(p['primary_rear_camera'])} MP Main"
                front_str = f"{p['primary_front_camera']} MP Front" if p["primary_front_camera"] < 1 else f"{int(p['primary_front_camera'])} MP Front"
                response_text = (
                    f"📱 **{p['name'].title()} Specifications**:\n"
                    f"- **Price**: ₹{p['price']:,}\n"
                    f"- **RAM & Storage**: {ram_str} | {int(p['storage'])}GB Storage\n"
                    f"- **Battery**: {p['battery_cap']} mAh (Fast Charging: {p['has_fast_charging']})\n"
                    f"- **Camera**: {cam_str} | {front_str}\n"
                    f"- **Display**: {p['display_size']}\" {p['display_type'].title()} @ {int(p['refresh_rate'])}Hz\n"
                    f"- **Processor**: {p['processor_brand'].title()} ({int(p['num_core'])}-core)\n"
                    f"- **5G Ready**: {p['has_5g']}"
                )
            else:
                products = []
                response_text = f"Could not find specifications for '{cleaned_target or query}'. Please check the model name."

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
                category_emoji_map = {
                    "camera_desc": ("📸", "top camera"),
                    "camera_asc": ("📸", "entry camera"),
                    "battery_desc": ("🔋", "long battery life"),
                    "battery_asc": ("🔋", "lowest battery capacity"),
                    "ram_desc": ("⚡", "high performance RAM"),
                    "ram_asc": ("⚡", "lowest RAM"),
                    "storage_desc": ("💾", "highest storage"),
                    "storage_asc": ("💾", "lowest storage"),
                    "price_asc": ("🏷️", "most affordable"),
                    "price_desc": ("👑", "premium flagship"),
                }
                top_p = products[0]
                brand_str = f" {slots['brand'].title()}" if slots.get("brand") else ""
                if sort_by == "battery_asc":
                    summary = f"🔋 The{brand_str} smartphone with the lowest battery capacity is the **{top_p['name'].title()}** ({top_p['battery_cap']} mAh, ₹{top_p['price']:,}). Here are top lowest battery picks:\n"
                elif sort_by == "battery_desc":
                    summary = f"🔋 The{brand_str} smartphone with the highest battery capacity is the **{top_p['name'].title()}** ({top_p['battery_cap']} mAh, ₹{top_p['price']:,}). Here are top battery picks:\n"
                elif sort_by == "camera_asc":
                    cam_fmt = f"{top_p['primary_rear_camera']}MP" if top_p['primary_rear_camera'] < 1 else f"{int(top_p['primary_rear_camera'])}MP"
                    summary = f"📸 The{brand_str} smartphone with the lowest camera resolution is the **{top_p['name'].title()}** ({cam_fmt}, ₹{top_p['price']:,}). Here are entry camera picks:\n"
                elif sort_by == "camera_desc":
                    cam_fmt = f"{top_p['primary_rear_camera']}MP" if top_p['primary_rear_camera'] < 1 else f"{int(top_p['primary_rear_camera'])}MP"
                    summary = f"📸 Top camera recommendations (led by **{top_p['name'].title()}** with {cam_fmt} rear camera):\n"
                elif sort_by == "ram_asc":
                    ram_fmt = f"{top_p['ram']}GB" if top_p['ram'] < 1 else f"{int(top_p['ram'])}GB"
                    summary = f"⚡ The{brand_str} smartphone with the lowest RAM is the **{top_p['name'].title()}** ({ram_fmt} RAM, ₹{top_p['price']:,}). Here are top entry-level picks:\n"
                elif sort_by == "ram_desc":
                    ram_fmt = f"{top_p['ram']}GB" if top_p['ram'] < 1 else f"{int(top_p['ram'])}GB"
                    summary = f"⚡ The{brand_str} smartphone with the highest RAM is the **{top_p['name'].title()}** ({ram_fmt} RAM, ₹{top_p['price']:,}). Here are top high performance picks:\n"
                elif sort_by == "price_asc":
                    summary = f"🏷️ The most affordable{brand_str} smartphone is the **{top_p['name'].title()}** at **₹{top_p['price']:,}**. Here are top budget picks:\n"
                elif sort_by == "price_desc":
                    summary = f"👑 The premium flagship{brand_str} smartphone is the **{top_p['name'].title()}** at **₹{top_p['price']:,}**. Here are top flagship picks:\n"
                else:
                    title_emoji, category_desc = category_emoji_map.get(sort_by, ("🔍", ""))
                    desc_part = f" {category_desc}" if category_desc else ""
                    summary = f"{title_emoji} Found **{search_res['total_matches']}** matching{desc_part} smartphones. Here are top recommendations:\n"
                lines = [summary]
                for i, p in enumerate(products, 1):
                    ram_str = f"{p['ram']}GB" if p["ram"] < 1 else f"{int(p['ram'])}GB"
                    cam_str = f"{p['primary_rear_camera']}MP" if p["primary_rear_camera"] < 1 else f"{int(p['primary_rear_camera'])}MP"
                    lines.append(
                        f"**{i}. {p['name'].title()}** — **₹{p['price']:,}**\n"
                        f"   - {ram_str} RAM / {int(p['storage'])}GB | {p['battery_cap']}mAh | "
                        f"{cam_str} Camera | 5G: {p['has_5g']}"
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
