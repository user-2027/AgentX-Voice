"""Router for categorizing and routing inquiries."""
from typing import Dict, Any, Optional
from models import CallCenterRequest, AgentResponse, QueryType, AgentType


class RouterAgent:
    """Routes inquiries to appropriate agents."""
    
    def __init__(self):
        self.name = "Router Agent"
        self.agent_type = AgentType.ROUTER
    
    async def route(self, request: CallCenterRequest) -> Dict[str, Any]:
        """
        Route the inquiry to appropriate agent(s).
        
        Args:
            request: The customer request
            
        Returns:
            Routing decision with query type and recommended agents
        """
        inquiry_lower = request.inquiry_text.lower()
        
        # Extract query type
        query_type = self._classify_query(inquiry_lower)
        
        # Determine which agents to involve
        agents_to_invoke = self._determine_agents(query_type, inquiry_lower)
        
        # Calculate routing confidence
        confidence = self._calculate_routing_confidence(inquiry_lower, query_type)
        
        return {
            "query_type": query_type,
            "agents_to_invoke": agents_to_invoke,
            "confidence": confidence,
            "reasoning": self._generate_reasoning(query_type, inquiry_lower)
        }
    
    def _classify_query(self, inquiry_text: str) -> QueryType:
        """Classify the query type."""
        # Appointment keywords
        appointment_keywords = [
            "appointment", "schedule", "booking", "visit", "slot", 
            "date", "time", "when", "cancel", "reschedule", "confirm"
        ]
        
        # Insurance keywords
        insurance_keywords = [
            "insurance", "coverage", "policy", "member id", "member number",
            "validate", "verification", "eligibility", "benefits"
        ]
        
        # Report keywords
        report_keywords = [
            "report", "result", "document", "statement", "record", 
            "lab", "test", "imaging", "billing", "history", "summary"
        ]
        
        appointment_score = sum(1 for kw in appointment_keywords if kw in inquiry_text)
        insurance_score = sum(1 for kw in insurance_keywords if kw in inquiry_text)
        report_score = sum(1 for kw in report_keywords if kw in inquiry_text)
        
        scores = {
            QueryType.APPOINTMENT_STATUS: appointment_score,
            QueryType.INSURANCE_VALIDATION: insurance_score,
            QueryType.REPORT_REQUEST: report_score,
            QueryType.GENERAL_INQUIRY: 0
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return QueryType.GENERAL_INQUIRY
        
        return max(scores, key=scores.get)
    
    def _determine_agents(self, query_type: QueryType, inquiry_text: str) -> list:
        """Determine which agents should handle this query."""
        agents = []
        
        # Always include knowledge base agent for context
        agents.append(AgentType.KNOWLEDGE_BASE)
        
        # Route to specialized agent based on query type
        if query_type == QueryType.APPOINTMENT_STATUS:
            agents.append(AgentType.APPOINTMENT)
        elif query_type == QueryType.INSURANCE_VALIDATION:
            agents.append(AgentType.INSURANCE)
        elif query_type == QueryType.REPORT_REQUEST:
            agents.append(AgentType.REPORT)
        
        # Always include synthesis agent to combine responses
        agents.append(AgentType.SYNTHESIS)
        
        return agents
    
    def _calculate_routing_confidence(self, inquiry_text: str, query_type: QueryType) -> float:
        """Calculate confidence in routing decision."""
        if query_type == QueryType.GENERAL_INQUIRY:
            return 0.5
        
        # Higher confidence if query is specific and clear
        specific_keywords = [
            "appointment", "insurance", "report", "status", "validate",
            "request", "check", "verify", "get", "find"
        ]
        
        keyword_count = sum(1 for kw in specific_keywords if kw in inquiry_text)
        confidence = min(0.95, 0.6 + (keyword_count * 0.1))
        
        return confidence
    
    def _generate_reasoning(self, query_type: QueryType, inquiry_text: str) -> str:
        """Generate reasoning for routing decision."""
        reasons = {
            QueryType.APPOINTMENT_STATUS: "Query contains appointment-related keywords",
            QueryType.INSURANCE_VALIDATION: "Query contains insurance-related keywords",
            QueryType.REPORT_REQUEST: "Query contains report/document-related keywords",
            QueryType.GENERAL_INQUIRY: "Query does not match specific categories"
        }
        return reasons.get(query_type, "Unknown query type")

