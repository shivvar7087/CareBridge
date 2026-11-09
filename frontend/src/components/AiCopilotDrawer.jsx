import { useState, useRef, useEffect } from 'react'
import { Sparkles, Send, X, Volume2, VolumeX, Bot, User, Copy, Check, MessageSquare, Languages } from 'lucide-react'
import api, { errorMessage } from '../api'

const QUICK_CHIPS_EN = [
  '💊 My medication schedule',
  '📅 When is my next appointment?',
  '📋 Missing diagnostic reports?',
  '🚨 Emergency health card',
  '🤝 Who are my caregivers?',
]

const QUICK_CHIPS_HI = [
  '💊 मेरी दवाइयों का समय',
  '📅 अगली डॉक्टर विज़िट कब है?',
  '📋 क्या कोई रिपोर्ट बाकी है?',
  '🚨 इमरजेंसी हेल्थ कार्ड',
  '🤝 मेरे देखभालकर्ता कौन हैं?',
]

export default function AiCopilotDrawer({ openEmergencyModal }) {
  const [isOpen, setIsOpen] = useState(false)
  const [language, setLanguage] = useState('en')
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

  // Update welcome greeting when language changes
  const handleLanguageChange = (newLang) => {
    setLanguage(newLang)
    const greeting = newLang === 'hi'
      ? 'नमस्ते! मैं आपका CareBridge AI स्वास्थ्य सहायक हूँ। आज मैं आपकी दवाओं, डॉक्टर अपॉइंटमेंट या रिकवरी यात्रा में कैसे मदद कर सकता हूँ?'
      : 'Hello! I am your CareBridge AI Health Assistant. How can I help coordinate your care plan, appointments, or prescriptions today?'
    setMessages((prev) => [
      ...prev,
      {
        sender: 'ai',
        text: greeting,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ])
  }

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
    utterance.lang = language === 'hi' ? 'hi-IN' : 'en-US'
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

    if ((query.includes('Emergency health card') || query.includes('इमरजेंसी हेल्थ कार्ड')) && openEmergencyModal) {
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
      const { data } = await api.post('/copilot/ask', { query, language })
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

  const chips = language === 'hi' ? QUICK_CHIPS_HI : QUICK_CHIPS_EN

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
        <span className="copilot-btn-text">
          {language === 'hi' ? 'AI से पूछें (हिंदी/EN)' : 'Ask CareBridge AI'}
        </span>
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
                  <span className="status-dot-pulse" /> Active · Bilingual (EN/हिंदी)
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {/* Language Switcher */}
              <div style={{ display: 'flex', background: '#F1F5F9', padding: 2, borderRadius: 8 }}>
                <button
                  type="button"
                  onClick={() => handleLanguageChange('en')}
                  style={{
                    border: 'none',
                    padding: '3px 8px',
                    borderRadius: 6,
                    fontSize: 11,
                    fontWeight: 700,
                    cursor: 'pointer',
                    background: language === 'en' ? '#2563EB' : 'transparent',
                    color: language === 'en' ? '#fff' : '#64748B',
                  }}
                >
                  EN
                </button>
                <button
                  type="button"
                  onClick={() => handleLanguageChange('hi')}
                  style={{
                    border: 'none',
                    padding: '3px 8px',
                    borderRadius: 6,
                    fontSize: 11,
                    fontWeight: 700,
                    cursor: 'pointer',
                    background: language === 'hi' ? '#2563EB' : 'transparent',
                    color: language === 'hi' ? '#fff' : '#64748B',
                  }}
                >
                  हिंदी
                </button>
              </div>

              <button className="copilot-close" onClick={() => setIsOpen(false)} aria-label="Close assistant">
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Quick Suggestion Chips */}
          <div className="copilot-chips-bar">
            {chips.map((chip, idx) => (
              <button key={idx} className="copilot-chip" onClick={() => handleSend(chip)}>
                {chip}
              </button>
            ))}
          </div>

          {/* Messages Feed */}
          <div className="copilot-messages">
            {messages.map((msg, index) => {
              const isAi = msg.sender === 'ai'
              return (
                <div key={index} className={`copilot-msg-row ${isAi ? 'ai-row' : 'user-row'}`}>
                  <div className="msg-avatar-icon">
                    {isAi ? <Bot size={16} /> : <User size={16} />}
                  </div>
                  <div className={`copilot-bubble ${isAi ? 'ai-bubble' : 'user-bubble'} ${msg.isError ? 'error-bubble' : ''}`}>
                    <div className="bubble-content" style={{ whiteSpace: 'pre-line' }}>
                      {msg.text}
                    </div>
                    <div className="bubble-footer">
                      <span className="msg-timestamp">{msg.time}</span>
                      {isAi && !msg.isError && (
                        <div className="bubble-actions">
                          <button
                            className="bubble-action-btn"
                            title="Read aloud"
                            onClick={() => handleSpeech(msg.text, index)}
                          >
                            {speakingIndex === index ? <VolumeX size={13} /> : <Volume2 size={13} />}
                          </button>
                          <button
                            className="bubble-action-btn"
                            title="Copy response"
                            onClick={() => handleCopy(msg.text, index)}
                          >
                            {copiedIndex === index ? <Check size={13} color="#16a34a" /> : <Copy size={13} />}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
            {loading && (
              <div className="copilot-msg-row ai-row">
                <div className="msg-avatar-icon">
                  <Bot size={16} />
                </div>
                <div className="copilot-bubble ai-bubble typing-bubble">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <form
            className="copilot-input-bar"
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
          >
            <input
              type="text"
              placeholder={language === 'hi' ? 'दवा, अपॉइंटमेंट या रिपोर्ट के बारे में पूछें...' : 'Ask about medicines, reports, appointments...'}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="copilot-send-btn"
              disabled={!input.trim() || loading}
              aria-label="Send query"
            >
              <Send size={16} />
            </button>
          </form>

          <div style={{ padding: '6px 16px 10px', fontSize: 10.5, color: '#94A3B8', textAlign: 'center', background: '#fff', borderTop: '1px solid #F1F5F9' }}>
            CareBridge AI · Team ByteCoders (IIMT Engineering College, Meerut)
          </div>
        </div>
      )}
    </>
  )
}
