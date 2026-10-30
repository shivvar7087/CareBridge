import { useEffect, useState } from 'react'
import { Database, Globe2, LockKeyhole, Save, ShieldCheck, UserRound } from 'lucide-react'
import api, { errorMessage } from '../api'
import { useAuth } from '../auth'
import { Card, Loading, Notice, PageHeading } from '../components/UI'

export default function SettingsPage() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { api.get('/patients/me').then(({ data }) => setProfile(data)).catch((e) => setError(errorMessage(e))) }, [])
  async function save(e) {
    e.preventDefault(); setBusy(true); setMessage(''); setError('')
    try {
      await api.put('/patients/me', { phone: profile.phone || null, preferred_language: profile.preferred_language, hospital_name: profile.hospital_name || null })
      setMessage('Your profile settings were saved.')
    } catch (e) { setError(errorMessage(e)) } finally { setBusy(false) }
  }
  if (!profile) return error ? <div className="form-error">{error}</div> : <Loading />
  return <div><PageHeading eyebrow="YOUR ACCOUNT" title="Settings" description="Manage the basic contact and display details linked to your care journey." />
    {message && <Notice tone="success">{message}</Notice>}{error && <div className="form-error">{error}</div>}
    <div className="settings-grid"><Card className="settings-profile"><div className="settings-card-head"><span className="settings-icon"><UserRound size={19} /></span><div><h2>Patient profile</h2><p>Only collect details that help coordinate your care.</p></div></div>
      {user.role === 'patient' ? <form onSubmit={save} className="settings-form"><div className="readonly-account"><span>Account name</span><strong>{profile.full_name}</strong><span>Email</span><strong>{profile.email}</strong></div><label className="field"><span>Phone (optional)</span><input value={profile.phone || ''} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} placeholder="Add a contact number" /></label><label className="field"><span>Preferred language</span><select value={profile.preferred_language || 'English'} onChange={(e) => setProfile({ ...profile, preferred_language: e.target.value })}>{['English', 'Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Kannada', 'Malayalam', 'Gujarati', 'Other'].map((x) => <option key={x}>{x}</option>)}</select></label><label className="field"><span>Hospital / clinic</span><input value={profile.hospital_name || ''} onChange={(e) => setProfile({ ...profile, hospital_name: e.target.value })} placeholder="Optional" /></label><button className="button button-primary" disabled={busy}><Save size={15} /> {busy ? 'Saving...' : 'Save profile'}</button></form> : <div className="readonly-account"><span>Patient</span><strong>{profile.full_name}</strong><span>Access</span><strong>Shared journey tasks only</strong></div>}
    </Card><div className="settings-side"><Card><div className="settings-card-head"><span className="settings-icon settings-icon-green"><LockKeyhole size={19} /></span><div><h3>Privacy and access</h3><p>Your journey is private unless you share it.</p></div></div><div className="setting-detail"><ShieldCheck size={15} /><span>Caregiver access can be removed at any time.</span></div><div className="setting-detail"><Database size={15} /><span>Uploaded documents are stored by the backend.</span></div></Card><Card><div className="settings-card-head"><span className="settings-icon settings-icon-purple"><Globe2 size={19} /></span><div><h3>Workspace</h3><p>{user.role === 'patient' ? 'Patient workspace' : 'Caregiver workspace'}</p></div></div><div className="workspace-detail"><span>Notifications</span><strong>In-app only</strong></div><div className="workspace-detail"><span>External messaging</span><strong>Not configured</strong></div><div className="workspace-detail"><span>Demo data</span><strong>{profile.is_demo ? 'Fictional sample' : 'Off'}</strong></div></Card></div></div>
    <div className="safety-footnote">CareBridge AI is a coordination tool. For changes to medical care instructions, contact your healthcare professional.</div>
  </div>
}
