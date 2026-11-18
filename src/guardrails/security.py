import re
from typing import Any

from src.config import settings


class SecurityGuardrails:
    """Enterprise multi-layer security guardrails: SQL injection defense, prompt injection prevention, PII redaction, and output sensitive data scrubbing."""

    # SQL Injection attack patterns (Destructive, Stacked, Comments, Union, Tautology, Reconnaissance)
    SQL_INJECTION_PATTERNS = [
        # Destructive & DDL commands
        r"(?i)\b(?:drop|alter|truncate)\s+(?:table|database|index|view|schema)\b",
        r"(?i)\bdelete\s+from\b",
        r"(?i)\binsert\s+into\b",
        r"(?i)\bupdate\s+\w+\s+set\b",
        # Stacked query separators
        r"(?i);\s*(?:drop|delete|insert|update|alter|truncate|create|select|grant|revoke|exec|execute|shutdown)\b",
        # SQL comment tricks used for filter bypass
        r"(?:--|/\*|\*/|;\s*--)",
        # Union-based exfiltration
        r"(?i)\bunion\s+(?:all\s+)?select\b",
        # Boolean / Tautology blind injections (' OR 1=1, " OR ""=", ' OR '1'='1)
        r"(?i)(?:['\"\s]|^)or\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?",
        r"(?i)(?:['\"\s]|^)and\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?",
        r"(?i)['\"]\s*or\s*['\"]['\"]\s*=\s*['\"]",
        r"(?i)\bor\s+true\b",
        # Database internals & Schema reconnaissance
        r"(?i)\b(?:sqlite_master|sqlite_schema|sqlite_temp_master|information_schema|sys\.tables|pg_catalog)\b",
        r"(?i)\b(?:pragma\s+\w+|load_extension)\b",
        # Command execution & Time-based blind primitives
        r"(?i)\b(?:sleep\s*\(|benchmark\s*\(|waitfor\s+delay|xp_cmdshell|pg_sleep)\b",
    ]

    # Prompt injection and jailbreak patterns
    INJECTION_PATTERNS = [
        r"(?i)\b(?:ignore|disregard|forget)\s+(all\s+)?(?:previous|prior|above)\s+instructions\b",
        r"(?i)\breveal\s+(?:your\s+)?(?:system\s+prompt|hidden\s+instructions|secret\s+instructions)\b",
        r"(?i)\bwhat\s+(?:is|are)\s+(?:your\s+)?(?:system\s+prompt|instructions|hidden\s+rules|system\s+role)\b",
        r"(?i)\btell\s+me\s+(?:your\s+)?(?:system\s+prompt|initial\s+prompt|instructions|database\s+password|api\s*key)\b",
        r"(?i)\b(?:database\s+password|db\s*credentials|secret\s*key|api\s*key)\b",
        r"(?i)\byou\s+are\s+now\s+(?:in\s+)?(?:dan\s+mode|unrestricted|god\s+mode|developer\s+mode)\b",
        r"(?i)\bjailbreak\b",
        r"(?i)\bact\s+as\s+(?:an\s+unfiltered|an\s+evil|a\s+hacked)\b",
        r"(?i)\bpretend\s+you\s+have\s+no\s+(?:rules|ethics|guardrails)\b",
        r"(?i)\bprint\s+everything\s+above\b",
        r"(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
    ]

    # PII patterns
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    PHONE_PATTERN = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    CREDIT_CARD_PATTERN = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
    ID_PATTERN = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"  # e.g. Aadhaar/National ID format

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.sqlite_db_path
        self._sql_regexes = [re.compile(p) for p in self.SQL_INJECTION_PATTERNS]
        self._injection_regexes = [re.compile(p) for p in self.INJECTION_PATTERNS]
        self._known_models_cache: set | None = None

    def inspect_input(self, text: str) -> dict[str, Any]:
        """
        Scans input for security threats:
        1. Length & Complexity DoS check
        2. Prompt injection & jailbreak detection
        3. PII detection and redaction
        """
        if not text:
            return {
                "is_safe": True,
                "sanitized_text": "",
                "rejection_reason": None,
                "pii_detected": False,
                "redactions": [],
            }

        # 1. DoS / Length Check
        if len(text) > 500:
            return {
                "is_safe": False,
                "sanitized_text": text[:500],
                "rejection_reason": "Query exceeds maximum allowed length of 500 characters (DoS protection).",
                "pii_detected": False,
                "redactions": [],
            }

        # Repetitive character spam
        if len(text) > 20 and len(set(text)) <= 3:
            return {
                "is_safe": False,
                "sanitized_text": text,
                "rejection_reason": "Query contains invalid repetitive characters (Spam protection).",
                "pii_detected": False,
                "redactions": [],
            }

        # 2. SQL Injection Check (Anti-Hacking & Database Integrity Protection)
        for regex in self._sql_regexes:
            if regex.search(text):
                return {
                    "is_safe": False,
                    "sanitized_text": text,
                    "rejection_reason": "Security Alert: Malicious SQL injection or database tampering attempt blocked.",
                    "pii_detected": False,
                    "redactions": [],
                }

        # 3. Prompt Injection / Jailbreak / System Prompt Extraction Check
        for regex in self._injection_regexes:
            if regex.search(text):
                return {
                    "is_safe": False,
                    "sanitized_text": text,
                    "rejection_reason": "Security Alert: Prompt injection or system prompt extraction attempt detected.",
                    "pii_detected": False,
                    "redactions": [],
                }

        # 4. PII Redaction
        sanitized = text
        redactions = []

        if re.search(self.EMAIL_PATTERN, sanitized):
            sanitized = re.sub(self.EMAIL_PATTERN, "[REDACTED_EMAIL]", sanitized)
            redactions.append("email")

        if re.search(self.CREDIT_CARD_PATTERN, sanitized):
            sanitized = re.sub(
                self.CREDIT_CARD_PATTERN, "[REDACTED_PAYMENT_INFO]", sanitized
            )
            redactions.append("credit_card")

        if re.search(self.PHONE_PATTERN, sanitized):
            sanitized = re.sub(self.PHONE_PATTERN, "[REDACTED_PHONE]", sanitized)
            redactions.append("phone_number")

        if re.search(self.ID_PATTERN, sanitized):
            sanitized = re.sub(self.ID_PATTERN, "[REDACTED_ID]", sanitized)
            redactions.append("national_id")

        return {
            "is_safe": True,
            "sanitized_text": sanitized,
            "rejection_reason": None,
            "pii_detected": len(redactions) > 0,
            "redactions": redactions,
        }

    def verify_output_grounding(
        self, response_text: str, context_products: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Output Guardrail: Checks if response mentions non-existent phones or hallucinated specs.
        """
        if not response_text:
            return {
                "grounding_score": 1.0,
                "hallucination_detected": False,
                "warnings": [],
            }

        warnings = []
        # Check if known brand names appear
        major_brands = [
            "samsung",
            "apple",
            "xiaomi",
            "vivo",
            "oppo",
            "oneplus",
            "realme",
            "motorola",
            "poco",
            "iqoo",
        ]
        mentioned_brands = [b for b in major_brands if b in response_text.lower()]

        # If context was provided, check if context models were respected
        if context_products:
            context_names = [p["name"].lower() for p in context_products]
            context_matched = any(
                any(token in response_text.lower() for token in name.split()[:2])
                for name in context_names
            )
            grounding_score = 0.95 if context_matched else 0.80
        else:
            grounding_score = 0.90

        # Check for extreme hallucinated price anomalies (e.g. ₹0 or ₹9999999)
        price_matches = re.findall(r"₹\s*(\d[\d,]*)", response_text)
        for p_str in price_matches:
            val = int(p_str.replace(",", ""))
            if val < 1000 or val > 300000:
                warnings.append(f"Unrealistic price detected: ₹{val}")
                grounding_score -= 0.3

        return {
            "grounding_score": max(0.0, round(grounding_score, 2)),
            "hallucination_detected": len(warnings) > 0 or grounding_score < 0.6,
            "warnings": warnings,
        }

    def scrub_sensitive_output(self, text: str) -> str:
        """
        Scans model output to ensure internal system secrets, filesystem paths,
        database schemas, or API keys are never leaked to consumer users.
        """
        if not text:
            return ""

        scrubbed = text

        # 1. Mask API keys or tokens
        scrubbed = re.sub(r"(?i)\b(?:Bearer\s+|sk-|api_key\s*[:=]\s*)[a-zA-Z0-9_\-\.]{16,}\b", "[REDACTED_API_KEY]", scrubbed)
        scrubbed = re.sub(r"\b[a-zA-Z0-9_\-]{32,}\b", "[REDACTED_TOKEN]", scrubbed)

        # 2. Mask absolute file paths and database connection strings
        scrubbed = re.sub(r"/(?:home|etc|var|usr|root)/[a-zA-Z0-9_\-\./]+", "[SYSTEM_PATH]", scrubbed)
        scrubbed = re.sub(r"[a-zA-Z]:\\[a-zA-Z0-9_\-\.\\]+", "[SYSTEM_PATH]", scrubbed)
        scrubbed = re.sub(r"(?i)\bdata/smartphones\.db\b", "catalog_database", scrubbed)

        # 3. Mask leaked system instructions or prompt delimiters
        scrubbed = re.sub(r"(?i)\byou are shopcart ai, an expert e-commerce.*?\n\n", "", scrubbed)
        scrubbed = re.sub(r"(?i)\bdo not include internal reasoning.*?\n", "", scrubbed)
        scrubbed = re.sub(r"</?AnswerToUser>", "", scrubbed, flags=re.IGNORECASE)

        # 4. Mask database schema statements
        scrubbed = re.sub(r"(?i)CREATE\s+TABLE\s+\w+\s*\(.*?\);?", "", scrubbed, flags=re.DOTALL)
        scrubbed = re.sub(r"(?i)\b(?:sqlite_master|sqlite_schema)\b", "catalog_table", scrubbed)

        return scrubbed.strip()


security_guardrails = SecurityGuardrails()
