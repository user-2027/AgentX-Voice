"""Agent for knowledge base lookups."""
from typing import Dict, Any, Optional
from models import CallCenterRequest, AgentResponse, QueryType, AgentType
from agents.base_agent import BaseAgent


class KnowledgeBaseAgent(BaseAgent):
    """Provides KB context and FAQs."""
    
    def __init__(self):
        super().__init__(AgentType.KNOWLEDGE_BASE, "Knowledge Base Agent")
        self.kb_data = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base data (mock implementation)."""
        return {
            "faqs": {
                "appointment": [
                    {
                        "question": "How do I cancel my appointment?",
                        "answer": "You can cancel your appointment by calling us at 1-800-XXX-XXXX or through your patient portal. Cancellations must be made at least 24 hours in advance."
                    },
                    {
                        "question": "Can I reschedule my appointment?",
                        "answer": "Yes, you can reschedule your appointment by calling us or using the patient portal. Please try to reschedule at least 24 hours in advance."
                    }
                ],
                "insurance": [
                    {
                        "question": "How do I verify my insurance?",
                        "answer": "You can verify your insurance by providing your member ID. Our system will check your coverage status and eligibility."
                    },
                    {
                        "question": "What insurance providers do you accept?",
                        "answer": "We accept most major insurance providers including BlueCross BlueShield, Aetna, UnitedHealthcare, Cigna, and Medicare."
                    }
                ],
                "reports": [
                    {
                        "question": "How long does it take to get lab results?",
                        "answer": "Lab results are typically available within 24-48 hours. You'll be notified when your results are ready."
                    },
                    {
                        "question": "How can I access my medical records?",
                        "answer": "You can access your medical records through the patient portal or by requesting them through our records department."
                    }
                ]
            },
            "policies": {
                "cancellation": "Appointments must be cancelled at least 24 hours in advance to avoid cancellation fees.",
                "insurance_verification": "Insurance verification is required before all appointments and procedures.",
                "report_request": "Report requests typically take 2-3 business days to process."
            },
            "contact_info": {
                "phone": "1-800-XXX-XXXX",
                "email": "support@healthcare.example.com",
                "hours": "Monday-Friday: 8 AM - 6 PM, Saturday: 9 AM - 2 PM"
            }
        }
    
    async def process(self, request: CallCenterRequest, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process knowledge base lookup."""
        inquiry_text = request.inquiry_text.lower()
        
        # Determine relevant KB section
        query_type = self.extract_query_type(inquiry_text)
        
        # Get relevant KB content
        kb_content = self._get_relevant_content(inquiry_text, query_type)
        
        # Generate response
        response_text = self._generate_response(kb_content, query_type)
        
        confidence = 0.7  # KB agent provides supporting context
        
        response = AgentResponse(
            agent_type=self.agent_type,
            query_type=query_type,
            confidence=confidence,
            response_text=response_text,
            data=kb_content,
            metadata={"source": "knowledge_base"}
        )
        
        self.log_interaction(request, response)
        return response
    
    def _get_relevant_content(self, inquiry_text: str, query_type: QueryType) -> Dict[str, Any]:
        """Get relevant knowledge base content."""
        content = {
            "relevant_faqs": [],
            "policies": [],
            "contact_info": self.kb_data["contact_info"]
        }
        
        # Get FAQs based on query type
        if query_type == QueryType.APPOINTMENT_STATUS:
            content["relevant_faqs"] = self.kb_data["faqs"]["appointment"]
            content["policies"] = [self.kb_data["policies"]["cancellation"]]
        elif query_type == QueryType.INSURANCE_VALIDATION:
            content["relevant_faqs"] = self.kb_data["faqs"]["insurance"]
            content["policies"] = [self.kb_data["policies"]["insurance_verification"]]
        elif query_type == QueryType.REPORT_REQUEST:
            content["relevant_faqs"] = self.kb_data["faqs"]["reports"]
            content["policies"] = [self.kb_data["policies"]["report_request"]]
        
        return content
    
    def _generate_response(self, kb_content: Dict[str, Any], query_type: QueryType) -> str:
        """Generate response from knowledge base content."""
        response_parts = []
        
        # Add relevant FAQs
        if kb_content.get("relevant_faqs"):
            response_parts.append("Here's some helpful information:")
            for faq in kb_content["relevant_faqs"][:2]:  # Limit to 2 most relevant
                response_parts.append(f"• {faq['answer']}")
        
        # Add policies
        if kb_content.get("policies"):
            response_parts.append(f"\nPolicy: {kb_content['policies'][0]}")
        
        # Add contact info if needed
        if not response_parts:
            contact = kb_content.get("contact_info", {})
            response_parts.append(f"For assistance, please contact us at {contact.get('phone', '1-800-XXX-XXXX')}.")
        
        return "\n".join(response_parts) if response_parts else "I don't have specific information about this topic in our knowledge base."

