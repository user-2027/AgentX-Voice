"""Agent package for multi-agent call center system."""
from agents.router_agent import RouterAgent
from agents.appointment_agent import AppointmentAgent
from agents.insurance_agent import InsuranceAgent
from agents.report_agent import ReportAgent
from agents.knowledge_base_agent import KnowledgeBaseAgent
from agents.synthesis_agent import SynthesisAgent

__all__ = [
    "RouterAgent",
    "AppointmentAgent",
    "InsuranceAgent",
    "ReportAgent",
    "KnowledgeBaseAgent",
    "SynthesisAgent"
]

