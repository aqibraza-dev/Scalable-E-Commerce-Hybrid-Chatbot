import re
import sqlite3
import time
from typing import Any

from src.config import settings
from src.data.loader import get_db_connection
from src.search.cache import MultiTierCache, global_cache

KNOWN_BRANDS = [
    "samsung",
    "apple",
    "xiaomi",
    "redmi",
    "vivo",
    "oppo",
    "oneplus",
    "realme",
    "motorola",
    "iqoo",
    "poco",
    "tecno",
    "lava",
    "infinix",
    "google",
    "nothing",
    "honor",
    "nokia",
    "micromax",
]

CONVERSATIONAL_STOPWORDS = {
    "find",
    "show",
    "me",
    "suggest",
    "recommend",
    "which",
    "what",
    "are",
    "the",
    "is",
    "for",
    "in",
    "with",
    "and",
    "or",
    "a",
    "an",
    "of",
    "to",
    "buy",
    "get",
    "give",
    "tell",
    "search",
    "list",
    "looking",
    "need",
    "want",
    "please",
    "phone",
    "phones",
    "mobile",
    "mobiles",
    "smartphone",
    "smartphones",
    "device",
    "devices",
    "best",
    "top",
    "good",
    "budget",
    "cheap",
    "cheapest",
    "latest",
    "new",
    "flagship",
    "rupees",
    "rs",
    "inr",
    "bucks",
    "under",
    "below",
    "above",
    "over",
    "between",
    "within",
    "upto",
    "up",
    "less",
    "more",
    "than",
    "around",
    "approx",
    "from",
    "at",
    "fast",
    "charging",
    "that",
    "not",
    "non",
    "only",
    "camera",
    "cameras",
    "spec",
    "specs",
    "specification",
    "specifications",
    "feature",
    "features",
    "details",
    "info",
    "information",
    "price",
    "cost",
    "how",
    "much",
    "many",
    "about",
    "compare",
    "comparison",
    "vs",
    "versus",
    "chart",
    "charts",
    "battery",
    "display",
    "screen",
    "processor",
    "ram",
    "storage",
    "mid",
    "range",
    "midrange",
    "medium",
    "sabse",
    "sasta",
    "saste",
    "mahanga",
    "mahnge",
    "dikhao",
    "batao",
    "chahiye",
    "kaun",
    "sa",
    "se",
    "ko",
    "bhi",
    "ek",
    "koi",
    "wala",
    "wali",
    "wale",
    "kya",
    "hai",
    "aur",
    "hazaar",
    "hazar",
    "thousand",
    "benefit",
    "benefits",
    "advantage",
    "advantages",
    "pro",
    "pros",
    "con",
    "cons",
    "worth",
    "review",
    "why",
    "explain",
    "highlight",
    "highlights",
    "rupee",
    "mein",
    "tak",
    "andar",
    "niche",
    "kam",
    "jyada",
    "zyada",
    "accha",
    "achha",
    "acha",
    "ache",
    "mast",
    "badhiya",
    "shandar",
    "bhai",
    "college",
    "student",
    "night",
    "photography",
    "vlogging",
    "vlog",
    "gaming",
    "game",
    "gamer",
    "games",
    "durable",
    "smooth",
    "better",
    "great",
    "handset",
    "cellphone",
    "am",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "who",
    "whom",
    "whose",
    "love",
    "loves",
    "like",
    "likes",
    "wants",
    "needs",
    "prefer",
    "prefers",
    "searching",
    "least",
    "lowest",
    "highest",
    "hight",
    "maximum",
    "minimum",
    "max",
    "min",
    "smallest",
    "largest",
    "biggest",
    "most",
    "cheaper",
    "where",
    "when",
    "whose",
    "whom",
    "life",
    "backup",
    "capacity",
    "level",
    "levels",
    "rating",
    "rated",
    "mega",
    "megapixel",
    "megapixels",
    "mp",
    "mah",
    "gb",
    "mb",
    "tb",
    "hz",
    "memory",
    "make",
    "makes",
    "company",
    "companies",
    "having",
    "carrying",
    "equipped",
}


