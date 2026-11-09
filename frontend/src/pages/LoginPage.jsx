import { useState } from 'react'
import { Activity, ArrowRight, Eye, EyeOff, HeartHandshake, ShieldCheck, Sparkles } from 'lucide-react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { errorMessage } from '../api'

export default function LoginPage() {
  const { user, login, register, loading } = useAuth()
  const [mode, setMode] = useState('login')
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ email: '', password: '', full_name: '', role: 'patient', invite_code: '' })
  if (loading) return <div className="screen-loader"><span className="spinner" /> Loading…</div>
  if (user) return <Navigate to="/" replace />
  function change(key, value) { setForm((prev) => ({ ...prev, [key]: value })) }
  async function submit(event) {
    event.preventDefault(); setError(''); setBusy(true)
    try { if (mode === 'login') await login({ email: form.email, password: form.password }); else await register(form) }
    catch (e) { setError(errorMessage(e)) } finally { setBusy(false) }
  }
  async function demoLogin() { setError(''); setBusy(true); try { await login({ email: 'demo@carebridge.ai', password: 'carebridge123' }) } catch (e) { setError(errorMessage(e)) } finally { setBusy(false) } }

  return <div className="auth-screen"><div className="auth-visual"><div className="auth-brand"><span className="brand-mark"><Activity size={21} /></span>CareBridge</div>
    <div className="visual-content"><div className="visual-tag"><Sparkles size={14} /> CARE COORDINATION, MADE CLEAR</div><h1>Your next steps,<br /><em>all in one place.</em></h1><p>Bring care plans, appointments, reports, and the people who support you together in one calm, organized workspace.</p>
      <div className="journey-preview"><div className="preview-heading"><span>YOUR CARE JOURNEY</span><span className="preview-dot" /> ACTIVE</div><div className="preview-step done"><span className="preview-node"><span>✓</span></span><div><strong>Hospital discharge</strong><small>Care plan received</small></div><span className="preview-date">DONE</span></div><div className="preview-step current"><span className="preview-node"><span>2</span></span><div><strong>Collect blood test report</strong><small>Shared with your caregiver</small></div><span className="preview-date">NEXT</span></div><div className="preview-step"><span className="preview-node"><span>3</span></span><div><strong>Follow-up appointment</strong><small>Friday, 14 November</small></div></div></div>
      <div className="visual-foot"><ShieldCheck size={17} /><span>Designed to help organize care instructions, not replace your care team.</span></div></div></div>
    <div className="auth-panel"><div className="auth-form-wrap"><div className="mobile-auth-brand"><span className="brand-mark"><Activity size={21} /></span>CareBridge</div><div className="auth-kicker">WELCOME TO CAREBRIDGE</div><h2>{mode === 'login' ? 'Sign in to your account' : 'Create your account'}</h2><p className="auth-subtitle">{mode === 'login' ? 'Your healthcare journey is ready when you are.' : 'Set up a secure space for your care journey.'}</p>
      {error && <div className="form-error">{error}</div>}
      <form onSubmit={submit} className="auth-form">
        {mode === 'register' && <><label className="field"><span>Full name</span><input required minLength="2" value={form.full_name} onChange={(e) => change('full_name', e.target.value)} placeholder="Your name" /></label><label className="field"><span>Account type</span><select value={form.role} onChange={(e) => change('role', e.target.value)}><option value="patient">Patient</option><option value="caregiver">Caregiver</option></select></label>{form.role === 'caregiver' && <label className="field"><span>Invitation code</span><input required value={form.invite_code} onChange={(e) => change('invite_code', e.target.value)} placeholder="Code from the patient" /></label>}</>}
        <label className="field"><span>Email address</span><input type="email" required value={form.email} onChange={(e) => change('email', e.target.value)} placeholder="you@example.com" autoComplete="email" /></label>
        <label className="field"><span>Password</span><span className="password-wrap"><input type={showPassword ? 'text' : 'password'} required minLength={mode === 'register' ? 8 : undefined} value={form.password} onChange={(e) => change('password', e.target.value)} placeholder={mode === 'register' ? 'At least 8 characters' : 'Enter your password'} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} /><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label="Toggle password visibility">{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></span></label>
        <button className="button button-primary full-width auth-submit" disabled={busy}>{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}<ArrowRight size={17} /></button>
      </form>
      {mode === 'login' && <><div className="auth-divider"><span>OR TRY A DEMO</span></div><button className="button button-outline full-width demo-button" onClick={demoLogin} disabled={busy}><HeartHandshake size={17} /> Continue with fictional demo account</button><div className="demo-credentials">Demo: <b>demo@carebridge.ai</b> · password <b>carebridge123</b></div></>}
      <div style={{ marginTop: 14, textAlign: 'center' }}>
        <Link to="/ice" style={{ color: '#DC2626', fontSize: 12.5, fontWeight: 700, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 6, background: '#FEF2F2', padding: '6px 14px', borderRadius: 8, border: '1px solid #FECACA' }}>
          🚨 First Responders: Open Public ICE Passport (&lt; 5s) →
        </Link>
      </div>
      <p className="auth-switch">{mode === 'login' ? 'New to CareBridge?' : 'Already have an account?'} <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>{mode === 'login' ? 'Create an account' : 'Sign in'}</button></p>
      <div className="auth-privacy"><ShieldCheck size={15} /> Your information stays private. No external messages are sent from this demo.</div>
    </div></div></div>
}
