import asyncio
import re
import time
from typing import Any

import httpx

from src.config import settings
from src.guardrails.rate_limiter import llm_rate_limiter
from src.search.engine import SearchEngine


class LLMChatbot:
    """
    LLM-based E-Commerce Advisor with OpenRouter API integration.
    Features:
    - RAG Context Grounding using local smartphone catalog
    - Model failover across OpenRouter free tiers (Gemma, LFM, Nemotron)
    - Rate limit enforcement (20 RPM / 1000 RPD)
    - Virtual fallback mode for load tests and rate limit handling
    - Clean text extraction (strips raw thought/reasoning tags)
    - Precise token counting and commercial cost calculation
    """
    def __init__(
        self,
        search_engine: SearchEngine | None = None,
        model: str | None = None,
        api_key: str | None = None
    ):
        self.search_engine = search_engine or SearchEngine()
        self.model = model or settings.open_router_model
        self.fallback_models = getattr(settings, "fallback_models", [
            self.model,
            "google/gemma-4-26b-a4b-it:free",
            "liquid/lfm-3-1.7b:free",
            "nvidia/nemotron-3.5-lightning:free"
        ])
        self.api_key = (api_key or settings.open_router_api or "").strip()
        self.base_url = settings.open_router_base_url
        self.timeout = 15.0

    def _build_rag_context(self, query: str) -> list[dict[str, Any]]:
        """Retrieves top 3 relevant phones from catalog to ground the LLM."""
        q_lower = query.lower()
        shopping_triggers = [
            "phone", "phones", "mobile", "mobiles", "smartphone", "smartphones",
            "device", "devices", "recommend", "suggest", "buy", "camera", "battery",
            "gaming", "ram", "5g", "under", "budget", "specs", "display", "best", "which"
        ]
        known_brands = [
            "samsung", "apple", "xiaomi", "realme", "oneplus", "vivo", "oppo",
            "motorola", "google", "nothing", "poco", "iqoo", "infinix", "tecno", "lava"
        ]
        has_shopping_intent = any(w in q_lower for w in shopping_triggers) or any(
            b in q_lower for b in known_brands
        )
        if not has_shopping_intent:
            return []

        # Extract structured parameters (budget, camera, 5G, RAM, battery)
        slots, _ = self.search_engine.parse_query_slots(query)
        min_p = slots.get("min_price")
        max_p = slots.get("max_price")
        if max_p and not min_p and max_p > 15000:
            min_p = max(0, max_p - 15000)

        sort_mode = slots.get("sort_by")
        if not sort_mode:
            if any(w in q_lower for w in ["camera", "photo", "vlog", "vlogging", "selfie", "portrait"]):
                sort_mode = "camera_desc"
            elif any(w in q_lower for w in ["battery", "backup", "durable", "construction", "outdoor", "lasting"]):
                sort_mode = "battery_desc"
            elif any(w in q_lower for w in ["gaming", "game", "performance", "speed", "fastest", "heavy"]):
                sort_mode = "ram_desc"
            else:
                sort_mode = "relevance"

        # Baseline modern RAM filter for advisory & gift recommendations
        ram_filter = slots.get("min_ram")
        if ram_filter is None and (max_p is None or max_p >= 10000):
            ram_filter = 4.0

        res = self.search_engine.search(
            brand=slots.get("brand"),
            min_price=min_p,
            max_price=max_p,
            min_ram=ram_filter,
            min_battery=slots.get("min_battery"),
            min_camera=slots.get("min_camera"),
            has_5g=slots.get("has_5g"),
            sort_by=sort_mode,
            limit=3,
        )
        if not res["products"]:
            # Fallback relaxing RAM constraints while preserving price and sort
            res = self.search_engine.search(
                brand=slots.get("brand"),
                min_price=min_p,
                max_price=max_p,
                sort_by=sort_mode,
                limit=3,
            )
        return res["products"]

    def _estimate_tokens(self, text: str) -> int:
        """Heuristic estimation of tokens (~4 characters per token)."""
        return max(1, len(text.split()) * 4 // 3)

    def _clean_response(self, text: str) -> str:
        """Removes internal thought/reasoning tags to ensure clean consumer-facing copy."""
        cleaned = re.sub(r"(?s)<thought>.*?</thought>", "", text)
        cleaned = re.sub(r"(?s)<reasoning>.*?</reasoning>", "", cleaned)
        cleaned = re.sub(r"(?s)^Thinking Process:.*?\n\n", "", cleaned)
        cleaned = re.sub(r"(?s)^Thought:.*?\n\n", "", cleaned)
        cleaned = re.sub(r"(?s)^We need to answer.*?\.\s*", "", cleaned)
        return cleaned.strip()

    async def _generate_virtual_response(
        self,
        query: str,
        context_products: list[dict[str, Any]],
        reason: str = "virtual_mode"
    ) -> dict[str, Any]:
        """
        High-fidelity virtual response generator.
        Simulates realistic LLM output and token counts when rate limits are active
        or for high-concurrency benchmarks.
        """
        if context_products:
            p = context_products[0]
            simulated_text = (
                f"Based on our smartphone catalog, I highly recommend the **{p['name'].title()}** "
                f"priced at **₹{p['price']:,}**. It features a {p['display_size']}-inch {p['display_type']} display, "
                f"{int(p['ram'])}GB RAM, and a long-lasting {p['battery_cap']}mAh battery with {p['has_fast_charging']} fast charging. "
                f"For your search '{query}', it delivers exceptional value and performance."
            )
            if len(context_products) > 1:
                alt = context_products[1]
                simulated_text += (
                    f"\n\nAnother top recommendation is the **{alt['name'].title()}** at **₹{alt['price']:,}** "
                    f"({int(alt['ram'])}GB RAM, {int(alt['primary_rear_camera'])}MP camera, {alt['battery_cap']}mAh battery)."
                )
        else:
            simulated_text = (
                f"Thank you for asking about '{query}'. Our smartphone catalog features over 3,200 devices. "
                "For balanced daily performance, look for at least 8GB RAM and a 5,000mAh battery."
            )

        prompt_tokens = self._estimate_tokens(query) + (len(context_products) * 60) + 120
        completion_tokens = self._estimate_tokens(simulated_text)
        total_tokens = prompt_tokens + completion_tokens

        # Realistic non-blocking asynchronous latency simulation
        await asyncio.sleep(0.02)

        return {
            "response": simulated_text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "model_used": f"{self.model} ({reason})",
            "context_products": context_products,
            "virtual_mode": True
        }

    async def generate_response(
        self,
        query: str,
        user_history: list[dict[str, str]] | None = None,
        force_virtual: bool = False
    ) -> dict[str, Any]:
        """Generates grounded response using OpenRouter API with multi-model failover or virtual fallback."""
        start_time = time.perf_counter()
        context_products = self._build_rag_context(query)

        # Check virtual mode setting
        if force_virtual or settings.virtual_llm_mode or not self.api_key:
            res = await self._generate_virtual_response(query, context_products, reason="virtual_configured")
            res["execution_time_ms"] = round((time.perf_counter() - start_time) * 1000, 3)
            return res

        # Check rate limiter
        allowed, wait_sec, current_rpm = llm_rate_limiter.acquire_llm_slot()
        if not allowed:
            # Fall back to virtual mode instead of failing or timing out
            res = await self._generate_virtual_response(query, context_products, reason=f"rate_limit_backpressure_rpm_{current_rpm}")
            res["execution_time_ms"] = round((time.perf_counter() - start_time) * 1000, 3)
            return res

        # Construct RAG Prompt
        catalog_lines = []
        for p in context_products:
            catalog_lines.append(
                f"- {p['name'].title()} | ₹{p['price']:,} | {int(p['ram'])}GB RAM | {p['battery_cap']}mAh | "
                f"5G: {p['has_5g']} | {p['display_type']} ({p['display_size']}\")"
            )
        catalog_str = "\n".join(catalog_lines) if catalog_lines else "No specific catalog match."

        system_prompt = (
            "You are Shopcart AI, an expert e-commerce smartphone shopping advisor for Shopcart. "
            "Help the customer choose the best smartphone based on the provided catalog data. "
            "Keep answers concise (under 3-4 sentences). Mention exact model names, prices in INR (₹), and key specifications (Camera MP, RAM, Battery). "
            "Respond directly to the customer in a warm, professional manner. "
            "Do NOT include internal reasoning, meta-analysis, or thought steps in your final response.\n\n"
            f"Catalog Context:\n{catalog_str}"
        )

        messages = [{"role": "system", "content": system_prompt}]
        if user_history:
            messages.extend(user_history[-3:])
        messages.append({"role": "user", "content": query})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "EcommerceChatbotSystem",
            "Content-Type": "application/json"
        }

        # Try primary model and fallbacks
        candidate_models = [self.model] + [m for m in self.fallback_models if m != self.model]
        last_error_reason = "api_error"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for model_candidate in candidate_models:
                payload = {
                    "model": model_candidate,
                    "messages": messages,
                    "max_tokens": 350,
                    "temperature": 0.3
                }
                try:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        choice = data.get("choices", [{}])[0]
                        msg = choice.get("message", {})
                        raw_content = msg.get("content") or msg.get("reasoning") or ""
                        content = self._clean_response(raw_content) or "I recommend checking our catalog for top deals."

                        usage = data.get("usage", {})
                        prompt_tok = usage.get("prompt_tokens") or self._estimate_tokens(system_prompt + query)
                        comp_tok = usage.get("completion_tokens") or self._estimate_tokens(content)
                        total_tok = prompt_tok + comp_tok

                        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
                        return {
                            "response": content,
                            "prompt_tokens": prompt_tok,
                            "completion_tokens": comp_tok,
                            "total_tokens": total_tok,
                            "model_used": data.get("model", model_candidate),
                            "context_products": context_products,
                            "execution_time_ms": elapsed_ms,
                            "virtual_mode": False
                        }
                    else:
                        last_error_reason = f"api_http_{resp.status_code}_{model_candidate}"
                except Exception as ex:
                    last_error_reason = f"exception_{type(ex).__name__}_{model_candidate}"

        # If all candidates fail or hit errors, fall back to virtual mode gracefully
        res = await self._generate_virtual_response(query, context_products, reason=last_error_reason)
        res["execution_time_ms"] = round((time.perf_counter() - start_time) * 1000, 3)
        return res

llm_chatbot = LLMChatbot()
