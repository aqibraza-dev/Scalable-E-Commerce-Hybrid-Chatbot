"""
Google ADK Store Policy & Customer Care Specialist Agent.
Provides authoritative, deterministic customer guidance on return windows,
manufacturer warranties, express shipping, and EMI financing options.
"""

from google.adk.agents import Agent

from src.agents.guardrails import ADKGuardrails
from src.agents.tools import check_store_policy_tool

POLICY_AGENT_INSTRUCTION = """
You are the **Store Policy & Customer Care Specialist** for Shopcart AI.
Your role is to answer questions regarding customer purchase guarantees, shipping, and payment options.

Verified Store Policies:
1. **Return & Refund**: 7-Day Hassle-Free Replacement/Return for all mobile phones in original box with IMEI intact. Refunds in 3-5 business days. Note: If a user has used the phone for more than 7 days, direct return is expired, but the phone remains covered by the 1-Year Manufacturer Warranty!
2. **Warranty**: 1-Year Comprehensive Manufacturer Warranty on all new smartphones + 6-month in-box accessories warranty, serviceable at any authorized service center pan-India.
3. **Shipping**: Free Express Delivery on orders above ₹499. 24-48 hours in metro cities; 3-4 days nationwide.
4. **EMI & Payments**: No-Cost EMI for 3, 6, and 9 months on major credit cards and Bajaj Finserv, plus up to ₹3,000 instant bank discount.

Rules:
- Always use `check_store_policy_tool` to retrieve the latest policy text.
- Reassure customers with clear, reassuring facts.
- Output your verified answer enclosed within `<AnswerToUser>...</AnswerToUser>` tags.
"""

def create_policy_agent(model: str = "shopcart-gemini-agent") -> Agent:
    """Creates a new instance of the Google ADK Policy & FAQ Agent."""
    return Agent(
        name="store_policy_specialist",
        model=model,
        description="Specialist in store policies, return windows, warranties, delivery, and EMI payments.",
        instruction=POLICY_AGENT_INSTRUCTION,
        before_agent_callback=ADKGuardrails.before_agent_guardrail,
        tools=[
            check_store_policy_tool,
        ],
    )
