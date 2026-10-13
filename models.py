"""Data models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class QueryType(str, Enum):
    """Types of customer inquiries."""
    APPOINTMENT_STATUS = "appointment_status"
    INSURANCE_VALIDATION = "insurance_validation"
    REPORT_REQUEST = "report_request"
    GENERAL_INQUIRY = "general_inquiry"
    UNKNOWN = "unknown"


class AgentType(str, Enum):
    """Types of specialized agents."""
    ROUTER = "router"
    APPOINTMENT = "appointment"
    INSURANCE = "insurance"
    REPORT = "report"
    KNOWLEDGE_BASE = "knowledge_base"
    SYNTHESIS = "synthesis"


class CallCenterRequest(BaseModel):
    """Request model for call center inquiry."""
    customer_id: str = Field(..., description="Unique customer identifier")
    inquiry_text: str = Field(..., description="Customer's inquiry text")
    phone_number: Optional[str] = Field(None, description="Customer phone number")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Request timestamp")


class AgentResponse(BaseModel):
    """Response from an individual agent."""
    agent_type: AgentType
    query_type: QueryType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    response_text: str = Field(..., description="Agent's response")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured data extracted")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class CallCenterResponse(BaseModel):
    """Final response to customer inquiry."""
    request_id: str = Field(..., description="Unique request identifier")
    customer_id: str = Field(..., description="Customer identifier")
    query_type: QueryType
    resolved: bool = Field(..., description="Whether inquiry was successfully resolved")
    response_text: str = Field(..., description="Final response to customer")
    agent_responses: List[AgentResponse] = Field(default_factory=list, description="Responses from all agents")
    execution_time_ms: float = Field(..., description="Total execution time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class AppointmentData(BaseModel):
    """Appointment information."""
    appointment_id: Optional[str] = None
    patient_name: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    status: Optional[str] = None
    provider: Optional[str] = None
    location: Optional[str] = None


class InsuranceData(BaseModel):
    """Insurance validation information."""
    member_id: Optional[str] = None
    insurance_provider: Optional[str] = None
    policy_number: Optional[str] = None
    coverage_status: Optional[str] = None
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    is_valid: Optional[bool] = None


class ReportData(BaseModel):
    """Report request information."""
    report_type: Optional[str] = None
    patient_id: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    status: Optional[str] = None
    request_id: Optional[str] = None

