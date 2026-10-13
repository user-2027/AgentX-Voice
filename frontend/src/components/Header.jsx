import React from 'react'
import './Header.css'

const Header = ({ systemStatus }) => {
  const statusColors = {
    'operational': '#10b981',
    'initializing': '#f59e0b',
    'offline': '#ef4444',
    'checking...': '#6b7280'
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <h1>Call Center Resolution System</h1>
          <p className="subtitle">Intelligent Multi-Agent Platform</p>
        </div>
        <div className="status-section">
          <div className="status-indicator">
            <span 
              className="status-dot" 
              style={{ backgroundColor: statusColors[systemStatus] }}
            ></span>
            <span className="status-text">System: {systemStatus}</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

