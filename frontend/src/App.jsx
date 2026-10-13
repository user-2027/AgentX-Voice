import React, { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import InquiryForm from './components/InquiryForm'
import AgentView from './components/AgentView'
import Metrics from './components/Metrics'
import Header from './components/Header'
import './App.css'

// Detect API URL - works in Codespaces and locally
const getApiUrl = () => {
  // In Codespaces, use the forwarded port URL
  if (window.location.hostname.includes('github.dev') || window.location.hostname.includes('preview.app')) {
    // Extract base URL and use port 8000
    const baseUrl = window.location.origin.replace(':3000', ':8000')
    return baseUrl
  }
  // Local development or explicit env var
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

const API_BASE_URL = getApiUrl()

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [inquiries, setInquiries] = useState([])
  const [metrics, setMetrics] = useState({
    totalInquiries: 0,
    resolved: 0,
    avgConfidence: 0,
    avgTime: 0
  })
  const [systemStatus, setSystemStatus] = useState('checking...')

  useEffect(() => {
    checkHealth()
    loadStats()
    const interval = setInterval(loadStats, 5000)
    return () => clearInterval(interval)
  }, [])

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      const data = await response.json()
      setSystemStatus(data.orchestrator_ready ? 'operational' : 'initializing')
    } catch (error) {
      setSystemStatus('offline')
      console.error('Health check failed:', error)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/stats`)
      const data = await response.json()
      setMetrics({
        totalInquiries: inquiries.length,
        resolved: inquiries.filter(i => i.resolved).length,
        avgConfidence: inquiries.length > 0 
          ? (inquiries.reduce((sum, i) => sum + (i.confidence || 0), 0) / inquiries.length * 100).toFixed(1)
          : 0,
        avgTime: inquiries.length > 0
          ? (inquiries.reduce((sum, i) => sum + i.execution_time_ms, 0) / inquiries.length).toFixed(0)
          : 0
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const handleNewInquiry = (inquiry) => {
    setInquiries(prev => [inquiry, ...prev])
  }

  return (
    <div className="app">
      <Header systemStatus={systemStatus} />
      
      <div className="container">
        <nav className="tabs">
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={activeTab === 'inquiry' ? 'active' : ''}
            onClick={() => setActiveTab('inquiry')}
          >
            New Inquiry
          </button>
          <button 
            className={activeTab === 'agents' ? 'active' : ''}
            onClick={() => setActiveTab('agents')}
          >
            Agent View
          </button>
          <button 
            className={activeTab === 'metrics' ? 'active' : ''}
            onClick={() => setActiveTab('metrics')}
          >
            Metrics
          </button>
        </nav>

        <main className="main-content">
          {activeTab === 'dashboard' && (
            <Dashboard inquiries={inquiries} metrics={metrics} />
          )}
          {activeTab === 'inquiry' && (
            <InquiryForm onInquirySubmitted={handleNewInquiry} apiBaseUrl={API_BASE_URL} />
          )}
          {activeTab === 'agents' && (
            <AgentView inquiries={inquiries} />
          )}
          {activeTab === 'metrics' && (
            <Metrics inquiries={inquiries} metrics={metrics} />
          )}
        </main>
      </div>
    </div>
  )
}

export default App

