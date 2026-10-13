"""Agent that combines responses from multiple agents."""
from typing import List, Dict, Any
from models import CallCenterRequest, AgentResponse, QueryType, AgentType
from agents.base_agent import BaseAgent


class SynthesisAgent(BaseAgent):
    """Combines responses from multiple agents."""
    
    def __init__(self):
        super().__init__(AgentType.SYNTHESIS, "Synthesis Agent")
    
    async def process(
        self,
        request: CallCenterRequest,
        agent_responses: List[AgentResponse],
        routing_info: Dict[str, Any]
    ) -> AgentResponse:
        """Synthesize responses from multiple agents into a coherent final response."""
        # Get primary agent response (specialized agent)
        primary_response = self._get_primary_response(agent_responses)
        
        # Get supporting context (knowledge base)
        kb_response = self._get_kb_response(agent_responses)
        
        # Combine responses
        synthesized_text = self._synthesize_responses(
            request.inquiry_text,
            primary_response,
            kb_response,
            agent_responses
        )
        
        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(agent_responses)
        
        # Determine if resolved
        resolved = confidence >= 0.7 and primary_response is not None
        
        response = AgentResponse(
            agent_type=self.agent_type,
            query_type=routing_info.get("query_type", QueryType.GENERAL_INQUIRY),
            confidence=confidence,
            response_text=synthesized_text,
            data={
                "primary_data": primary_response.data if primary_response else {},
                "kb_context": kb_response.data if kb_response else {},
                "resolved": resolved
            },
            metadata={
                "agents_involved": [resp.agent_type.value for resp in agent_responses],
                "primary_agent": primary_response.agent_type.value if primary_response else None
            }
        )
        
        return response
    
    def _get_primary_response(self, responses: List[AgentResponse]) -> AgentResponse:
        """Get the primary specialized agent response."""
        # Exclude router, KB, and synthesis agents
        specialized_agents = [
            resp for resp in responses
            if resp.agent_type not in [AgentType.ROUTER, AgentType.KNOWLEDGE_BASE, AgentType.SYNTHESIS]
        ]
        
        if not specialized_agents:
            return None
        
        # Return the one with highest confidence
        return max(specialized_agents, key=lambda r: r.confidence)
    
    def _get_kb_response(self, responses: List[AgentResponse]) -> AgentResponse:
        """Get knowledge base response."""
        for resp in responses:
            if resp.agent_type == AgentType.KNOWLEDGE_BASE:
                return resp
        return None
    
    def _synthesize_responses(
        self,
        inquiry_text: str,
        primary_response: AgentResponse,
        kb_response: AgentResponse,
        all_responses: List[AgentResponse]
    ) -> str:
        """Synthesize multiple responses into one coherent response."""
        if not primary_response:
            if kb_response:
                return f"{kb_response.response_text}\n\nIf you need more specific assistance, please contact our support team."
            return "I apologize, but I couldn't find specific information to answer your inquiry. Please contact our support team at 1-800-XXX-XXXX for assistance."
        
        # Start with primary response
        synthesized = primary_response.response_text
        
        # Add KB context if relevant and not redundant
        if kb_response and self._should_include_kb_context(synthesized, kb_response.response_text):
            # Extract non-redundant info from KB
            kb_additions = self._extract_additional_info(synthesized, kb_response.response_text)
            if kb_additions:
                synthesized += f"\n\nAdditional Information: {kb_additions}"
        
        # Ensure professional tone and completeness
        if not synthesized.endswith(('.', '!', '?')):
            synthesized += "."
        
        return synthesized
    
    def _should_include_kb_context(self, primary_text: str, kb_text: str) -> bool:
        """Determine if KB context should be included."""
        # Include if KB has meaningful additional information
        if len(kb_text) < 20:
            return False
        
        # Check for redundancy
        primary_lower = primary_text.lower()
        kb_lower = kb_text.lower()
        
        # If KB text is mostly covered in primary, skip
        kb_words = set(kb_lower.split())
        primary_words = set(primary_lower.split())
        
        overlap = len(kb_words & primary_words) / len(kb_words) if kb_words else 0
        return overlap < 0.7  # Include if less than 70% overlap
    
    def _extract_additional_info(self, primary_text: str, kb_text: str) -> str:
        """Extract additional non-redundant information from KB."""
        # Simple extraction - take first sentence or key phrases not in primary
        kb_sentences = kb_text.split('.')
        primary_lower = primary_text.lower()
        
        for sentence in kb_sentences:
            sentence_lower = sentence.lower().strip()
            if sentence_lower and len(sentence_lower) > 20:
                # Check if this sentence adds new information
                sentence_words = set(sentence_lower.split())
                primary_words = set(primary_lower.split())
                
                if len(sentence_words - primary_words) > 3:  # Has at least 3 new words
                    return sentence.strip()
        
        return ""
    
    def _calculate_overall_confidence(self, responses: List[AgentResponse]) -> float:
        """Calculate overall confidence from all agent responses."""
        if not responses:
            return 0.0
        
        # Weight primary agent response more heavily
        primary = self._get_primary_response(responses)
        if primary:
            # Average with weight: 70% primary, 30% others
            primary_conf = primary.confidence
            other_confs = [r.confidence for r in responses if r != primary]
            other_avg = sum(other_confs) / len(other_confs) if other_confs else 0.5
            
            return (primary_conf * 0.7) + (other_avg * 0.3)
        
        # If no primary, average all
        return sum(r.confidence for r in responses) / len(responses)

