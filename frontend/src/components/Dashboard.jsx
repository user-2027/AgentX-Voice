import React from 'react'
import InquiryCard from './InquiryCard'
import './Dashboard.css'

const Dashboard = ({ inquiries, metrics }) => {
  const recentInquiries = inquiries.slice(0, 5)

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Dashboard Overview</h2>
        <div className="quick-stats">
          <div className="stat-card">
            <div className="stat-value">{inquiries.length}</div>
            <div className="stat-label">Total Inquiries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{inquiries.filter(i => i.resolved).length}</div>
            <div className="stat-label">Resolved</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{metrics.avgConfidence}%</div>
            <div className="stat-label">Avg Confidence</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{metrics.avgTime}ms</div>
            <div className="stat-label">Avg Response Time</div>
          </div>
        </div>
      </div>

      <div className="recent-inquiries">
        <h3>Recent Inquiries</h3>
        {recentInquiries.length === 0 ? (
          <div className="empty-state">
            <p>No inquiries yet. Submit one from the "New Inquiry" tab!</p>
          </div>
        ) : (
          <div className="inquiry-list">
            {recentInquiries.map(inquiry => (
              <InquiryCard key={inquiry.request_id} inquiry={inquiry} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

