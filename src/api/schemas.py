from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        ..., min_length=1, max_length=500, description="User query or search phrase"
    )
    mode: str = Field(
        "hybrid", description="Execution mode: hybrid, pure_llm, typical_only, google_adk"
    )
    user_id: str | None = Field("guest_user", description="Optional user identifier")
    session_id: str | None = Field(None, description="Optional Google ADK session identifier")
    history: list[dict[str, Any]] | None = Field(
        default=[], description="Recent multi-turn conversation history"
    )
    cart_items: list[dict[str, Any]] | None = Field(
        default=[], description="Current shopping cart items"
    )


class ProductCard(BaseModel):
    id: int
    name: str
    brand: str
    price: int
    ram: float
    storage: float
    battery_cap: int
    has_5g: str
    display_size: float
    display_type: str
    primary_rear_camera: float


class ChatResponse(BaseModel):
    query: str
    response: str
    routing_tier: str
    tokens_used: int
    tokens_saved: int
    cache_hit: bool
    similarity_score: float
    execution_time_ms: float
    pii_redacted: bool
    redactions: list[str] = []
    products: list[dict[str, Any]] | None = []
    model_used: str | None = None
    cart_action: dict[str, Any] | None = None
    action_chips: list[str] = []


class SearchRequest(BaseModel):
    query: str | None = None
    brand: str | None = None
    min_price: int | None = None
    max_price: int | None = None
    min_ram: float | None = None
    min_storage: float | None = None
    min_battery: int | None = None
    has_5g: str | None = None
    sort_by: str = "relevance"
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchResponse(BaseModel):
    total_matches: int
    limit: int
    offset: int
    products: list[dict[str, Any]]
    facets: dict[str, Any]
    execution_time_ms: float
    from_cache: bool


class GuardrailCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class GuardrailCheckResponse(BaseModel):
    is_safe: bool
    sanitized_text: str
    rejection_reason: str | None = None
    pii_detected: bool
    redactions: list[str] = []


class ProductPriceUpdateRequest(BaseModel):
    price: int = Field(..., gt=0, le=10000000, description="New price in INR")
