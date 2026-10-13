"""Agent for appointment inquiries."""
from typing import Dict, Any, Optional
import re
from datetime import datetime
from models import CallCenterRequest, AgentResponse, QueryType, AgentType
from agents.base_agent import BaseAgent
from mock_data import MockDataGenerator


class AppointmentAgent(BaseAgent):
    """Handles appointment-related queries."""
    
    def __init__(self):
        super().__init__(AgentType.APPOINTMENT, "Appointment Agent")
        self.mock_data = MockDataGenerator()
    
    async def process(self, request: CallCenterRequest, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process appointment inquiry."""
        inquiry_text = request.inquiry_text.lower()
        customer_id = request.customer_id
        
        # Extract appointment ID if mentioned
        appointment_id = self._extract_appointment_id(inquiry_text)
        
        # Determine action type
        action = self._determine_action(inquiry_text)
        
        # Get appointment data
        appointment_data = {}
        if appointment_id:
            apt = self.mock_data.get_appointment_by_id(appointment_id)
            if apt:
                appointment_data = apt
        else:
            # Get customer's appointments
            appointments = self.mock_data.get_appointment_by_customer(customer_id)
            if appointments:
                appointment_data = appointments[0] if len(appointments) == 1 else {"all_appointments": appointments}
        
        # Generate response
        response_text = self._generate_response(action, inquiry_text, appointment_data)
        
        # Calculate confidence
        confidence = self.calculate_confidence(inquiry_text, appointment_data)
        
        response = AgentResponse(
            agent_type=self.agent_type,
            query_type=QueryType.APPOINTMENT_STATUS,
            confidence=confidence,
            response_text=response_text,
            data=appointment_data,
            metadata={"action": action, "customer_id": customer_id}
        )
        
        self.log_interaction(request, response)
        return response
    
    def _extract_appointment_id(self, text: str) -> Optional[str]:
        """Extract appointment ID from text."""
        # Pattern: APT-XXX or appointment XXX
        patterns = [
            r'apt-?\s*(\d+)',
            r'appointment\s+(\d+)',
            r'appt\s*#?\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                num = match.group(1)
                return f"APT-{num.zfill(3)}"
        
        return None
    
    def _determine_action(self, text: str) -> str:
        """Determine what action the customer wants."""
        if any(word in text for word in ["status", "check", "when", "time", "date"]):
            return "check_status"
        elif any(word in text for word in ["cancel", "remove", "delete"]):
            return "cancel"
        elif any(word in text for word in ["reschedule", "change", "modify", "move"]):
            return "reschedule"
        elif any(word in text for word in ["confirm", "verify"]):
            return "confirm"
        else:
            return "check_status"
    
    def _generate_response(self, action: str, inquiry_text: str, appointment_data: Dict[str, Any]) -> str:
        """Generate natural language response."""
        if not appointment_data or (not appointment_data.get("appointment_id") and not appointment_data.get("all_appointments")):
            return "I couldn't find any appointment records for you. Please contact our scheduling department at 1-800-XXX-XXXX for assistance."
        
        if "all_appointments" in appointment_data:
            appointments = appointment_data["all_appointments"]
            response = f"I found {len(appointments)} appointment(s) for you:\n"
            for apt in appointments:
                response += f"- Appointment {apt['appointment_id']}: {apt['appointment_date']} at {apt['appointment_time']} with {apt['provider']} ({apt['status']})\n"
            return response
        
        apt_id = appointment_data.get("appointment_id", "N/A")
        date = appointment_data.get("appointment_date", "N/A")
        time = appointment_data.get("appointment_time", "N/A")
        status = appointment_data.get("status", "unknown")
        provider = appointment_data.get("provider", "N/A")
        location = appointment_data.get("location", "N/A")
        
        if action == "check_status":
            return f"Your appointment {apt_id} is scheduled for {date} at {time} with {provider} at {location}. Current status: {status.title()}."
        elif action == "cancel":
            return f"To cancel your appointment {apt_id} on {date}, please confirm and I'll process the cancellation."
        elif action == "reschedule":
            return f"To reschedule your appointment {apt_id} on {date} at {time}, please let me know your preferred new date and time."
        elif action == "confirm":
            return f"Confirmed! Your appointment {apt_id} on {date} at {time} with {provider} at {location} is {status}."
        else:
            return f"Your appointment information: {apt_id} on {date} at {time} with {provider}. Status: {status.title()}."
    
    def _get_required_fields(self) -> list:
        """Get required fields for appointment data."""
        return ["appointment_id", "appointment_date", "status"]

