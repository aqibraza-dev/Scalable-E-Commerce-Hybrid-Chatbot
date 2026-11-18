import re
import threading
import time
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import settings
from src.search.cache import MultiTierCache, global_cache

SYNONYMS = {
    "mobile": "phone",
    "smartphones": "phone",
    "smartphone": "phone",
    "phones": "phone",
    "mobiles": "phone",
    "device": "phone",
    "top": "best",
    "cheapest": "budget",
    "cheap": "budget",
    "below": "under",
    "less": "under",
    "within": "under",
    "suggest": "recommend",
    "find": "recommend",
    "show": "recommend",
    "buy": "recommend",
    "give": "recommend",
    "get": "recommend",
    "least": "lowest",
    "min": "lowest",
    "minimum": "lowest",
    "smallest": "lowest",
    "max": "highest",
    "maximum": "highest",
    "most": "highest",
    "longest": "highest",
    "hight": "highest",
    "highet": "highest",
}

STOP_WORDS = {
    "what", "is", "the", "which", "are", "for", "in", "with", "a", "an",
    "of", "to", "me", "some", "i", "can", "you", "please", "want", "need",
    "tell", "about", "my", "hi", "hello", "hey",
    "has", "have", "had", "does", "do", "did", "where", "how", "whose", "whom",
    "give", "show", "get", "find", "suggest"
}

KNOWN_BRANDS = {
    "samsung", "apple", "xiaomi", "vivo", "oppo", "oneplus",
    "realme", "motorola", "iqoo", "poco", "tecno", "lava",
    "infinix", "google", "nothing", "nokia", "honor", "micromax"
}

