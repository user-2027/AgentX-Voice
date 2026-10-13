"""Agent for report requests."""
from typing import Dict, Any, Optional
import re
from models import CallCenterRequest, AgentResponse, QueryType, AgentType
from agents.base_agent import BaseAgent
from mock_data import MockDataGenerator


class ReportAgent(BaseAgent):
    """Handles report requests."""
    
    def __init__(self):
        super().__init__(AgentType.REPORT, "Report Agent")
        self.mock_data = MockDataGenerator()
        self.report_types = [
            "lab_results", "imaging_results", "billing_statement",
            "medical_history", "prescription_history", "visit_summary"
        ]
    
    async def process(self, request: CallCenterRequest, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process report-related inquiries."""
        inquiry_text = request.inquiry_text.lower()
        customer_id = request.customer_id
        
        # Extract report type
        report_type = self._extract_report_type(inquiry_text)
        
        # Determine action
        action = self._determine_action(inquiry_text)
        
        # Process report request
        if action == "request":
            report_data = self.mock_data.request_report(customer_id, report_type)
        else:
            # Check status or retrieve
            report_data = {
                "report_type": report_type,
                "status": "available" if action == "retrieve" else "processing",
                "customer_id": customer_id
            }
        
        # Generate response
        response_text = self._generate_response(action, inquiry_text, report_data, report_type)
        
        # Calculate confidence
        confidence = self.calculate_confidence(inquiry_text, report_data)
        
        response = AgentResponse(
            agent_type=self.agent_type,
            query_type=QueryType.REPORT_REQUEST,
            confidence=confidence,
            response_text=response_text,
            data=report_data,
            metadata={"action": action, "customer_id": customer_id, "report_type": report_type}
        )
        
        self.log_interaction(request, response)
        return response
    
    def _extract_report_type(self, text: str) -> str:
        """Extract report type from text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["lab", "test result", "blood test", "lab work"]):
            return "lab_results"
        elif any(word in text_lower for word in ["imaging", "x-ray", "scan", "mri", "ct scan"]):
            return "imaging_results"
        elif any(word in text_lower for word in ["billing", "bill", "statement", "invoice"]):
            return "billing_statement"
        elif any(word in text_lower for word in ["medical history", "history", "medical record"]):
            return "medical_history"
        elif any(word in text_lower for word in ["prescription", "medication", "meds"]):
            return "prescription_history"
        elif any(word in text_lower for word in ["visit summary", "visit", "summary"]):
            return "visit_summary"
        else:
            return "general_report"
    
    def _determine_action(self, text: str) -> str:
        """Determine what action the customer wants."""
        if any(word in text for word in ["request", "get", "need", "want", "send"]):
            return "request"
        elif any(word in text for word in ["status", "where", "when", "ready"]):
            return "check_status"
        elif any(word in text for word in ["download", "retrieve", "access", "view"]):
            return "retrieve"
        else:
            return "request"
    
    def _generate_response(self, action: str, inquiry_text: str, report_data: Dict[str, Any], report_type: str) -> str:
        """Generate natural language response."""
        report_type_display = report_type.replace("_", " ").title()
        
        if action == "request":
            report_id = report_data.get("report_id", "PENDING")
            estimated_date = report_data.get("estimated_completion", "2-3 business days")
            return f"I've submitted your request for {report_type_display}. Request ID: {report_id}. Your report will be ready within {estimated_date}. You'll receive a notification when it's available."
        elif action == "check_status":
            status = report_data.get("status", "unknown")
            return f"The status of your {report_type_display} request is: {status.title()}. For more details, please contact our records department."
        elif action == "retrieve":
            return f"Your {report_type_display} is available. Please log in to your patient portal or contact us to receive it via secure email."
        else:
            return f"I can help you with {report_type_display}. Would you like to request a new report, check the status of an existing request, or retrieve an available report?"
    
    def _get_required_fields(self) -> list:
        """Get required fields for report data."""
        return ["report_type", "status"]

