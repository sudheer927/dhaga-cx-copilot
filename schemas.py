from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class IntentEnum(str, Enum):
    WISMO = "WISMO"                               # Where Is My Order / Delivery status
    RETURN_REQUEST = "RETURN_REQUEST"             # Size exchange, return garment
    REFUND_STATUS = "REFUND_STATUS"               # Account deducted, COD refund
    DEFECT_DAMAGE = "DEFECT_DAMAGE"               # Torn garment, wrong color/item
    ESCALATION_HOSTILE = "ESCALATION_HOSTILE"     # Abusive, threatening legal/consumer court
    GENERAL_INQUIRY = "GENERAL_INQUIRY"           # Offers, store timing, catalogue
    UNKNOWN = "UNKNOWN"

class SentimentEnum(str, Enum):
    CALM = "CALM"
    ANXIOUS = "ANXIOUS"
    FRUSTRATED = "FRUSTRATED"
    ABUSIVE = "ABUSIVE"

class UrgencyEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class TicketExtractionResult(BaseModel):
    """Structured output for Step 1: Router & Entity Extractor (Model A)"""
    intent: IntentEnum = Field(description="Primary category of the support inquiry")
    order_id: Optional[str] = Field(default=None, description="Extracted order ID like DH-10492 or similar")
    phone_number: Optional[str] = Field(default=None, description="Extracted phone number if mentioned")
    sentiment: SentimentEnum = Field(default=SentimentEnum.CALM, description="Customer emotional state")
    urgency: UrgencyEnum = Field(default=UrgencyEnum.LOW, description="Operational urgency")
    language: str = Field(default="Hinglish", description="Detected language (e.g. Hinglish, English, Hindi)")
    summary: str = Field(description="One-sentence English summary of the customer's core problem")
    product_mentioned: Optional[str] = Field(default=None, description="Product or garment type mentioned")
    confidence: float = Field(ge=0.0, le=1.0, description="Model classification confidence score")

class PolicyVerdictEnum(str, Enum):
    PASS_WITHIN_POLICY = "PASS_WITHIN_POLICY"
    FAIL_OUT_OF_POLICY = "FAIL_OUT_OF_POLICY"
    PARTIAL_EXCEPTION_REVIEW = "PARTIAL_EXCEPTION_REVIEW"

class PolicyCheckResult(BaseModel):
    """Structured output for Step 2: Deterministic Policy Check (Pure Code)"""
    eligible_for_auto_reply: bool
    policy_code: str
    policy_message: str
    policy_verdict: PolicyVerdictEnum = PolicyVerdictEnum.PASS_WITHIN_POLICY
    order_found: bool
    is_ambiguous: bool = False
    ambiguous_orders: List[str] = Field(default_factory=list)
    order_data: Optional[Dict[str, Any]] = None
    courier_events: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Granular date and policy gap audit for agents & automated out-of-policy handling
    order_placed_date: Optional[str] = None
    delivered_date: Optional[str] = None
    ticket_raised_date: Optional[str] = None
    days_gap: Optional[int] = None
    policy_threshold_days: int = 7
    checks_summary: List[Dict[str, Any]] = Field(default_factory=list)

class DraftResponseResult(BaseModel):
    """Structured output for Step 3: Response Drafter (Model A)"""
    reply_text: str = Field(description="Customer-facing reply in empathetic Hinglish or English")
    tone: str = Field(description="Tone of the message, e.g. Empathetic, Direct, Reassuring")
    includes_tracking_link: bool = Field(default=False)
    includes_edd: bool = Field(default=False)
    suggested_canned_macro: Optional[str] = None

class EvaluatorResult(BaseModel):
    """Structured output for Step 4: Evaluator-Optimizer (Model B)"""
    passed: bool = Field(description="Whether the draft meets accuracy and policy criteria")
    truthfulness_score: float = Field(ge=0.0, le=1.0, description="Verification that facts match DB")
    safety_score: float = Field(ge=0.0, le=1.0, description="Ensures no unauthorized promises or insults")
    hallucination_detected: bool = Field(default=False)
    feedback: str = Field(description="Explanation of the evaluation judgment")
    action: str = Field(description="AUTO_SEND, HUMAN_REVIEW, or ESCALATE_LEAD")

class CostMetric(BaseModel):
    """Telemetry record for token cost arithmetic"""
    model_name: str
    step: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    cost_inr: float = 0.0
    latency_ms: int = 0
