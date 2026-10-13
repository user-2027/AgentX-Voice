import React from 'react'
import './Metrics.css'

const Metrics = ({ inquiries, metrics }) => {
  const calculateROI = () => {
    if (inquiries.length === 0) return null
    
    const avgTime = inquiries.reduce((sum, i) => sum + i.execution_time_ms, 0) / inquiries.length
    const resolved = inquiries.filter(i => i.resolved).length
    const resolutionRate = (resolved / inquiries.length) * 100
    
    // Based on industry standards
    const baselineAHT = 300000 // 5 minutes in ms
    const ahtReduction = ((baselineAHT - avgTime) / baselineAHT) * 100
    
    return {
      ahtReduction: ahtReduction.toFixed(1),
      resolutionRate: resolutionRate.toFixed(1),
      totalSavings: (inquiries.length * 2.5).toFixed(0) // Estimated $2.50 per automated call
    }
  }

  const roi = calculateROI()
  const queryTypeDistribution = {}
  inquiries.forEach(inq => {
    queryTypeDistribution[inq.query_type] = (queryTypeDistribution[inq.query_type] || 0) + 1
  })

  return (
    <div className="metrics">
      <h2>Performance Metrics & ROI</h2>
      
      <div className="metrics-grid">
        <div className="metric-card primary">
          <div className="metric-icon">⏱</div>
          <div className="metric-content">
            <div className="metric-label">Average Handle Time</div>
            <div className="metric-big-value">{metrics.avgTime}ms</div>
            {roi && (
              <div className="metric-improvement">
                {roi.ahtReduction > 0 ? '↓' : ''} {Math.abs(roi.ahtReduction)}% vs baseline
              </div>
            )}
          </div>
        </div>

        <div className="metric-card primary">
          <div className="metric-icon">✓</div>
          <div className="metric-content">
            <div className="metric-label">First Call Resolution</div>
            <div className="metric-big-value">
              {inquiries.length > 0 
                ? ((inquiries.filter(i => i.resolved).length / inquiries.length) * 100).toFixed(1)
                : 0}%
            </div>
            {roi && (
              <div className="metric-improvement">
                +{((parseFloat(roi.resolutionRate) - 65) / 65 * 100).toFixed(1)}% vs 65% baseline
              </div>
            )}
          </div>
        </div>

        <div className="metric-card primary">
          <div className="metric-icon">%</div>
          <div className="metric-content">
            <div className="metric-label">Average Confidence</div>
            <div className="metric-big-value">{metrics.avgConfidence}%</div>
            <div className="metric-subtext">System accuracy</div>
          </div>
        </div>

        <div className="metric-card primary">
          <div className="metric-icon">$</div>
          <div className="metric-content">
            <div className="metric-label">Estimated Savings</div>
            <div className="metric-big-value">${roi?.totalSavings || '0'}</div>
            <div className="metric-subtext">Based on {inquiries.length} automated calls</div>
          </div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-card">
          <h3>Query Type Distribution</h3>
          <div className="query-distribution">
            {Object.keys(queryTypeDistribution).length === 0 ? (
              <p className="no-data">No data yet</p>
            ) : (
              Object.entries(queryTypeDistribution).map(([type, count]) => (
                <div key={type} className="distribution-item">
                  <div className="distribution-label">
                    {type.replace('_', ' ').toUpperCase()}
                  </div>
                  <div className="distribution-bar">
                    <div 
                      className="distribution-fill"
                      style={{ 
                        width: `${(count / inquiries.length) * 100}%`,
                        backgroundColor: getTypeColor(type)
                      }}
                    >
                      <span className="distribution-value">{count}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="chart-card">
          <h3>Performance Trend</h3>
          <div className="trend-info">
            <div className="trend-item">
              <span className="trend-label">Total Inquiries:</span>
              <span className="trend-value">{inquiries.length}</span>
            </div>
            <div className="trend-item">
              <span className="trend-label">Resolved:</span>
              <span className="trend-value">
                {inquiries.filter(i => i.resolved).length}
              </span>
            </div>
            <div className="trend-item">
              <span className="trend-label">Success Rate:</span>
              <span className="trend-value">
                {inquiries.length > 0
                  ? ((inquiries.filter(i => i.resolved).length / inquiries.length) * 100).toFixed(1)
                  : 0}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const getTypeColor = (type) => {
  const colors = {
    'appointment_status': '#3b82f6',
    'insurance_validation': '#10b981',
    'report_request': '#f59e0b',
    'general_inquiry': '#8b5cf6',
    'unknown': '#6b7280'
  }
  return colors[type] || '#6b7280'
}

export default Metrics

