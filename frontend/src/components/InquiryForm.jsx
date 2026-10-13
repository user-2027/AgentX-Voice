import React, { useState } from 'react'
import axios from 'axios'
import './InquiryForm.css'

const InquiryForm = ({ onInquirySubmitted, apiBaseUrl }) => {
  const [formData, setFormData] = useState({
    customer_id: 'CUST-001',
    inquiry_text: '',
    phone_number: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [response, setResponse] = useState(null)

  const exampleInquiries = [
    "I want to check the status of my appointment",
    "Can you verify my insurance coverage?",
    "I need my lab results from last week",
    "What's the status of appointment APT-001?",
    "Is my insurance still active?",
    "I want to cancel my appointment"
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await axios.post(`${apiBaseUrl}/api/v1/inquiry`, formData)
      setResponse(res.data)
      
      // Get confidence from synthesis agent
      const synthesisAgent = res.data.agent_responses?.find(
        r => r.agent_type === 'synthesis'
      )
      const inquiryWithConfidence = {
        ...res.data,
        confidence: synthesisAgent?.confidence || 0,
        agents_invoked: res.data.metadata?.agents_invoked || [],
        inquiry_text: formData.inquiry_text
      }
      
      onInquirySubmitted(inquiryWithConfidence)
      
      // Reset form
      setFormData(prev => ({ ...prev, inquiry_text: '' }))
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process inquiry')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleExampleClick = (example) => {
    setFormData(prev => ({ ...prev, inquiry_text: example }))
  }

  return (
    <div className="inquiry-form">
      <h2>Submit New Inquiry</h2>
      
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="customer_id">Customer ID</label>
          <select
            id="customer_id"
            value={formData.customer_id}
            onChange={(e) => setFormData(prev => ({ ...prev, customer_id: e.target.value }))}
            required
          >
            <option value="CUST-001">CUST-001</option>
            <option value="CUST-002">CUST-002</option>
            <option value="CUST-003">CUST-003</option>
            <option value="CUST-004">CUST-004</option>
            <option value="CUST-005">CUST-005</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="inquiry_text">Inquiry Text *</label>
          <textarea
            id="inquiry_text"
            value={formData.inquiry_text}
            onChange={(e) => setFormData(prev => ({ ...prev, inquiry_text: e.target.value }))}
            placeholder="Enter your inquiry here... (e.g., 'I want to check my appointment status')"
            required
            rows="4"
          />
        </div>

        <div className="form-group">
          <label htmlFor="phone_number">Phone Number (Optional)</label>
          <input
            type="tel"
            id="phone_number"
            value={formData.phone_number}
            onChange={(e) => setFormData(prev => ({ ...prev, phone_number: e.target.value }))}
            placeholder="555-1234"
          />
        </div>

        <div className="example-inquiries">
          <p className="example-label">Example Inquiries:</p>
          <div className="example-buttons">
            {exampleInquiries.map((example, idx) => (
              <button
                key={idx}
                type="button"
                className="example-btn"
                onClick={() => handleExampleClick(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Processing...' : 'Submit Inquiry'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {response && (
        <div className="response-preview">
          <h3>Response Generated</h3>
          <div className="response-content">
            <p><strong>Query Type:</strong> {response.query_type.replace('_', ' ')}</p>
            <p><strong>Resolved:</strong> {response.resolved ? 'Yes' : 'No'}</p>
            <p><strong>Response Time:</strong> {response.execution_time_ms.toFixed(0)}ms</p>
            <div className="response-text">
              <strong>Response:</strong>
              <p>{response.response_text}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InquiryForm

