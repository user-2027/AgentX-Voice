import React from 'react'
import './InquiryCard.css'

const InquiryCard = ({ inquiry }) => {
  const queryTypeColors = {
    'appointment_status': '#3b82f6',
    'insurance_validation': '#10b981',
    'report_request': '#f59e0b',
    'general_inquiry': '#8b5cf6',
    'unknown': '#6b7280'
  }

  const getAgentIcons = (agents) => {
    const icons = {
      'router': '🔄',
      'appointment': '📅',
      'insurance': '🛡️',
      'report': '📄',
      'knowledge_base': '📚',
      'synthesis': '🧠'
    }
    return agents?.map(agent => icons[agent] || '🤖').join(' ') || ''
  }

  return (
    <div className="inquiry-card">
      <div className="inquiry-header">
        <div className="inquiry-type" style={{ 
          backgroundColor: queryTypeColors[inquiry.query_type] || '#6b7280' 
        }}>
          {inquiry.query_type.replace('_', ' ').toUpperCase()}
        </div>
        <div className={`inquiry-status ${inquiry.resolved ? 'resolved' : 'unresolved'}`}>
          {inquiry.resolved ? '✅ Resolved' : '⏳ Processing'}
        </div>
      </div>
      
      <div className="inquiry-content">
        <div className="inquiry-text">
          <strong>Inquiry:</strong> {inquiry.inquiry_text || 'N/A'}
        </div>
        <div className="inquiry-response">
          <strong>Response:</strong> {inquiry.response_text || 'Processing...'}
        </div>
      </div>

      <div className="inquiry-metrics">
        <div className="metric">
          <span className="metric-label">Confidence:</span>
          <span className="metric-value">{(inquiry.confidence * 100 || 0).toFixed(1)}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Time:</span>
          <span className="metric-value">{inquiry.execution_time_ms?.toFixed(0) || 0}ms</span>
        </div>
        <div className="metric">
          <span className="metric-label">Agents:</span>
          <span className="metric-value">{getAgentIcons(inquiry.agents_invoked)}</span>
        </div>
      </div>
    </div>
  )
}

export default InquiryCard

