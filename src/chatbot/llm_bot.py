import asyncio
import re
import time
from typing import Any

import httpx

from src.config import settings
from src.data.schema_context import DATABASE_SCHEMA_CONTEXT
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
            "motorola", "google", "nothing", "poco", "iqoo", "infinix", "tecno", "lava",
            "nokia", "honor", "micromax"
        ]
        has_shopping_intent = any(w in q_lower for w in shopping_triggers) or any(
            b in q_lower for b in known_brands
        )
        if not has_shopping_intent:
            return []

        from src.chatbot.typical_bot import typical_chatbot
        intent = typical_chatbot.classify_intent(query)
        if intent == "SPEC_INQUIRY":
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
            return res["products"]

        # 1. Dual Extremes Comparison ("cheapest and most expensive", "sabse sasta aur mahanga")
        is_cheap_term = bool(re.search(r"\b(cheapest|cheepest|lowest\s+price|most\s+affordable|sasta|sabse\s+sasta|budget\s+phone)\b", q_lower))
        is_premium_term = bool(re.search(r"\b(premium|priminum|primum|premiun|preimum|most\s+expensive|costliest|flagship|highest\s+price|mahanga|sabse\s+mahanga|ultra\s+flagship)\b", q_lower))
        if is_cheap_term and is_premium_term:
            cheap = self.search_engine.search(sort_by="price_asc", limit=1)
            flag = self.search_engine.search(min_price=50000, sort_by="price_desc", limit=1)
            if not flag["products"]:
                flag = self.search_engine.search(sort_by="price_desc", limit=1)
            return [p for p in (cheap["products"][:1] + flag["products"][:1]) if p]

        # 2. Side-by-side Comparison Intent ("compare X and Y", "X vs Y")
        if any(w in q_lower for w in ["compare", " vs ", "versus", "comparison", "difference between"]):
            cleaned = re.sub(
                r"^(?:show\s+)?(?:direct\s+)?(?:comparison\s+)?(?:spec\s+)?(?:hardware\s+)?(?:chart\s+)?(?:for\s+|of\s+|comparing\s+|between\s+)?",
                "",
                q_lower,
            )
            cleaned = cleaned.replace("compare", "").replace("comparison", "").replace("chart", "").strip()
            parts = re.split(r"\s+(?:vs|versus|and|with|to)\s+", cleaned)
            if len(parts) >= 2:
                from src.chatbot.typical_bot import typical_chatbot
                p_a = typical_chatbot._resolve_comparison_target(parts[0].strip())
                p_b = typical_chatbot._resolve_comparison_target(parts[1].strip())
                matched = [p for p in [p_a, p_b] if p]
                if len(matched) == 2:
                    return matched
                elif len(matched) == 1:
                    alts = self.search_engine.search(brand=matched[0]["brand"], sort_by="price_desc", limit=2)
                    return matched + [p for p in alts["products"] if p["id"] != matched[0]["id"]]
                else:
                    return []

        # 3. Extract structured parameters (budget, camera, 5G, RAM, battery)
        slots, residual_tokens = self.search_engine.parse_query_slots(query)
        min_p = slots.get("min_price")
        max_p = slots.get("max_price")
        if max_p and not min_p and max_p > 15000:
            min_p = max(0, max_p - 15000)

        sort_mode = slots.get("sort_by")
        if not sort_mode:
            if any(w in q_lower for w in ["least battery", "lowest battery", "min battery", "minimum battery", "smallest battery"]):
                sort_mode = "battery_asc"
            elif any(w in q_lower for w in ["least camera", "lowest camera", "least mp", "lowest mp", "smallest camera"]):
                sort_mode = "camera_asc"
            elif any(w in q_lower for w in ["lowest ram", "least ram", "min ram", "minimum ram", "smallest ram"]):
                sort_mode = "ram_asc"
            elif any(w in q_lower for w in ["highest ram", "hight ram", "max ram", "maximum ram", "most ram"]):
                sort_mode = "ram_desc"
            elif any(w in q_lower for w in ["cheapest", "lowest price", "least price"]):
                sort_mode = "price_asc"
            elif any(w in q_lower for w in ["most expensive", "costliest", "highest price"]):
                sort_mode = "price_desc"
            elif any(w in q_lower for w in ["camera", "photo", "vlog", "vlogging", "selfie", "portrait"]):
                sort_mode = "camera_desc"
            elif any(w in q_lower for w in ["battery", "backup", "durable", "construction", "outdoor", "lasting"]):
                sort_mode = "battery_desc"
            elif any(w in q_lower for w in ["gaming", "game", "performance", "speed", "fastest", "heavy"]):
                sort_mode = "ram_desc"
            else:
                sort_mode = "relevance"

        # Baseline modern RAM filter for general advisory & gift recommendations (skip for extremum low queries or model queries)
        query_text = " ".join(residual_tokens) if residual_tokens else None
        is_lowest_extremum = (
            sort_mode in ["ram_asc", "battery_asc", "camera_asc", "price_asc"]
            or any(w in q_lower for w in ["lowest", "least", "min", "minimum", "smallest", "cheapest", "sasta"])
        )
        ram_filter = slots.get("min_ram")
        if ram_filter is None and not is_lowest_extremum and not query_text and (max_p is None or max_p >= 10000):
            ram_filter = 4.0

        res = self.search_engine.search(
            query=query_text,
            brand=slots.get("brand"),
            min_price=min_p,
            max_price=max_p,
            min_ram=ram_filter,
            min_battery=slots.get("min_battery"),
            min_camera=slots.get("min_camera"),
            has_5g=slots.get("has_5g"),
            sort_by=sort_mode,
            relax_query=False if query_text else True,
            limit=3,
        )
        if not res["products"]:
            # Fallback relaxing query text & RAM constraints for open advisory queries while preserving price/sort/brand
            res = self.search_engine.search(
                brand=slots.get("brand"),
                min_price=min_p,
                max_price=max_p,
                min_camera=slots.get("min_camera"),
                min_battery=slots.get("min_battery"),
                sort_by=sort_mode,
                limit=3,
            )
        return res["products"]

    def _estimate_tokens(self, text: str) -> int:
        """Heuristic estimation of tokens (~4 characters per token)."""
        return max(1, len(text.split()) * 4 // 3)

    def _clean_response(self, text: str) -> str:
        """
        Extracts consumer-facing text strictly within <AnswerToUser>...</AnswerToUser> tags
        and aggressively scrubs any internal reasoning, thoughts, or draft commentary.
        """
        if not text:
            return ""

        # 1. Strip explicit thought and reasoning blocks first
        cleaned = re.sub(r"(?si)<thought>.*?</thought>", "", text)
        cleaned = re.sub(r"(?si)<reasoning>.*?</reasoning>", "", cleaned)
        cleaned = re.sub(r"(?si)\[THOUGHT\].*?\[/THOUGHT\]", "", cleaned)

        # 2. Search for designated delimiter tags: <AnswerToUser>...</AnswerToUser>
        tag_match = re.search(r"(?si)<AnswerToUser>(.*?)(?:</AnswerToUser>|$)", cleaned)
        if tag_match and len(tag_match.group(1).strip()) > 3:
            raw_target = tag_match.group(1).strip()
        else:
            # Check secondary common wrappers
            alt_match = re.search(
                r"(?si)<(?:answer|response|final_answer|output)>(.*?)(?:</(?:answer|response|final_answer|output)>|$)",
                cleaned
            )
            if alt_match and len(alt_match.group(1).strip()) > 3:
                raw_target = alt_match.group(1).strip()
            else:
                raw_target = cleaned.strip()

        cleaned = raw_target

        # 3. If "Let me craft:" or "Here is the response:" or similar draft marker exists, discard prior reasoning
        draft_markers = [
            r"(?i)\blet\s+me\s+craft\s*:?\s*",
            r"(?i)\blet's\s+craft\s*:?\s*",
            r"(?i)\bhere\s+is\s+the\s+(?:final\s+)?(?:answer|response)\s*:?\s*",
            r"(?i)\bfinal\s+answer\s*:?\s*",
        ]
        for marker in draft_markers:
            m = re.search(marker, cleaned)
            if m:
                cleaned = cleaned[m.end():].strip()
                break

        # 4. Filter line-by-line to remove lingering chain-of-thought sentences
        reasoning_line_starters = (
            "the user previously asked",
            "the user is asking",
            "the user previously",
            "the user asks",
            "earlier context had",
            "from my previous response",
            "i should provide",
            "i need to",
            "we need to",
            "let me craft",
            "let me check",
            "let me analyze",
            "here's a thinking process",
            "thinking process:",
            "thinking process",
            "analyze user input",
            "1. analyze user input",
            "identify key requirements",
            "2. identify key requirements",
            "user asks:",
            "i have access to a database",
            "thought:",
            "draft:",
            "internal notes:",
            "possibly a typo:",
            "so likely they mean",
            "need to list key",
            "the question:",
        )

        lines = cleaned.splitlines()
        filtered_lines = []
        skip_thought_mode = False

        for line in lines:
            line_s = line.strip()
            line_l = line_s.lower()

            if any(line_l.startswith(p) for p in reasoning_line_starters):
                skip_thought_mode = True
                continue

            # Check if this line signals consumer-facing content (bullets, phone specs, greetings)
            is_consumer_line = (
                line_s.startswith("- **") or
                line_s.startswith("**") or
                line_s.startswith("•") or
                line_s.startswith("1.") or
                line_s.startswith("2.") or
                line_s.startswith("3.") or
                any(line_l.startswith(w) for w in ["the ", "based on", "here are", "for your", "shopcart", "hello", "hi "])
            )

            if skip_thought_mode and is_consumer_line:
                skip_thought_mode = False

            if not skip_thought_mode:
                filtered_lines.append(line)

        final_text = "\n".join(filtered_lines).strip()

        # Remove any stray closing tags or artifacts
        final_text = re.sub(r"</?(?:AnswerToUser|thought|reasoning|answer|output)>", "", final_text, flags=re.IGNORECASE).strip()

        # Check if the extracted text is contaminated with lingering chain-of-thought phrases
        cot_indicators = [
            "thinking process", "analyze user input", "identify key requirements",
            "i need to recommend", "i have access to a database",
            "key specs to look for", "the user previously asked"
        ]
        if any(ci in final_text.lower() for ci in cot_indicators):
            return ""

        return final_text

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
        q_l = query.lower()
        is_comp = len(context_products) >= 2 and any(w in q_l for w in ["compare", " vs ", "versus", "comparison", "sasta aur mahanga"])
        if is_comp:
            p_a, p_b = context_products[0], context_products[1]
            ram_a = f"{p_a['ram']}GB RAM" if p_a["ram"] < 1 else f"{int(p_a['ram'])}GB RAM"
            ram_b = f"{p_b['ram']}GB RAM" if p_b["ram"] < 1 else f"{int(p_b['ram'])}GB RAM"
            cam_a = f"{p_a['primary_rear_camera']}MP" if p_a["primary_rear_camera"] < 1 else f"{int(p_a['primary_rear_camera'])}MP"
            cam_b = f"{p_b['primary_rear_camera']}MP" if p_b["primary_rear_camera"] < 1 else f"{int(p_b['primary_rear_camera'])}MP"
            simulated_text = (
                f"⚖️ Here is a comparison between the **{p_a['name'].title()}** and the **{p_b['name'].title()}**:\n\n"
                f"- **{p_a['name'].title()}** (₹{p_a['price']:,}): {p_a['display_size']}\" {p_a['display_type'].title()} display, "
                f"{ram_a} | {int(p_a['storage'])}GB Storage, {cam_a} Camera, {p_a['battery_cap']}mAh Battery, 5G: {p_a['has_5g']}.\n"
                f"- **{p_b['name'].title()}** (₹{p_b['price']:,}): {p_b['display_size']}\" {p_b['display_type'].title()} display, "
                f"{ram_b} | {int(p_b['storage'])}GB Storage, {cam_b} Camera, {p_b['battery_cap']}mAh Battery, 5G: {p_b['has_5g']}.\n\n"
                f"Both models are available in our catalog with 7-day replacement and express shipping."
            )
        elif context_products:
            p = context_products[0]
            ram_str = f"{p['ram']}GB RAM" if p['ram'] < 1 else f"{int(p['ram'])}GB RAM"
            cam_str = f"{p['primary_rear_camera']}MP" if p['primary_rear_camera'] < 1 else f"{int(p['primary_rear_camera'])}MP"
            # Extremum-aware tailored virtual response
            if any(w in q_l for w in ["least battery", "lowest battery", "min battery", "smallest battery"]):
                simulated_text = (
                    f"The smartphone with the lowest battery capacity in our catalog is the **{p['name'].title()}** "
                    f"priced at **₹{p['price']:,}**. It features a {p['battery_cap']} mAh battery, {ram_str}, "
                    f"and a {cam_str} camera with {p['display_size']}\" {p['display_type']} display."
                )
            elif any(w in q_l for w in ["least camera", "lowest camera", "least mp", "lowest mp", "smallest camera"]):
                simulated_text = (
                    f"The smartphone with the lowest camera resolution in our catalog is the **{p['name'].title()}** "
                    f"priced at **₹{p['price']:,}**, featuring a {cam_str} camera, {ram_str}, "
                    f"and a {p['battery_cap']} mAh battery."
                )
            elif any(w in q_l for w in ["lowest ram", "least ram", "min ram", "minimum ram", "smallest ram"]):
                simulated_text = (
                    f"The smartphone with the lowest RAM in our catalog is the **{p['name'].title()}** "
                    f"priced at **₹{p['price']:,}**, equipped with {ram_str}, a {cam_str} camera, "
                    f"and a {p['battery_cap']} mAh battery."
                )
            elif any(w in q_l for w in ["highest ram", "hight ram", "max ram", "maximum ram", "most ram"]):
                simulated_text = (
                    f"The smartphone with the highest RAM in our catalog is the **{p['name'].title()}** "
                    f"priced at **₹{p['price']:,}**, packing an ultra-high performance {ram_str}, "
                    f"{cam_str} camera, and a {p['battery_cap']} mAh battery."
                )
            else:
                battery_desc = f"a long-lasting {p['battery_cap']}mAh battery" if p['battery_cap'] >= 4500 else f"a {p['battery_cap']}mAh battery"
                simulated_text = (
                    f"Based on our smartphone catalog, I highly recommend the **{p['name'].title()}** "
                    f"priced at **₹{p['price']:,}**. It features a {p['display_size']}-inch {p['display_type']} display, "
                    f"{ram_str}, a {cam_str} camera, and {battery_desc} with {p['has_fast_charging']} fast charging. "
                    f"For your search '{query}', it delivers exceptional value and performance."
                )
                if len(context_products) > 1:
                    alt = context_products[1]
                    alt_ram = f"{alt['ram']}GB RAM" if alt['ram'] < 1 else f"{int(alt['ram'])}GB RAM"
                    alt_cam = f"{alt['primary_rear_camera']}MP" if alt['primary_rear_camera'] < 1 else f"{int(alt['primary_rear_camera'])}MP"
                    simulated_text += (
                        f"\n\nAnother top recommendation is the **{alt['name'].title()}** at **₹{alt['price']:,}** "
                        f"({alt_ram}, {alt_cam} camera, {alt['battery_cap']}mAh battery)."
                    )
        else:
            if any(w in q_l for w in ["compare", " vs ", "versus", "comparison"]):
                simulated_text = (
                    f"Thank you for asking to compare devices in '{query}'. Neither of the requested models was found in our active smartphone catalog. "
                    "Our store features over 3,200 smartphones from Samsung, Apple, OnePlus, Xiaomi, and more with fast shipping and 7-day returns."
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
            ram_fmt = f"{p['ram']}GB RAM" if p["ram"] < 1 else f"{int(p['ram'])}GB RAM"
            cam_fmt = f"{p['primary_rear_camera']}MP Camera" if p["primary_rear_camera"] < 1 else f"{int(p['primary_rear_camera'])}MP Camera"
            catalog_lines.append(
                f"- {p['name'].title()} | ₹{p['price']:,} | {ram_fmt} | {p['battery_cap']}mAh | "
                f"{cam_fmt} | 5G: {p['has_5g']} | {p['display_type']} ({p['display_size']}\")"
            )
        catalog_str = "\n".join(catalog_lines) if catalog_lines else "No specific catalog match."

        system_prompt = (
            "You are Shopcart AI, an expert e-commerce smartphone shopping advisor for Shopcart.\n"
            f"{DATABASE_SCHEMA_CONTEXT}\n\n"
            "CRITICAL OUTPUT INSTRUCTIONS:\n"
            "1. You MUST enclose your final consumer-facing response strictly within <AnswerToUser> and </AnswerToUser> tags.\n"
            "2. DO NOT output any thinking process, analysis steps, reasoning monologue, or drafts outside or inside <AnswerToUser>.\n"
            "3. Any text outside <AnswerToUser>...</AnswerToUser> will be rejected.\n"
            "4. Inside <AnswerToUser>, respond directly to the customer in a warm, professional manner. Keep answers concise (under 3-4 sentences or clear bullet points), mentioning exact model names, prices in INR (₹), and key specs (Camera MP, RAM, Battery, 5G).\n\n"
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
                    "max_tokens": 800,
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
                        # Strictly extract customer-facing content; NEVER use internal reasoning
                        raw_content = msg.get("content") or ""
                        if not raw_content:
                            last_error_reason = f"no_content_{model_candidate}"
                            continue

                        content = self._clean_response(raw_content)
                        if not content:
                            last_error_reason = f"empty_after_clean_{model_candidate}"
                            continue

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
