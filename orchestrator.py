"""Orchestrator for handling inquiries through agents."""
import time
import uuid
from typing import Dict, Any, List
from datetime import datetime
from models import (
    CallCenterRequest,
    CallCenterResponse,
    AgentResponse,
    AgentType,
    QueryType
)
from agents import (
    RouterAgent,
    AppointmentAgent,
    InsuranceAgent,
    ReportAgent,
    KnowledgeBaseAgent,
    SynthesisAgent
)


class MultiAgentOrchestrator:
    """Coordinates agents to handle inquiries."""
    
    def __init__(self):
        self.router = RouterAgent()
        self.appointment_agent = AppointmentAgent()
        self.insurance_agent = InsuranceAgent()
        self.report_agent = ReportAgent()
        self.kb_agent = KnowledgeBaseAgent()
        self.synthesis_agent = SynthesisAgent()
        
        # Agent registry
        self.agent_registry: Dict[AgentType, Any] = {
            AgentType.APPOINTMENT: self.appointment_agent,
            AgentType.INSURANCE: self.insurance_agent,
            AgentType.REPORT: self.report_agent,
            AgentType.KNOWLEDGE_BASE: self.kb_agent,
            AgentType.SYNTHESIS: self.synthesis_agent
        }
    
    async def process_request(self, request: CallCenterRequest) -> CallCenterResponse:
        """Process customer request through agents."""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Step 1: Route the inquiry
        routing_info = await self.router.route(request)
        query_type = routing_info["query_type"]
        agents_to_invoke = routing_info["agents_to_invoke"]
        
        # Step 2: Invoke specialized agents in parallel (simulated)
        agent_responses: List[AgentResponse] = []
        
        # Invoke knowledge base agent first for context
        if AgentType.KNOWLEDGE_BASE in agents_to_invoke:
            kb_response = await self.kb_agent.process(request)
            agent_responses.append(kb_response)
        
        # Invoke specialized agent
        specialized_agent_type = None
        for agent_type in agents_to_invoke:
            if agent_type in [AgentType.APPOINTMENT, AgentType.INSURANCE, AgentType.REPORT]:
                specialized_agent_type = agent_type
                agent = self.agent_registry[agent_type]
                response = await agent.process(request, context=routing_info)
                agent_responses.append(response)
                break
        
        # Step 3: Synthesize responses
        if AgentType.SYNTHESIS in agents_to_invoke:
            synthesis_response = await self.synthesis_agent.process(
                request,
                agent_responses,
                routing_info
            )
            agent_responses.append(synthesis_response)
            final_response = synthesis_response.response_text
            resolved = synthesis_response.data.get("resolved", False) if synthesis_response.data else False
            confidence = synthesis_response.confidence
        else:
            # Fallback if synthesis not invoked
            if agent_responses:
                primary = agent_responses[0]
                final_response = primary.response_text
                resolved = primary.confidence >= 0.7
                confidence = primary.confidence
            else:
                final_response = "I apologize, but I couldn't process your request. Please contact support."
                resolved = False
                confidence = 0.0
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Create final response
        return CallCenterResponse(
            request_id=request_id,
            customer_id=request.customer_id,
            query_type=query_type,
            resolved=resolved,
            response_text=final_response,
            agent_responses=agent_responses,
            execution_time_ms=execution_time_ms,
            timestamp=datetime.now(),
            metadata={
                "routing_confidence": routing_info["confidence"],
                "routing_reasoning": routing_info["reasoning"],
                "agents_invoked": [agent.value for agent in agents_to_invoke]
            }
        )
    
    async def process_batch(self, requests: List[CallCenterRequest]) -> List[CallCenterResponse]:
        """Process multiple requests in batch."""
        responses = []
        for request in requests:
            response = await self.process_request(request)
            responses.append(response)
        return responses

