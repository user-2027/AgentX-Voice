import React from 'react'
import './AgentView.css'

const AgentView = ({ inquiries }) => {
  const getAgentStats = () => {
    const agentStats = {
      router: { count: 0, avgConfidence: 0 },
      appointment: { count: 0, avgConfidence: 0 },
      insurance: { count: 0, avgConfidence: 0 },
      report: { count: 0, avgConfidence: 0 },
      knowledge_base: { count: 0, avgConfidence: 0 },
      synthesis: { count: 0, avgConfidence: 0 }
    }

    inquiries.forEach(inquiry => {
      inquiry.agent_responses?.forEach(response => {
        const agentType = response.agent_type
        if (agentStats[agentType]) {
          agentStats[agentType].count++
          agentStats[agentType].avgConfidence += response.confidence
        }
      })
    })

    Object.keys(agentStats).forEach(agent => {
      if (agentStats[agent].count > 0) {
        agentStats[agent].avgConfidence = 
          (agentStats[agent].avgConfidence / agentStats[agent].count * 100).toFixed(1)
      }
    })

    return agentStats
  }

  const agentStats = getAgentStats()

  const agents = [
    { id: 'router', name: 'Router Agent', icon: '🔄', desc: 'Routes inquiries' },
    { id: 'appointment', name: 'Appointment Agent', icon: '📅', desc: 'Handles appointments' },
    { id: 'insurance', name: 'Insurance Agent', icon: '🛡️', desc: 'Validates insurance' },
    { id: 'report', name: 'Report Agent', icon: '📄', desc: 'Manages reports' },
    { id: 'knowledge_base', name: 'Knowledge Base', icon: '📚', desc: 'Provides context' },
    { id: 'synthesis', name: 'Synthesis Agent', icon: '🧠', desc: 'Combines responses' }
  ]

  return (
    <div className="agent-view">
      <h2>Multi-Agent System Overview</h2>
      
      <div className="agents-grid">
        {agents.map(agent => {
          const stats = agentStats[agent.id]
          return (
            <div key={agent.id} className="agent-card">
              <div className="agent-header">
                <span className="agent-icon">{agent.icon}</span>
                <div>
                  <h3>{agent.name}</h3>
                  <p className="agent-desc">{agent.desc}</p>
                </div>
              </div>
              <div className="agent-stats">
                <div className="stat">
                  <span className="stat-label">Invocations:</span>
                  <span className="stat-value">{stats.count}</span>
                </div>
                {stats.count > 0 && (
                  <div className="stat">
                    <span className="stat-label">Avg Confidence:</span>
                    <span className="stat-value">{stats.avgConfidence}%</span>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {inquiries.length === 0 && (
        <div className="empty-state">
          <p>No agent activity yet. Submit inquiries to see agents in action!</p>
        </div>
      )}
    </div>
  )
}

export default AgentView