class SemanticCache:
    """
    Enterprise Slot-Aware Semantic LLM Cache.
    Matches queries by semantic meaning using domain-aware normalization,
    TF-IDF Unigram vectors, and Cosine Similarity.
    Prevents false positive caching by ensuring critical enterprise slots (brand, price ceiling) match.
    """
    def __init__(
        self,
        threshold: float = 0.70,
        ttl_seconds: int | None = None,
        cache: MultiTierCache | None = None
    ):
        self.threshold = threshold
        self.ttl_seconds = ttl_seconds or settings.semantic_cache_ttl_seconds
        self.cache = cache or global_cache
        
        self.clean_regex = re.compile(r"[^a-zA-Z0-9\s]")
        
        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 1),
            lowercase=True,
            token_pattern=r"(?u)\b\w+\b"
        )
        
        # In-memory storage for active queries and vectors
        self._queries: list[str] = []
        self._raw_queries: list[str] = []
        self._vectors: np.ndarray | None = None
        self._records: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        
        # Base domain vocabulary corpus
        self._corpus: list[str] = [
            "recommend best 5g phone under 20000 rupees camera battery",
            "budget phone under 15000 8gb ram amoled display",
            "compare samsung galaxy s25 ultra oneplus 13 specifications",
            "return refund warranty policy mobile purchases",
            "fast charging 6000mah battery snapdragon processor",
            "gaming phone under 25000 120hz refresh rate",
            "apple iphone 15 pro max price discount warranty emi",
            "budget 5g phone high megapixel camera",
            "vivo v50 specifications display battery ram storage"
        ]
        self._rebuild_index()

    def normalize_text(self, text: str) -> str:
        """Domain-aware NLP normalization (currency, 'k' thousands, synonyms, stopwords)."""
        t = text.lower()
        t = re.sub(r"₹|rs\.?|inr", " rupees ", t)
        t = re.sub(r"\b(\d+)k\b", r"\g<1>000", t)
        t = self.clean_regex.sub(" ", t)
        tokens = t.split()
        norm_tokens = []
        for tok in tokens:
            if tok in STOP_WORDS:
                continue
            tok = SYNONYMS.get(tok, tok)
            norm_tokens.append(tok)
        return " ".join(norm_tokens)

    def extract_slots(self, text: str) -> dict[str, Any]:
        """Extracts brand, price, network, feature focus, and extremum direction for semantic precision."""
        t = text.lower()
        t = re.sub(r"₹|rs\.?|inr", " rupees ", t)
        t = re.sub(r"\b(\d+)k\b", r"\g<1>000", t)
        
        # 1. Brand extraction
        brand = None
        for b in KNOWN_BRANDS:
            if re.search(r"\b" + re.escape(b) + r"\b", t):
                brand = "xiaomi" if b == "redmi" else b
                break
                
        # 2. Price extraction (must be an explicit budget / price, not battery mah or screen size)
        price = None
        p_match = re.search(
            r"(?:under|below|not\s+above|not\s+over|less\s+than|within|upto|up\s+to|<=|<|budget\s+of|in|around)\s*(?:rupees)?\s*(\d{4,6})(?:\s*budget)?",
            t
        )
        if p_match:
            price = int(p_match.group(1))
        else:
            p_match2 = re.search(r"\b(\d{4,6})\s*(?:rupees|budget)\b", t)
            if p_match2:
                price = int(p_match2.group(1))

        # 3. 5G (respecting negations)
        has_5g = bool(re.search(r"\b5g\b", t)) and not bool(re.search(r"\b(not\s+5g|non\s+5g|no\s+5g)\b", t))
        # 4. Feature focus slot (battery, camera, ram, storage, price, display)
        feature = None
        if re.search(r"\b(?:battery|backup|mah|power)\b", t):
            feature = "battery"
        elif re.search(r"\b(?:camera|cameras|photo|photos|mp|megapixel|megapixels|selfie)\b", t):
            feature = "camera"
        elif re.search(r"\b(?:ram|memory)\b", t):
            feature = "ram"
        elif re.search(r"\b(?:storage|rom)\b", t):
            feature = "storage"
        elif re.search(r"\b(?:price|cost|daam|sasta|mahanga|budget|cheap|expensive|affordable)\b", t):
            feature = "price"
        elif re.search(r"\b(?:display|screen|amoled|oled|refresh\s*rate|hz)\b", t):
            feature = "display"

        # 5. Extremum direction slot (asc vs desc)
        direction = None
        if re.search(r"\b(?:least|lowest|min|minimum|smallest|cheapest|cheepest|sasta|kam|entry)\b", t):
            direction = "asc"
        elif re.search(r"\b(?:highest|hight|max|maximum|most|top|best|costliest|expensive|mahanga|jyada|zyada|flagship|premium|longest)\b", t):
            direction = "desc"

        # 6. Intent type (comparison vs single search)
        is_comp = bool(re.search(r"\b(?:compare|comparison|vs|versus|difference\s+between)\b", t))

        return {
            "brand": brand,
            "price": price,
            "has_5g": has_5g,
            "feature": feature,
            "direction": direction,
            "is_comp": is_comp,
        }

    def _rebuild_index(self) -> None:
        """Fits vectorizer on combined base corpus and cached queries."""
        all_docs = self._corpus + self._queries
        self._vectorizer.fit(all_docs)
        if self._queries:
            self._vectors = self._vectorizer.transform(self._queries)
        else:
            self._vectors = None

    def lookup(self, query: str) -> dict[str, Any] | None:
        """
        Performs two-phase lookup:
        Phase 1: O(1) Exact normalized hash check (100% token savings, ~0.05ms)
        Phase 2: Slot-aware semantic cosine similarity check (100% token savings, ~1-3ms)
        """
        normalized_q = self.normalize_text(query)
        if not normalized_q:
            return None

        # Phase 1: Exact Query Cache Check
        exact_key = self.cache.generate_key("exact_chat", normalized_q)
        exact_val = self.cache.get(exact_key)
        if exact_val is not None:
            return {
                "cache_hit": True,
                "cache_type": "exact_cache",
                "similarity_score": 1.0,
                "response": exact_val["response"],
                "products": exact_val.get("products", []),
                "tokens_saved": exact_val.get("tokens_saved", 350),
                "original_matched_query": exact_val.get("query", query)
            }

        # Phase 2: Semantic Similarity Check
        with self._lock:
            if not self._queries or self._vectors is None:
                return None

            try:
                query_slots = self.extract_slots(query)
                query_vec = self._vectorizer.transform([normalized_q])
                sims = cosine_similarity(query_vec, self._vectors)[0]

                # Filter by slot compatibility (prevent cross-brand or cross-price mismatch)
                best_score = -1.0
                best_idx = -1

                for idx, score in enumerate(sims):
                    if score < self.threshold:
                        continue
                    rec = self._records[idx]
                    rec_slots = rec.get("slots", {})

                    # If brand specified in either, they must match
                    if query_slots["brand"] != rec_slots.get("brand"):
                        continue

                    # If price specified in either, they must match
                    if query_slots["price"] != rec_slots.get("price"):
                        continue

                    # If 5G specified in either, both must match
                    if query_slots["has_5g"] != rec_slots.get("has_5g", False):
                        continue

                    # Feature focus (battery, camera, ram, etc.) must match if present
                    if query_slots["feature"] != rec_slots.get("feature"):
                        continue

                    # Extremum direction: conflict if one is 'asc' (least/lowest) and other is not
                    q_dir = query_slots.get("direction")
                    r_dir = rec_slots.get("direction")
                    if q_dir == "asc" or r_dir == "asc":
                        if q_dir != r_dir:
                            continue
                    elif q_dir and r_dir and q_dir != r_dir:
                        continue

                    # Comparison intent must match
                    if query_slots["is_comp"] != rec_slots.get("is_comp", False):
                        continue

                    if score > best_score:
                        best_score = float(score)
                        best_idx = idx

                if best_idx != -1 and best_score >= self.threshold:
                    record = self._records[best_idx]
                    if time.time() - record["stored_at"] < self.ttl_seconds:
                        return {
                            "cache_hit": True,
                            "cache_type": "semantic_cache",
                            "similarity_score": round(best_score, 4),
                            "response": record["response"],
                            "products": record.get("products", []),
                            "tokens_saved": record.get("tokens_saved", 350),
                            "original_matched_query": record["query"]
                        }
            except Exception:
                pass

        return None

    def store(
        self,
        query: str,
        response: str,
        prompt_tokens: int = 250,
        completion_tokens: int = 100,
        products: list[dict[str, Any]] | None = None
    ) -> None:
        """Stores query, response, and products in both Exact and Semantic cache."""
        normalized_q = self.normalize_text(query)
        if not normalized_q:
            return

        total_tokens = prompt_tokens + completion_tokens
        slots = self.extract_slots(query)
        prods_to_store = products or []

        # 1. Store in Exact Cache
        exact_key = self.cache.generate_key("exact_chat", normalized_q)
        exact_payload = {
            "query": query,
            "response": response,
            "products": prods_to_store,
            "tokens_saved": total_tokens,
            "stored_at": time.time(),
            "slots": slots
        }
        self.cache.set(exact_key, exact_payload, ttl=self.ttl_seconds)

        # 2. Store in Semantic Cache
        with self._lock:
            if normalized_q in self._queries:
                return

            record = {
                "query": query,
                "normalized_query": normalized_q,
                "response": response,
                "products": prods_to_store,
                "tokens_saved": total_tokens,
                "stored_at": time.time(),
                "slots": slots
            }
            self._raw_queries.append(query)
            self._queries.append(normalized_q)
            self._records.append(record)
            self._rebuild_index()

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "semantic_entries_count": len(self._queries),
                "threshold": self.threshold,
                "ttl_seconds": self.ttl_seconds
            }

    def clear(self) -> None:
        with self._lock:
            self._queries.clear()
            self._raw_queries.clear()
            self._records.clear()
            self._vectors = None
            self._rebuild_index()
        self.cache.invalidate_prefix("exact_chat:")

global_semantic_cache = SemanticCache()
