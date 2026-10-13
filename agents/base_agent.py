"""Base agent implementation."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from models import CallCenterRequest, AgentResponse, QueryType, AgentType


class BaseAgent(ABC):
    """Base class for agents."""
    
    def __init__(self, agent_type: AgentType, name: str):
        self.agent_type = agent_type
        self.name = name
        self.history: list = []
    
    @abstractmethod
    async def process(self, request: CallCenterRequest, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process request and return response."""
        pass
    
    def extract_query_type(self, inquiry_text: str) -> QueryType:
        """Extract query type from text."""
        inquiry_lower = inquiry_text.lower()
        
        if any(keyword in inquiry_lower for keyword in ["appointment", "schedule", "booking", "visit"]):
            return QueryType.APPOINTMENT_STATUS
        elif any(keyword in inquiry_lower for keyword in ["insurance", "coverage", "policy", "member id"]):
            return QueryType.INSURANCE_VALIDATION
        elif any(keyword in inquiry_lower for keyword in ["report", "result", "document", "statement", "record"]):
            return QueryType.REPORT_REQUEST
        else:
            return QueryType.GENERAL_INQUIRY
    
    def calculate_confidence(self, inquiry_text: str, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence based on data."""
        if not extracted_data:
            return 0.3
        
        required_fields = self._get_required_fields()
        if not required_fields:
            return 0.8
        
        filled_fields = sum(1 for field in required_fields if extracted_data.get(field))
        confidence = min(0.9, 0.5 + (filled_fields / len(required_fields)) * 0.4)
        return confidence
    
    def _get_required_fields(self) -> list:
        """Override in subclasses."""
        return []
    
    def log_interaction(self, request: CallCenterRequest, response: AgentResponse):
        """Log interaction."""
        self.history.append({
            "timestamp": time.time(),
            "request": request.dict(),
            "response": response.dict()
        })

