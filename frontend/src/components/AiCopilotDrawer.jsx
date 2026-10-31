import { useState, useRef, useEffect } from 'react'
import { Sparkles, Send, X, Volume2, VolumeX, Bot, User, Copy, Check, MessageSquare } from 'lucide-react'
import api, { errorMessage } from '../api'

const QUICK_CHIPS = [
  '💊 My medication schedule',
  '📅 When is my next appointment?',
  '📋 Missing diagnostic reports?',
  '🚨 Emergency health card',
  '🤝 Who are my caregivers?',
]

export default function AiCopilotDrawer({ openEmergencyModal }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'Hello! I am your CareBridge AI Health Assistant. How can I help coordinate your care plan, appointments, or prescriptions today?',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [speakingIndex, setSpeakingIndex] = useState(null)
  const [copiedIndex, setCopiedIndex] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isOpen])

  // Listen for global trigger events
  useEffect(() => {
    function handleOpenCopilot() {
      setIsOpen(true)
    }
    window.addEventListener('open-copilot-drawer', handleOpenCopilot)
    return () => window.removeEventListener('open-copilot-drawer', handleOpenCopilot)
  }, [])

  // Stop speech when drawer closes
  useEffect(() => {
    if (!isOpen && window.speechSynthesis) {
      window.speechSynthesis.cancel()
      setSpeakingIndex(null)
    }
  }, [isOpen])

  function handleSpeech(text, index) {
    if (!window.speechSynthesis) return
    if (speakingIndex === index) {
      window.speechSynthesis.cancel()
      setSpeakingIndex(null)
      return
    }

    window.speechSynthesis.cancel()
    const cleanText = text.replace(/[*#•]/g, '').trim()
    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.rate = 0.95
    utterance.pitch = 1.0
    utterance.onend = () => setSpeakingIndex(null)
    utterance.onerror = () => setSpeakingIndex(null)
    setSpeakingIndex(index)
    window.speechSynthesis.speak(utterance)
  }

  function handleCopy(text, index) {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(index)
      setTimeout(() => setCopiedIndex(null), 2000)
    })
  }

  async function handleSend(textToSend) {
    const query = (textToSend || input).trim()
    if (!query || loading) return

    if (query.includes('Emergency health card') && openEmergencyModal) {
      openEmergencyModal()
      setIsOpen(false)
      return
    }

    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    const userMsg = { sender: 'user', text: query, time: timeNow }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const { data } = await api.post('/copilot/ask', { query })
      const aiMsg = {
        sender: 'ai',
        text: data.answer,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err) {
      const errorMsg = {
        sender: 'ai',
        text: `Unable to get answer: ${errorMessage(err)}. Please try again.`,
        time: timeNow,
        isError: true,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        className={`copilot-floating-btn ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open CareBridge AI Assistant"
      >
        <span className="copilot-btn-icon">
          <Sparkles size={20} />
        </span>
        <span className="copilot-btn-text">Ask CareBridge AI</span>
        <span className="copilot-pulse-ring" />
      </button>

      {/* Slide-out Drawer */}
      {isOpen && (
        <div className="copilot-drawer">
          <div className="copilot-header">
            <div className="copilot-brand">
              <div className="copilot-avatar">
                <Bot size={20} />
              </div>
              <div>
                <strong>CareBridge AI Copilot</strong>
                <span className="copilot-status">
                  <span className="status-dot-pulse" /> Active · Context-Aware
                </span>
              </div>
            </div>
            <button className="copilot-close" onClick={() => setIsOpen(false)} aria-label="Close assistant">
              <X size={18} />
            </button>
          </div>

          {/* Quick Suggestion Chips */}
          <div className="copilot-chips-bar">
            {QUICK_CHIPS.map((chip, idx) => (
              <button
                key={idx}
                className="copilot-chip"
                onClick={() => handleSend(chip)}
                disabled={loading}
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Conversation Stream */}
          <div className="copilot-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`copilot-msg ${msg.sender === 'user' ? 'msg-user' : 'msg-ai'}`}>
                <div className="msg-avatar">
                  {msg.sender === 'user' ? <User size={14} /> : <Sparkles size={14} />}
                </div>
                <div className="msg-content">
                  <div className="msg-bubble">
                    <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                  </div>
                  <div className="msg-meta">
                    <small>{msg.time}</small>
                    {msg.sender === 'ai' && (
                      <div className="msg-actions">
                        <button
                          className="msg-action-btn"
                          onClick={() => handleSpeech(msg.text, index)}
                          title={speakingIndex === index ? 'Stop speaking' : 'Read aloud'}
                        >
                          {speakingIndex === index ? <VolumeX size={13} /> : <Volume2 size={13} />}
                        </button>
                        <button
                          className="msg-action-btn"
                          onClick={() => handleCopy(msg.text, index)}
                          title="Copy text"
                        >
                          {copiedIndex === index ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="copilot-msg msg-ai">
                <div className="msg-avatar">
                  <Sparkles size={14} />
                </div>
                <div className="msg-content">
                  <div className="msg-bubble msg-typing">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <form
            className="copilot-input-area"
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
          >
            <input
              type="text"
              placeholder="Ask about medications, appointments, tests…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="copilot-send-btn"
              disabled={!input.trim() || loading}
              aria-label="Send message"
            >
              <Send size={16} />
            </button>
          </form>

          <div className="copilot-footnote">
            Clerical healthcare coordination only. Always confirm instructions with your doctor.
          </div>
        </div>
      )}
    </>
  )
}
