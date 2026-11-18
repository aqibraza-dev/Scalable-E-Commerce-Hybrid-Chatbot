"""
Google ADK Shopping Advisor & Cart Specialist Agent.
Provides personalized smartphone advice tailored to user lifestyles
(gaming, students, photography, vlogging, budget) and manages shopping cart actions.
"""

from google.adk.agents import Agent

from src.agents.guardrails import ADKGuardrails
from src.agents.tools import (
    get_phone_specs_tool,
    manage_cart_tool,
    search_catalog_tool,
)

ADVISOR_AGENT_INSTRUCTION = """
You are the **Shopping Advisor & Bag Specialist** for Shopcart AI.
Your role is to offer tailored lifestyle advice and help users add smartphones to their shopping cart.

Capabilities:
1. Recommend phones matching specific lifestyle needs (e.g. mobile gaming, college student budget, vlogging, long battery life).
2. Help users add smartphones to their shopping bag using `manage_cart_tool`.
3. Provide quick specification summaries before checkout using `get_phone_specs_tool`.

Rules:
- Give concise, grounded advice highlighting why a phone fits the customer's specific needs.
- Suggest promo code **NIKEAIR** for 15% discount at checkout.
- Format all prices in INR ₹ (e.g., ₹14,999).
- Enclose all responses within `<AnswerToUser>...</AnswerToUser>` tags.
"""

def create_advisor_agent(model: str = "shopcart-gemini-agent") -> Agent:
    """Creates a new instance of the Google ADK Shopping Advisor Agent."""
    return Agent(
        name="shopping_advisor_specialist",
        model=model,
        description="Specialist in personalized smartphone recommendations, lifestyle matching, and cart management.",
        instruction=ADVISOR_AGENT_INSTRUCTION,
        before_agent_callback=ADKGuardrails.before_agent_guardrail,
        tools=[
            search_catalog_tool,
            get_phone_specs_tool,
            manage_cart_tool,
        ],
    )
