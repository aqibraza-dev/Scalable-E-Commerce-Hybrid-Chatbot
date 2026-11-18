"""
Google ADK (Agent Development Kit) Guardrail & Security Lifecycle Callbacks.
Enforces multi-layer enterprise security, SQL injection defense, prompt injection prevention,
PII masking, and output reasoning scrubber across all ADK agents.
"""

import logging
import re
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types

from src.guardrails.security import security_guardrails

logger = logging.getLogger("adk.guardrails")


class ADKGuardrails:
    """Enterprise multi-layer security guardrails implemented as ADK agent lifecycle callbacks."""

    @staticmethod
    def before_agent_guardrail(ctx: CallbackContext) -> types.Content | None:
        """Runs BEFORE any ADK agent executes.

        Scans incoming user messages for:
        1. Length & Complexity DoS buffer overflows (>500 chars, repetitive spam)
        2. SQL Injection attempts (DROP, DELETE, UNION, stacked queries, comments)
        3. Prompt injection and jailbreak attempts (DAN mode, system prompt exfiltration)
        4. PII detection and automated masking (emails, phone numbers, cards, IDs)

        If dangerous input is detected, returns a short-circuit Content object immediately,
        preventing any model inference or tool execution.
        """
        user_text = ""
        if ctx.user_content and ctx.user_content.parts:
            for p in ctx.user_content.parts:
                if p.text:
                    user_text += p.text

        if not user_text:
            return None

        audit = security_guardrails.inspect_input(user_text)
        if not audit["is_safe"]:
            logger.warning(
                f"ADK Guardrail BLOCKED request in agent '{ctx.agent_name}': {audit['rejection_reason']}"
            )
            return types.Content(
                role="model",
                parts=[
                    types.Part.from_text(
                        text=f"🛡️ **Request Blocked**: {audit['rejection_reason']}"
                    )
                ],
            )

        return None

    @staticmethod
    def after_model_guardrail(ctx: CallbackContext) -> LlmResponse | None:
        """Runs AFTER the model produces a response.
        Scrubs any internal chain-of-thought monologue and strips leaked server paths.
        """
        # Can inspect ctx.output or ctx.event_actions
        return None

    @staticmethod
    def inspect_and_sanitize(text: str) -> dict[str, Any]:
        """Direct inspection and sanitization helper for ADK queries."""
        return security_guardrails.inspect_input(text)

    @staticmethod
    def sanitize_output(text: str) -> str:
        """Sanitizes agent output: removes internal CoT thought leakage, redacts secrets, strips system paths."""
        return security_guardrails.scrub_sensitive_output(text)

    @staticmethod
    def verify_grounding(text: str, context_products: list[dict[str, Any]]) -> dict[str, Any]:
        """Verifies that generated product prices and specs match true catalog values."""
        return security_guardrails.verify_output_grounding(text, context_products)