class SearchEngine:
    def __init__(self, db_path: str | None = None, cache: MultiTierCache | None = None):
        self.db_path = db_path or settings.sqlite_db_path
        self.cache = cache or global_cache
        self.typo_corrections = {
            "samusng": "samsung",
            "samsng": "samsung",
            "smansung": "samsung",
            "samsong": "samsung",
            "sansung": "samsung",
            "smasung": "samsung",
            "samasung": "samsung",
            "ipone": "apple",
            "iphone": "apple",
            "iphones": "apple",
            "iphhone": "apple",
            "iphne": "apple",
            "ihpone": "apple",
            "redmi": "xiaomi",
            "readmi": "xiaomi",
            "one plus": "oneplus",
            "onplus": "oneplus",
            "one pluse": "oneplus",
            "motrola": "motorola",
            "moto": "motorola",
            "morotola": "motorola",
            "real me": "realme",
            "relame": "realme",
            "xioami": "xiaomi",
            "xiomi": "xiaomi",
            "noting": "nothing",
            "hight": "highest",
            "highet": "highest",
            "heighest": "highest",
            "maxmimum": "maximum",
            "minimun": "minimum",
            "priminum": "premium",
            "primum": "premium",
            "premiun": "premium",
            "preimum": "premium",
            "edgee": "edge",
            "edg": "edge",
            "memory": "ram",
        }

    def _normalize_query(self, query: str | None) -> str:
        if not query:
            return ""
        q = query.strip().lower()
        # Remove currency symbols and digit-grouping commas (e.g. 25,000 -> 25000)
        q = re.sub(r"₹|rs\.?|inr", " ", q)
        q = re.sub(r"(?<=\d),(?=\d)", "", q)
        for typo, fix in self.typo_corrections.items():
            q = re.sub(r"\b" + re.escape(typo) + r"\b", fix, q)
        return q

    def parse_query_slots(self, query: str) -> tuple[dict[str, Any], list[str]]:
        """
        Extracts structured e-commerce filters (brand, budget, RAM, 5G, display, processor, sorting)
        and isolates residual model keywords, handling negations gracefully.
        """
        q = self._normalize_query(query)
        slots: dict[str, Any] = {
            "brand": None,
            "max_price": None,
            "min_price": None,
            "has_5g": None,
            "min_ram": None,
            "min_storage": None,
            "min_battery": None,
            "min_camera": None,
            "display_type": None,
            "min_refresh_rate": None,
            "processor_brand": None,
            "sort_by": None,
        }

        # Normalize thousand words & spaces before k (e.g. "10 hazar" -> "10k", "10 thousand" -> "10k", "10 k" -> "10k")
        q = re.sub(r"(?<=\d)\s*(?:thousand|hazaar|hazar|k)\b", "k", q)
        q = re.sub(r"\b(?:thousand|hazaar|hazar)\b", "k", q)

        # 1. 5G / Network (with negation handling)
        if re.search(r"\b(not\s+5g|non\s+5g|without\s+5g|no\s+5g|4g\s+only|4g)\b", q):
            slots["has_5g"] = "No"
            q = re.sub(
                r"\b(not\s+5g|non\s+5g|without\s+5g|no\s+5g|4g\s+only|4g)\b", " ", q
            )
        elif re.search(r"\b5g\b", q):
            slots["has_5g"] = "Yes"
            q = re.sub(r"\b5g\b", " ", q)

        # 2. Price range (between, under, not above, budget of, within, upto, me, tak, ke andar)
        m_bet = re.search(
            r"between\s+(?:rs\.?|inr|₹)?\s*(\d+)(k)?\s+and\s+(?:rs\.?|inr|₹)?\s*(\d+)(k)?",
            q,
        )
        if m_bet:
            p1 = int(m_bet.group(1)) * (
                1000 if m_bet.group(2) or int(m_bet.group(1)) < 500 else 1
            )
            p2 = int(m_bet.group(3)) * (
                1000 if m_bet.group(4) or int(m_bet.group(3)) < 500 else 1
            )
            slots["min_price"] = min(p1, p2)
            slots["max_price"] = max(p1, p2)
            q = q[: m_bet.start()] + " " + q[m_bet.end() :]
        else:
            # Check maximum price patterns (English and Hindi/Hinglish)
            m_max = re.search(
                r"(?:under|below|not\s+above|not\s+over|not\s+more\s+than|less\s+than|within|upto|up\s+to|<=|<|budget\s+of|ke\s+andar|andar|tak|niche|kam)\s*(?:rs\.?|inr|₹)?\s*(\d+)(k)?(?:\s*(?:rupees|rs|inr|budget|tak|me|mein))?",
                q,
            )
            if m_max:
                v = int(m_max.group(1))
                if m_max.group(2) or v < 500:
                    v *= 1000
                slots["max_price"] = v
                q = q[: m_max.start()] + " " + q[m_max.end() :]

            if slots["max_price"] is None:
                # Postfix pattern: "10000 me", "10k me", "10k tak", "10k ke andar", "10000 rupees budget"
                m_post = re.search(
                    r"\b(\d+)(k)?\s*(?:me|mein|tak|ke\s+andar|ke\s+niche|se\s+kam|se\s+sasta|budget|rupees|rs|inr)\b",
                    q,
                )
                if m_post:
                    v = int(m_post.group(1))
                    if m_post.group(2) or v < 500:
                        v *= 1000
                    slots["max_price"] = v
                    q = q[: m_post.start()] + " " + q[m_post.end() :]

            if slots["max_price"] is None:
                # Standalone k-notation: e.g. "10k", "20k", "30k" not immediately part of ram or battery
                m_k = re.search(r"\b(\d{1,3})k\b(?!\s*ram|\s*mah|\s*hz)", q)
                if m_k:
                    slots["max_price"] = int(m_k.group(1)) * 1000
                    q = q[: m_k.start()] + " " + q[m_k.end() :]

            # Check minimum price patterns
            m_min = re.search(
                r"(?:above|over|not\s+under|not\s+below|not\s+less\s+than|more\s+than|min|minimum|>=|>|se\s+jyada|se\s+zyada)\s*(?:rs\.?|inr|₹)?\s*(\d+)(k)?",
                q,
            )
            if m_min:
                v = int(m_min.group(1))
                if m_min.group(2) or v < 500:
                    v *= 1000
                slots["min_price"] = v
                q = q[: m_min.start()] + " " + q[m_min.end() :]

        # Fuzzy Budget Term Detection (e.g. "mid budget", "budget", "flagship")
        if slots["max_price"] is None and slots["min_price"] is None:
            if re.search(r"\b(mid\s*budget|mid\s*range|midrange|medium\s*budget)\b", q):
                slots["min_price"] = 15000
                slots["max_price"] = 35000
                q = re.sub(r"\b(mid\s*budget|mid\s*range|midrange|medium\s*budget)\b", " ", q)
            elif re.search(r"\b(budget|low\s*budget|cheap|affordable|sasta|kam\s*budget)\b", q):
                slots["max_price"] = 15000
                q = re.sub(r"\b(budget|low\s*budget|cheap|affordable|sasta|kam\s*budget)\b", " ", q)
            elif re.search(r"\b(flagship|premium|ultra|high\s*end|top\s*end|mahanga)\b", q):
                slots["min_price"] = 45000
                q = re.sub(r"\b(flagship|premium|ultra|high\s*end|top\s*end|mahanga)\b", " ", q)

        # Feature Preference & Smart Sorting Detection (Extremums & Attributes)
        # 1. RAM extremums
        if re.search(r"\b(?:least|lowest|min|minimum|smallest|kam|sabse\s+kam)\s+(?:ram|memory)(?:\s*(?:ram|memory|gb))?\b|\b(?:ram|memory)\s+(?:is\s+)?(?:least|lowest|min|minimum|smallest|kam)\b", q):
            slots["sort_by"] = "ram_asc"
            slots["min_ram"] = None
            q = re.sub(r"\b(?:least|lowest|min|minimum|smallest|kam|sabse\s+kam)\s+(?:ram|memory)(?:\s*(?:ram|memory|gb))?\b|\b(?:ram|memory)\s+(?:is\s+)?(?:least|lowest|min|minimum|smallest|kam)\b", " ", q)
        elif re.search(r"\b(?:highest|hight|high|max|maximum|most|top|best|sabse\s+jyada|sabse\s+zyada)\s+(?:ram|memory)(?:\s*(?:ram|memory|gb))?\b|\b(?:ram|memory)\s+(?:is\s+)?(?:highest|hight|high|max|maximum|most|top|best)\b", q):
            slots["sort_by"] = "ram_desc"
            q = re.sub(r"\b(?:highest|hight|high|max|maximum|most|top|best|sabse\s+jyada|sabse\s+zyada)\s+(?:ram|memory)(?:\s*(?:ram|memory|gb))?\b|\b(?:ram|memory)\s+(?:is\s+)?(?:highest|hight|high|max|maximum|most|top|best)\b", " ", q)
        # 2. Battery extremums
        elif re.search(r"\b(?:least|lowest|min|minimum|smallest|kam|sabse\s+kam)\s*(?:battery|backup|mah|power)(?:\s*(?:battery|backup|mah|power|life))?\b|\b(?:battery|backup|mah|power)\s+(?:is\s+)?(?:least|lowest|min|minimum|smallest|kam)\b", q):
            slots["sort_by"] = "battery_asc"
            q = re.sub(r"\b(?:least|lowest|min|minimum|smallest|kam|sabse\s+kam)\s*(?:battery|backup|mah|power)(?:\s*(?:battery|backup|mah|power|life))?\b|\b(?:battery|backup|mah|power)\s+(?:is\s+)?(?:least|lowest|min|minimum|smallest|kam)\b", " ", q)
        elif re.search(r"\b(?:highest|max|maximum|most|best|top|longest|sabse\s+jyada|sabse\s+zyada)\s*(?:battery|backup|mah|power)(?:\s*(?:battery|backup|mah|power|life))?\b|\b(?:battery|backup|mah|power)\s+(?:is\s+)?(?:highest|max|maximum|most|best|top|longest)\b", q):
            slots["sort_by"] = "battery_desc"
            q = re.sub(r"\b(?:highest|max|maximum|most|best|top|longest|sabse\s+jyada|sabse\s+zyada)\s*(?:battery|backup|mah|power)(?:\s*(?:battery|backup|mah|power|life))?\b|\b(?:battery|backup|mah|power)\s+(?:is\s+)?(?:highest|max|maximum|most|best|top|longest)\b", " ", q)
        # 3. Camera extremums
        elif re.search(r"\b(?:least|lowest|min|minimum|smallest|kam|sabse\s+kam)\s*(?:mp\s+|mega\s*pixels?\s+|megapixels?\s+)?(?:camera|cameras|photo|photos|photography|selfie|megapixels?|mega\s*pixels?|mp)(?:\s*(?:camera|cameras|megapixels?|mega\s*pixels?|mp))?\b|\b(?:camera|cameras|megapixels?|mega\s*pixels?|mp)\s+(?:is\s+)?(?:least|lowest|min|minimum|smallest|kam)\b|\b(?:least|lowest|min|minimum|smallest|kam)\s+(?:mp|megapixels?|mega\s*pixels?)\b", q):
            slots["sort_by"] = "camera_asc"
            slots["min_camera"] = None
            q = re.sub(r"\b(?:least|lowest|min|minimum|smallest|kam|sabse\s+kam)\s*(?:mp\s+|mega\s*pixels?\s+|megapixels?\s+)?(?:camera|cameras|photo|photos|photography|selfie|megapixels?|mega\s*pixels?|mp)(?:\s*(?:camera|cameras|megapixels?|mega\s*pixels?|mp))?\b|\b(?:camera|cameras|megapixels?|mega\s*pixels?|mp)\s+(?:is\s+)?(?:least|lowest|min|minimum|smallest|kam)\b|\b(?:least|lowest|min|minimum|smallest|kam)\s+(?:mp|megapixels?|mega\s*pixels?)\b", " ", q)
        elif re.search(r"\b(?:highest|max|maximum|most|best|top)\s*(?:mp\s+|mega\s*pixels?\s+|megapixels?\s+)?(?:camera|cameras|photo|photos|photography|selfie|megapixels?|mega\s*pixels?|mp)(?:\s*(?:camera|cameras|megapixels?|mega\s*pixels?|mp))?\b|\b(?:camera|cameras|megapixels?|mega\s*pixels?|mp)\s+(?:is\s+)?(?:highest|max|maximum|most|best|top)\b|\b(?:highest|max|maximum|most|best|top)\s+(?:mp|megapixels?|mega\s*pixels?)\b", q):
            slots["sort_by"] = "camera_desc"
            if slots.get("min_camera") is None:
                if slots["max_price"] is not None and slots["max_price"] <= 10000:
                    slots["min_camera"] = 13.0
                elif slots["max_price"] is not None and slots["max_price"] <= 25000:
                    slots["min_camera"] = 48.0
                else:
                    slots["min_camera"] = 50.0
            q = re.sub(r"\b(?:highest|max|maximum|most|best|top)\s*(?:mp\s+|mega\s*pixels?\s+|megapixels?\s+)?(?:camera|cameras|photo|photos|photography|selfie|megapixels?|mega\s*pixels?|mp)(?:\s*(?:camera|cameras|megapixels?|mega\s*pixels?|mp))?\b|\b(?:camera|cameras|megapixels?|mega\s*pixels?|mp)\s+(?:is\s+)?(?:highest|max|maximum|most|best|top)\b|\b(?:highest|max|maximum|most|best|top)\s+(?:mp|megapixels?|mega\s*pixels?)\b", " ", q)
        # 4. Storage extremums
        elif re.search(r"\b(?:least|lowest|min|minimum|smallest|kam)\s+storage\b", q):
            slots["sort_by"] = "storage_asc"
            q = re.sub(r"\b(?:least|lowest|min|minimum|smallest|kam)\s+storage\b", " ", q)
        elif re.search(r"\b(?:highest|max|maximum|most|top|best|sabse\s+jyada)\s+storage\b", q):
            slots["sort_by"] = "storage_desc"
            q = re.sub(r"\b(?:highest|max|maximum|most|top|best|sabse\s+jyada)\s+storage\b", " ", q)
        # 5. Price extremums
        elif re.search(r"\b(cheapest|cheepest|lowest\s+price|least\s+price|minimum\s+price|most\s+affordable|sasta|kam\s*daam|saste)\b", q):
            slots["sort_by"] = "price_asc"
        elif re.search(r"\b(most\s+expensive|costliest|highest\s+price|maximum\s+price|mahanga|expensive|premium|flagship|ultra\s+flagship)\b", q):
            slots["sort_by"] = "price_desc"
        # 6. General Feature preferences (fallback to desc, unless asking about a specific model's spec)
        is_spec_inquiry = bool(re.search(r"\b(?:what\s+is\s+(?:the\s+)?|what\s+are\s+(?:the\s+)?|how\s+is\s+(?:the\s+)?|details\s+of|specs?\s+of|specifications?\s+of|(?:battery|camera|ram|storage|price|cost|display|screen|processor)\s+of)\b", q))
        if not is_spec_inquiry:
            if re.search(r"\b(camera|cameras|photo|photos|photography|selfie|megapixels?|mp|video|vlogging|night\s*mode|portrait)\b", q):
                slots["sort_by"] = "camera_desc"
                if slots.get("min_camera") is None:
                    if slots["max_price"] is not None and slots["max_price"] <= 10000:
                        slots["min_camera"] = 13.0
                    elif slots["max_price"] is not None and slots["max_price"] <= 25000:
                        slots["min_camera"] = 48.0
                    else:
                        slots["min_camera"] = 50.0
            elif re.search(r"\b(battery|backup|mah|power|long\s*lasting|charge|charging)\b", q):
                slots["sort_by"] = "battery_desc"
            elif re.search(r"\b(gaming|game|gamer|games|processor|fastest|speed|performance|heavy\s*use)\b", q):
                slots["sort_by"] = "ram_desc"

        # 3. Brand extraction
        for b in KNOWN_BRANDS:
            if re.search(r"\b" + re.escape(b) + r"\b", q):
                slots["brand"] = "xiaomi" if b == "redmi" else b
                q = re.sub(r"\b" + re.escape(b) + r"\b", " ", q)
                break

        # 4. RAM extraction
        m_ram = re.search(r"\b(\d+)\s*gb(?:\s*ram)?\b", q)
        if m_ram:
            slots["min_ram"] = float(m_ram.group(1))
            q = q[: m_ram.start()] + " " + q[m_ram.end() :]

        # 5. Battery extraction
        m_bat = re.search(r"\b(\d{4,5})\s*mah(?:\s*battery)?\b", q)
        if m_bat:
            slots["min_battery"] = int(m_bat.group(1))
            q = q[: m_bat.start()] + " " + q[m_bat.end() :]

        # 6. Display & Refresh rate
        m_disp = re.search(r"\b(amoled|oled|lcd)\b", q)
        if m_disp:
            slots["display_type"] = m_disp.group(1)
            q = re.sub(r"\b(amoled|oled|lcd)\b", " ", q)

        m_hz = re.search(r"\b(\d{2,3})\s*hz\b", q)
        if m_hz:
            slots["min_refresh_rate"] = float(m_hz.group(1))
            q = q[: m_hz.start()] + " " + q[m_hz.end() :]

        # 7. Processor
        m_proc = re.search(
            r"\b(snapdragon|mediatek|dimensity|exynos|bionic|tensor)\b", q
        )
        if m_proc:
            slots["processor_brand"] = m_proc.group(1)
            q = re.sub(
                r"\b(snapdragon|mediatek|dimensity|exynos|bionic|tensor)\b", " ", q
            )

        # 8. Residual keywords
        words = re.findall(r"\b[a-zA-Z0-9]+\b", q)
        residual_keywords = [
            w for w in words if w not in CONVERSATIONAL_STOPWORDS and (len(w) > 1 or w.isdigit())
        ]

        return slots, residual_keywords

    def search(
        self,
        query: str | None = None,
        brand: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        min_ram: float | None = None,
        min_storage: float | None = None,
        min_battery: int | None = None,
        min_camera: float | None = None,
        has_5g: str | None = None,
        display_type: str | None = None,
        min_refresh_rate: float | None = None,
        processor_brand: str | None = None,
        sort_by: str = "relevance",
        limit: int = 10,
        offset: int = 0,
        relax_query: bool = True,
    ) -> dict[str, Any]:
        """
        Executes an optimized product search with B-Tree indexes, FTS5 BM25 ranking,
        faceted navigation, and two-tier caching.
        """
        start_time = time.perf_counter()
        residual_tokens: list[str] = []

        # Smart extraction from query if query string provided
        if query:
            extracted_slots, residual_tokens = self.parse_query_slots(query)
            if brand is None:
                brand = extracted_slots["brand"]
            if min_price is None:
                min_price = extracted_slots["min_price"]
            if max_price is None:
                max_price = extracted_slots["max_price"]
            if has_5g is None:
                has_5g = extracted_slots["has_5g"]
            if min_ram is None:
                min_ram = extracted_slots["min_ram"]
            if min_battery is None:
                min_battery = extracted_slots["min_battery"]
            if min_camera is None:
                min_camera = extracted_slots.get("min_camera")
            if min_storage is None:
                min_storage = extracted_slots.get("min_storage")
            if display_type is None:
                display_type = extracted_slots["display_type"]
            if min_refresh_rate is None:
                min_refresh_rate = extracted_slots["min_refresh_rate"]
            if processor_brand is None:
                processor_brand = extracted_slots["processor_brand"]
            if sort_by == "relevance" and extracted_slots.get("sort_by"):
                sort_by = extracted_slots["sort_by"]

        # Build cache key
        cache_params = {
            "tokens": residual_tokens,
            "brand": brand.lower() if brand else None,
            "min_price": min_price,
            "max_price": max_price,
            "min_ram": min_ram,
            "min_storage": min_storage,
            "min_battery": min_battery,
            "min_camera": min_camera,
            "has_5g": has_5g.capitalize() if has_5g else None,
            "display_type": display_type.lower() if display_type else None,
            "min_refresh_rate": min_refresh_rate,
            "processor_brand": processor_brand.lower() if processor_brand else None,
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset,
        }
        cache_key = self.cache.generate_key("search", cache_params)

        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
            cached_result["execution_time_ms"] = elapsed_ms
            cached_result["from_cache"] = True
            return cached_result

        conn = get_db_connection(self.db_path, read_only=True)
        cursor = conn.cursor()

        # Build dynamic SQL query
        where_clauses = []
        params = []

        # Residual model keywords match using FTS5
        if residual_tokens:
            fts_query = " ".join([f"{t}*" for t in residual_tokens])
            where_clauses.append(
                "s.id IN (SELECT id FROM smartphones_fts WHERE smartphones_fts MATCH ?)"
            )
            params.append(fts_query)

        if brand:
            where_clauses.append("s.brand = ?")
            params.append(brand.strip().lower())

        if min_price is not None:
            where_clauses.append("s.price >= ?")
            params.append(int(min_price))

        if max_price is not None:
            where_clauses.append("s.price <= ?")
            params.append(int(max_price))

        if min_ram is not None:
            where_clauses.append("s.ram >= ?")
            params.append(float(min_ram))

        if min_storage is not None:
            where_clauses.append("s.storage >= ?")
            params.append(float(min_storage))

        if min_battery is not None:
            where_clauses.append("s.battery_cap >= ?")
            params.append(int(min_battery))

        if min_camera is not None:
            where_clauses.append("s.primary_rear_camera >= ?")
            params.append(float(min_camera))

        if has_5g is not None:
            where_clauses.append("s.has_5g = ?")
            params.append(has_5g.strip().capitalize())

        if display_type:
            where_clauses.append("s.display_type LIKE ?")
            params.append(f"%{display_type.strip().lower()}%")

        if min_refresh_rate is not None:
            where_clauses.append("s.refresh_rate >= ?")
            params.append(float(min_refresh_rate))

        if processor_brand:
            where_clauses.append("s.processor_brand LIKE ?")
            params.append(f"%{processor_brand.strip().lower()}%")

        # Exclude zero or corrupt metrics for ascending metric sorts
        if sort_by == "battery_asc":
            where_clauses.append("s.battery_cap > 0")
        elif sort_by == "ram_asc":
            where_clauses.append("s.ram > 0")
        elif sort_by == "camera_asc":
            where_clauses.append("s.primary_rear_camera > 0")
        elif sort_by == "storage_asc":
            where_clauses.append("s.storage > 0")

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Total matching count
        count_sql = f"SELECT count(*) FROM smartphones s {where_sql}"
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()[0]

        # Query Relaxation: if FTS residual keywords returned 0 results, but concrete structured filters were present
        has_concrete_filter = any([
            min_price is not None,
            max_price is not None,
            min_ram is not None,
            min_storage is not None,
            min_battery is not None,
            min_camera is not None,
            has_5g is not None,
            display_type is not None,
            min_refresh_rate is not None,
            processor_brand is not None,
        ])
        if total_count == 0 and residual_tokens and relax_query and has_concrete_filter:
            where_clauses_relaxed = [c for c in where_clauses if "smartphones_fts" not in c]
            params_relaxed = [p for p in params if p != fts_query]
            where_sql_relaxed = ("WHERE " + " AND ".join(where_clauses_relaxed)) if where_clauses_relaxed else ""
            cursor.execute(f"SELECT count(*) FROM smartphones s {where_sql_relaxed}", params_relaxed)
            relaxed_count = cursor.fetchone()[0]
            if relaxed_count > 0:
                total_count = relaxed_count
                where_sql = where_sql_relaxed
                params = params_relaxed

        # If min_camera was auto-inferred and returned 0 products, relax min_camera
        if total_count == 0 and min_camera is not None and "s.primary_rear_camera >= ?" in where_clauses:
            where_clauses_no_cam = [c for c in where_clauses if "s.primary_rear_camera" not in c]
            params_no_cam = [p for p, c in zip(params, where_clauses) if "s.primary_rear_camera" not in c]
            where_sql_no_cam = ("WHERE " + " AND ".join(where_clauses_no_cam)) if where_clauses_no_cam else ""
            cursor.execute(f"SELECT count(*) FROM smartphones s {where_sql_no_cam}", params_no_cam)
            no_cam_count = cursor.fetchone()[0]
            if no_cam_count > 0:
                total_count = no_cam_count
                where_sql = where_sql_no_cam
                params = params_no_cam

        # Sorting
        sort_sql_map = {
            "price_asc": "s.price ASC",
            "price_desc": "s.price DESC",
            "battery_asc": "s.battery_cap ASC, s.price ASC",
            "battery_desc": "s.battery_cap DESC, s.price DESC",
            "ram_asc": "s.ram ASC, s.price ASC",
            "ram_desc": "s.ram DESC, s.price DESC",
            "camera_asc": "s.primary_rear_camera ASC, s.price ASC",
            "camera_desc": "s.primary_rear_camera DESC, s.price DESC",
            "storage_asc": "s.storage ASC, s.price ASC",
            "storage_desc": "s.storage DESC, s.price DESC",
            "relevance": (
                "(s.ram >= 4) DESC, s.price DESC, s.primary_rear_camera DESC"
                if max_price is not None
                else ("s.price DESC" if not residual_tokens else "s.id ASC")
            ),
        }
        order_by = sort_sql_map.get(sort_by, "s.price DESC")

        # Query products
        select_sql = f"""
            SELECT s.*
            FROM smartphones s
            {where_sql}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        cursor.execute(select_sql, params + [limit, offset])
        rows = [dict(row) for row in cursor.fetchall()]

        # Faceted aggregation across results
        facets = self._calculate_facets(cursor, where_sql, params)
        conn.close()

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

        result = {
            "total_matches": total_count,
            "limit": limit,
            "offset": offset,
            "products": rows,
            "facets": facets,
            "execution_time_ms": elapsed_ms,
            "from_cache": False,
        }

        # Cache search result
        self.cache.set(cache_key, result, ttl=settings.search_cache_ttl_seconds)
        return result

    def _calculate_facets(
        self, cursor: sqlite3.Cursor, where_sql: str, params: list
    ) -> dict[str, Any]:
        """Computes multi-dimensional search facets (brands, price brackets, 5G)."""
        facets = {
            "brands": {},
            "price_ranges": {
                "Under 15k": 0,
                "15k - 30k": 0,
                "30k - 60k": 0,
                "Above 60k": 0,
            },
            "has_5g": {"Yes": 0, "No": 0},
        }

        # Top 6 Brands in matched subset
        brand_sql = f"""
            SELECT s.brand, count(*) as cnt
            FROM smartphones s
            {where_sql}
            GROUP BY s.brand
            ORDER BY cnt DESC
            LIMIT 6
        """
        cursor.execute(brand_sql, params)
        for row in cursor.fetchall():
            facets["brands"][row[0]] = row[1]

        # 5G counts
        fg_sql = f"""
            SELECT s.has_5g, count(*) as cnt
            FROM smartphones s
            {where_sql}
            GROUP BY s.has_5g
        """
        cursor.execute(fg_sql, params)
        for row in cursor.fetchall():
            if row[0] in facets["has_5g"]:
                facets["has_5g"][row[0]] = row[1]

        # Price range buckets
        price_bucket_sql = f"""
            SELECT 
                SUM(CASE WHEN s.price < 15000 THEN 1 ELSE 0 END) as b1,
                SUM(CASE WHEN s.price >= 15000 AND s.price <= 30000 THEN 1 ELSE 0 END) as b2,
                SUM(CASE WHEN s.price > 30000 AND s.price <= 60000 THEN 1 ELSE 0 END) as b3,
                SUM(CASE WHEN s.price > 60000 THEN 1 ELSE 0 END) as b4
            FROM smartphones s
            {where_sql}
        """
        cursor.execute(price_bucket_sql, params)
        prow = cursor.fetchone()
        if prow:
            facets["price_ranges"]["Under 15k"] = prow[0] or 0
            facets["price_ranges"]["15k - 30k"] = prow[1] or 0
            facets["price_ranges"]["30k - 60k"] = prow[2] or 0
            facets["price_ranges"]["Above 60k"] = prow[3] or 0

        return facets

    def get_by_id(self, product_id: int) -> dict[str, Any] | None:
        """Fast O(1) product lookup by primary key."""
        cache_key = f"prod:{product_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        conn = get_db_connection(self.db_path, read_only=True)
        cur = conn.cursor()
        cur.execute("SELECT * FROM smartphones WHERE id = ?", (product_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            res = dict(row)
            self.cache.set(cache_key, res, ttl=settings.exact_cache_ttl_seconds)
            return res
        return None

    def compare_products(self, name_a: str, name_b: str) -> dict[str, Any]:
        """Compares two phones side by side."""
        prod_a = self.search(query=name_a, limit=1)
        prod_b = self.search(query=name_b, limit=1)

        item_a = prod_a["products"][0] if prod_a["products"] else None
        item_b = prod_b["products"][0] if prod_b["products"] else None

        return {
            "product_a": item_a,
            "product_b": item_b,
            "found_both": bool(item_a and item_b),
        }

    def update_product_price(self, product_id: int, new_price: int) -> bool:
        """
        Updates a smartphone's price in SQLite and evicts corresponding L1/L2 caches.
        Demonstrates cache invalidation upon inventory/price mutation.
        """
        conn = get_db_connection(self.db_path, read_only=False)
        cur = conn.cursor()
        cur.execute(
            "UPDATE smartphones SET price = ? WHERE id = ?",
            (int(new_price), int(product_id)),
        )
        affected = cur.rowcount
        conn.commit()
        conn.close()

        if affected > 0:
            # 1. Evict direct product item cache
            self.cache.delete(f"prod:{product_id}")
            # 2. Invalidate all search query caches to ensure fresh pricing
            self.cache.invalidate_prefix("search:")
            return True
        return False
