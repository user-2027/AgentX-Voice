"""Agent for insurance validation."""
from typing import Dict, Any, Optional
import re
from models import CallCenterRequest, AgentResponse, QueryType, AgentType
from agents.base_agent import BaseAgent
from mock_data import MockDataGenerator


class InsuranceAgent(BaseAgent):
    """Handles insurance validation."""
    
    def __init__(self):
        super().__init__(AgentType.INSURANCE, "Insurance Agent")
        self.mock_data = MockDataGenerator()
    
    async def process(self, request: CallCenterRequest, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process insurance-related inquiries."""
        inquiry_text = request.inquiry_text.lower()
        customer_id = request.customer_id
        
        # Extract member ID if mentioned
        member_id = self._extract_member_id(inquiry_text)
        
        # Validate insurance
        validation_result = self.mock_data.validate_insurance(customer_id, member_id)
        
        # Get full insurance data
        insurance_data = {}
        if member_id:
            insurance_data = self.mock_data.get_insurance_by_member_id(member_id) or {}
        else:
            insurance_data = self.mock_data.get_insurance_by_customer(customer_id) or {}
        
        # Generate response
        response_text = self._generate_response(inquiry_text, validation_result, insurance_data)
        
        # Calculate confidence
        confidence = self.calculate_confidence(inquiry_text, insurance_data)
        
        response = AgentResponse(
            agent_type=self.agent_type,
            query_type=QueryType.INSURANCE_VALIDATION,
            confidence=confidence,
            response_text=response_text,
            data={**insurance_data, **validation_result},
            metadata={"customer_id": customer_id, "member_id": member_id or insurance_data.get("member_id")}
        )
        
        self.log_interaction(request, response)
        return response
    
    def _extract_member_id(self, text: str) -> Optional[str]:
        """Extract member ID from text."""
        # Pattern: INS-XXXXX or member id XXXX
        patterns = [
            r'ins-?\s*(\d+)',
            r'member\s+(?:id|number|#)\s*:?\s*(\w+)',
            r'member\s+(\w+)',
            r'policy\s+#?\s*:?\s*(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"INS-{match.group(1)}" if not match.group(1).startswith("INS") else match.group(1)
        
        return None
    
    def _generate_response(self, inquiry_text: str, validation_result: Dict[str, Any], insurance_data: Dict[str, Any]) -> str:
        """Generate natural language response."""
        if not insurance_data or not validation_result.get("valid"):
            reason = validation_result.get("reason", "Insurance information not found")
            return f"I couldn't validate your insurance coverage. {reason}. Please provide your member ID or contact our insurance department for assistance."
        
        member_id = insurance_data.get("member_id", "N/A")
        provider = insurance_data.get("insurance_provider", "N/A")
        status = insurance_data.get("coverage_status", "unknown")
        expiry = insurance_data.get("expiry_date", "N/A")
        policy = insurance_data.get("policy_number", "N/A")
        
        if "validate" in inquiry_text or "check" in inquiry_text:
            if validation_result["valid"]:
                return f"Your insurance is active and valid. Member ID: {member_id}, Provider: {provider}, Policy: {policy}, Status: {status.title()}, Valid until: {expiry}."
            else:
                return f"Your insurance coverage has expired. Member ID: {member_id}, Provider: {provider}, Expired on: {expiry}. Please contact your insurance provider to renew coverage."
        elif "coverage" in inquiry_text or "benefits" in inquiry_text:
            return f"Your insurance coverage details: Provider: {provider}, Member ID: {member_id}, Status: {status.title()}, Valid until: {expiry}."
        else:
            return f"Insurance Information: Member ID: {member_id}, Provider: {provider}, Policy: {policy}, Coverage Status: {status.title()}, Valid until: {expiry}."
    
    def _get_required_fields(self) -> list:
        """Get required fields for insurance data."""
        return ["member_id", "insurance_provider", "coverage_status"]

