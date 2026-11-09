import { useEffect, useState } from 'react'
import {
  Activity, AlertCircle, Bell, Check, Database, Download, Globe2, Heart,
  Hospital, LockKeyhole, Phone, Printer, Save, ShieldAlert, ShieldCheck,
  Sparkles, Trash2, UserRound, Volume2, Award
} from 'lucide-react'
import api, { errorMessage } from '../api'
import { useAuth } from '../auth'
import { Card, Loading, Notice, PageHeading } from '../components/UI'

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
const LANGUAGES = [
  'English', 'Hindi (हिंदी)', 'Bengali (বাংলা)', 'Tamil (தமிழ்)',
  'Telugu (తెలుగు)', 'Marathi (मराठी)', 'Kannada (ಕನ್ನಡ)', 'Malayalam (മലയാളം)', 'Gujarati (ગુજરાતી)'
]

const COMMON_ALLERGIES = [
  'Penicillin', 'NSAIDs (Ibuprofen / Diclofenac)', 'Sulfa Drugs',
  'Aspirin', 'Latex', 'Contrast Dye (Iodine)', 'Peanuts', 'None'
]

const CHRONIC_CONDITIONS = [
  'Essential Hypertension', 'Type-2 Diabetes Mellitus', 'Coronary Artery Disease',
  'Asthma / COPD', 'Thyroid Disorder', 'Post-Op Knee / Hip Recovery', 'None'
]

export default function SettingsPage() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [activeTab, setActiveTab] = useState('profile')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  // Extended Preferences State
  const [preferences, setPreferences] = useState({
    blood_group: 'B+ Positive',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    allergies: ['Penicillin (Moderate rash / anaphylactoid)', 'NSAIDs (Mild gastric distress)'],
    chronic_conditions: ['Essential Hypertension', 'Type-2 Diabetes Mellitus (Controlled)'],
    organ_donor: true,
    physician_name: 'Dr. Sarah Chen, MD (Cardiology)',
    hospital_helpline: '+91 11 2658 8500',
    // Notifications
    notify_medication_morning: true,
    notify_medication_evening: true,
    notify_appointments_24h: true,
    notify_report_readiness: true,
    notify_caregiver_actions: true,
    audio_chimes: true,
    tts_speed: 'normal',
    // Caregiver permissions
    share_medication_adherence: true,
    share_reports: true,
    broadcast_sos_to_caregivers: true,
  })

  useEffect(() => {
    api.get('/patients/me')
      .then(({ data }) => {
        setProfile(data)
        if (data.blood_group) {
          setPreferences((prev) => ({ ...prev, blood_group: data.blood_group }))
        }
        if (data.emergency_contact_name) {
          setPreferences((prev) => ({ ...prev, emergency_contact_name: data.emergency_contact_name }))
        }
        if (data.emergency_contact_phone) {
          setPreferences((prev) => ({ ...prev, emergency_contact_phone: data.emergency_contact_phone }))
        }
        if (data.settings_json) {
          try {
            const parsed = JSON.parse(data.settings_json)
            setPreferences((prev) => ({ ...prev, ...parsed }))
          } catch (e) {
            // keep defaults
          }
        }
      })
      .catch((e) => setError(errorMessage(e)))
  }, [])

  function toggleAllergy(item) {
    if (item === 'None') {
      setPreferences((prev) => ({ ...prev, allergies: ['None'] }))
      return
    }
    setPreferences((prev) => {
      const current = prev.allergies.filter((a) => a !== 'None')
      const exists = current.some((a) => a.includes(item))
      const updated = exists ? current.filter((a) => !a.includes(item)) : [...current, item]
      return { ...prev, allergies: updated }
    })
  }

  function toggleCondition(item) {
    if (item === 'None') {
      setPreferences((prev) => ({ ...prev, chronic_conditions: ['None'] }))
      return
    }
    setPreferences((prev) => {
      const current = prev.chronic_conditions.filter((c) => c !== 'None')
      const exists = current.some((c) => c.includes(item))
      const updated = exists ? current.filter((c) => !c.includes(item)) : [...current, item]
      return { ...prev, chronic_conditions: updated }
    })
  }

  async function saveAll(e) {
    if (e) e.preventDefault()
    setBusy(true)
    setMessage('')
    setError('')
    try {
      await api.put('/patients/me', {
        phone: profile.phone || null,
        preferred_language: profile.preferred_language,
        hospital_name: profile.hospital_name || null,
        blood_group: preferences.blood_group,
        emergency_contact_name: preferences.emergency_contact_name || null,
        emergency_contact_phone: preferences.emergency_contact_phone || null,
        settings_json: JSON.stringify(preferences),
      })
      setMessage('All profile, emergency ID, and care settings saved successfully!')
      setTimeout(() => setMessage(''), 4000)
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setBusy(false)
    }
  }

  function exportData() {
    const payload = {
      patient: profile,
      preferences,
      exported_at: new Date().toISOString(),
      platform: 'CareBridge AI · Team ByteCoders (IIMT Engineering College, Meerut)',
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `carebridge_medical_record_${profile?.id || 'demo'}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  function clearCache() {
    if (window.confirm('Clear local temporary session cache? You will remain logged in.')) {
      window.localStorage.removeItem('carebridge_cached_tasks')
      window.localStorage.removeItem('carebridge_offline_adherence')
      alert('Local session cache cleared.')
    }
  }

  if (!profile) return error ? <div className="form-error">{error}</div> : <Loading />

  return (
    <div>
      <PageHeading
        eyebrow="ACCOUNT & CARE PREFERENCES"
        title="Settings & Medical Configuration"
        description="Manage clinical contacts, Emergency ICE ID card, notification alerts, and caregiver sharing permissions."
      />

      {message && <Notice tone="success">{message}</Notice>}
      {error && <div className="form-error">{error}</div>}

      {/* Settings Navigation Tabs */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20, borderBottom: '1px solid #E2E8F0', paddingBottom: 10 }}>
        {[
          { id: 'profile', label: '👤 Profile & Hospital', desc: 'Basic info' },
          { id: 'ice', label: '🚨 Emergency ICE ID', desc: 'Paramedic triage' },
          { id: 'notifications', label: '🔔 Reminders & Audio', desc: 'Alert schedules' },
          { id: 'sharing', label: '🤝 Caregiver Sharing', desc: 'Privacy controls' },
          { id: 'data', label: '💾 Data & Export', desc: 'DPDP compliance' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '8px 16px',
              borderRadius: 10,
              fontSize: 13,
              fontWeight: 700,
              cursor: 'pointer',
              border: 'none',
              background: activeTab === tab.id ? '#2563EB' : '#F1F5F9',
              color: activeTab === tab.id ? '#fff' : '#475569',
              transition: 'all 0.2s',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="settings-grid">
        {/* Main Settings Card based on Active Tab */}
        <Card style={{ flex: 2 }}>
          {/* TAB 1: Profile & Hospital */}
          {activeTab === 'profile' && (
            <div>
              <div className="settings-card-head">
                <span className="settings-icon"><UserRound size={19} /></span>
                <div>
                  <h2>Patient Profile & Clinical Facility</h2>
                  <p>Contact details and clinical establishment coordinating your recovery.</p>
                </div>
              </div>

              {user.role === 'patient' ? (
                <form onSubmit={saveAll} className="settings-form">
                  <div className="readonly-account">
                    <span>Account Name</span>
                    <strong>{profile.full_name}</strong>
                    <span>Email Address</span>
                    <strong>{profile.email}</strong>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
                    <label className="field">
                      <span>Phone Number</span>
                      <input
                        value={profile.phone || ''}
                        onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                        placeholder="+91 98100 23456"
                      />
                    </label>

                    <label className="field">
                      <span>Preferred Language</span>
                      <select
                        value={profile.preferred_language || 'English'}
                        onChange={(e) => setProfile({ ...profile, preferred_language: e.target.value })}
                      >
                        {LANGUAGES.map((x) => (
                          <option key={x} value={x.split(' ')[0]}>{x}</option>
                        ))}
                      </select>
                    </label>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
                    <label className="field">
                      <span>Primary Hospital / Clinic</span>
                      <input
                        value={profile.hospital_name || ''}
                        onChange={(e) => setProfile({ ...profile, hospital_name: e.target.value })}
                        placeholder="Harborview Medical Centre"
                      />
                    </label>

                    <label className="field">
                      <span>Attending Physician</span>
                      <input
                        value={preferences.physician_name}
                        onChange={(e) => setPreferences({ ...preferences, physician_name: e.target.value })}
                        placeholder="Dr. Sarah Chen, MD"
                      />
                    </label>
                  </div>

                  <label className="field">
                    <span>Hospital Emergency Helpline</span>
                    <input
                      value={preferences.hospital_helpline}
                      onChange={(e) => setPreferences({ ...preferences, hospital_helpline: e.target.value })}
                      placeholder="+91 11 2658 8500"
                    />
                  </label>

                  <button className="button button-primary" disabled={busy}>
                    <Save size={15} /> {busy ? 'Saving…' : 'Save Profile Details'}
                  </button>
                </form>
              ) : (
                <div className="readonly-account">
                  <span>Patient</span>
                  <strong>{profile.full_name}</strong>
                  <span>Your Access</span>
                  <strong>Authorized Family Caregiver</strong>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Emergency ICE ID Passport */}
          {activeTab === 'ice' && (
            <div>
              <div className="settings-card-head">
                <span className="settings-icon settings-icon-red"><ShieldAlert size={19} color="#DC2626" /></span>
                <div>
                  <h2>In Case of Emergency (ICE) Configuration</h2>
                  <p>Critical triage information delivered to first responders in under 5 seconds.</p>
                </div>
              </div>

              <form onSubmit={saveAll} className="settings-form">
                {/* Blood Group Selector */}
                <div>
                  <label className="field-label" style={{ fontWeight: 700, fontSize: 13, marginBottom: 8, display: 'block' }}>
                    Blood Group:
                  </label>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {BLOOD_GROUPS.map((bg) => (
                      <button
                        key={bg}
                        type="button"
                        onClick={() => setPreferences({ ...preferences, blood_group: bg })}
                        style={{
                          padding: '6px 14px',
                          borderRadius: 8,
                          fontSize: 13,
                          fontWeight: 800,
                          cursor: 'pointer',
                          border: preferences.blood_group === bg ? '2px solid #DC2626' : '1px solid #CBD5E1',
                          background: preferences.blood_group === bg ? '#FEF2F2' : '#fff',
                          color: preferences.blood_group === bg ? '#DC2626' : '#334155',
                        }}
                      >
                        {bg}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Emergency Contact */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
                  <label className="field">
                    <span>Emergency Contact Name</span>
                    <input
                      value={preferences.emergency_contact_name}
                      onChange={(e) => setPreferences({ ...preferences, emergency_contact_name: e.target.value })}
                      placeholder="e.g. Priya Sharma (Spouse / Sibling)"
                    />
                  </label>
                  <label className="field">
                    <span>Emergency Contact Phone</span>
                    <input
                      value={preferences.emergency_contact_phone}
                      onChange={(e) => setPreferences({ ...preferences, emergency_contact_phone: e.target.value })}
                      placeholder="+91 98765 43210"
                    />
                  </label>
                </div>

                {/* Known Allergies Checklist */}
                <div>
                  <label className="field-label" style={{ fontWeight: 700, fontSize: 13, marginBottom: 6, display: 'block' }}>
                    Critical Drug Allergies:
                  </label>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {COMMON_ALLERGIES.map((allergy) => {
                      const selected = preferences.allergies.some((a) => a.includes(allergy))
                      return (
                        <button
                          key={allergy}
                          type="button"
                          onClick={() => toggleAllergy(allergy)}
                          style={{
                            padding: '6px 12px',
                            borderRadius: 8,
                            fontSize: 12,
                            fontWeight: 600,
                            cursor: 'pointer',
                            border: selected ? '1px solid #EF4444' : '1px solid #CBD5E1',
                            background: selected ? '#FEE2E2' : '#F8FAFC',
                            color: selected ? '#991B1B' : '#475569',
                          }}
                        >
                          {selected ? '⚠️ ' : ''}{allergy}
                        </button>
                      )
                    })}
                  </div>
                </div>

                {/* Chronic Conditions */}
                <div>
                  <label className="field-label" style={{ fontWeight: 700, fontSize: 13, marginBottom: 6, display: 'block' }}>
                    Chronic Health Conditions:
                  </label>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {CHRONIC_CONDITIONS.map((cond) => {
                      const selected = preferences.chronic_conditions.some((c) => c.includes(cond))
                      return (
                        <button
                          key={cond}
                          type="button"
                          onClick={() => toggleCondition(cond)}
                          style={{
                            padding: '6px 12px',
                            borderRadius: 8,
                            fontSize: 12,
                            fontWeight: 600,
                            cursor: 'pointer',
                            border: selected ? '1px solid #F97316' : '1px solid #CBD5E1',
                            background: selected ? '#FFEDD5' : '#F8FAFC',
                            color: selected ? '#9A3412' : '#475569',
                          }}
                        >
                          {cond}
                        </button>
                      )
                    })}
                  </div>
                </div>

                {/* Organ Donor Toggle */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F8FAFC', borderRadius: 10, border: '1px solid #E2E8F0' }}>
                  <div>
                    <strong style={{ fontSize: 13.5, display: 'block' }}>Registered Organ Donor</strong>
                    <span style={{ fontSize: 12, color: '#64748B' }}>Displays life-saving donor confirmation on Paramedic ICE card.</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={preferences.organ_donor}
                    onChange={(e) => setPreferences({ ...preferences, organ_donor: e.target.checked })}
                    style={{ width: 18, height: 18, cursor: 'pointer' }}
                  />
                </div>

                <div style={{ display: 'flex', gap: 10 }}>
                  <button className="button button-primary" disabled={busy}>
                    <Save size={15} /> {busy ? 'Saving…' : 'Save Emergency ICE Settings'}
                  </button>
                  <a href={`/ice/${profile.id || 1}`} target="_blank" rel="noreferrer" className="button button-outline" style={{ display: 'flex', alignItems: 'center', gap: 6, textDecoration: 'none' }}>
                    <ShieldAlert size={15} color="#DC2626" /> View Public QR Passport →
                  </a>
                </div>
              </form>
            </div>
          )}

          {/* TAB 3: Notifications & Reminders */}
          {activeTab === 'notifications' && (
            <div>
              <div className="settings-card-head">
                <span className="settings-icon settings-icon-purple"><Bell size={19} color="#7C3AED" /></span>
                <div>
                  <h2>Medication Reminders & Notification Schedules</h2>
                  <p>Configure automated reminders to stay on schedule with daily medications and doctor appointments.</p>
                </div>
              </div>

              <form onSubmit={saveAll} className="settings-form">
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {[
                    { key: 'notify_medication_morning', title: 'Morning Medication Alarm (08:00 AM)', desc: 'Daily notification for morning doses (Aspirin, Metformin)' },
                    { key: 'notify_medication_evening', title: 'Bedtime Medication Reminder (08:00 PM)', desc: 'Daily notification for cholesterol & evening doses (Atorvastatin)' },
                    { key: 'notify_appointments_24h', title: '24-Hour Advance Appointment Alerts', desc: 'Alerts you 1 day before any scheduled clinic or doctor visit' },
                    { key: 'notify_report_readiness', title: 'Diagnostic Lab Report Readiness Alerts', desc: 'Notifies you when required lab tests are due or missing' },
                    { key: 'notify_caregiver_actions', title: 'Caregiver Activity Sync', desc: 'Notifies you when a family caregiver completes or logs an assigned recovery task' },
                    { key: 'audio_chimes', title: 'Audio Alert Sound & Chime', desc: 'Plays soft audio notification when reminders trigger' },
                  ].map((item) => (
                    <label key={item.key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F8FAFC', borderRadius: 10, border: '1px solid #E2E8F0', cursor: 'pointer' }}>
                      <div>
                        <strong style={{ fontSize: 13.5, display: 'block', color: '#0F172A' }}>{item.title}</strong>
                        <span style={{ fontSize: 12, color: '#64748B' }}>{item.desc}</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={!!preferences[item.key]}
                        onChange={(e) => setPreferences({ ...preferences, [item.key]: e.target.checked })}
                        style={{ width: 18, height: 18, cursor: 'pointer' }}
                      />
                    </label>
                  ))}
                </div>

                <button className="button button-primary" disabled={busy}>
                  <Save size={15} /> {busy ? 'Saving…' : 'Save Notification Preferences'}
                </button>
              </form>
            </div>
          )}

          {/* TAB 4: Caregiver Sharing & Privacy */}
          {activeTab === 'sharing' && (
            <div>
              <div className="settings-card-head">
                <span className="settings-icon settings-icon-green"><LockKeyhole size={19} color="#16A34A" /></span>
                <div>
                  <h2>Caregiver Sharing & Access Control</h2>
                  <p>Fine-grained permissions governing what connected family caregivers can see and assist with.</p>
                </div>
              </div>

              <form onSubmit={saveAll} className="settings-form">
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F0FDF4', borderRadius: 10, border: '1px solid #BBF7D0', cursor: 'pointer' }}>
                    <div>
                      <strong style={{ fontSize: 13.5, display: 'block', color: '#14532D' }}>Share Daily Medication Adherence</strong>
                      <span style={{ fontSize: 12, color: '#166534' }}>Allows caregivers to monitor adherence streak and see if doses are taken.</span>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.share_medication_adherence}
                      onChange={(e) => setPreferences({ ...preferences, share_medication_adherence: e.target.checked })}
                      style={{ width: 18, height: 18 }}
                    />
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F8FAFC', borderRadius: 10, border: '1px solid #E2E8F0', cursor: 'pointer' }}>
                    <div>
                      <strong style={{ fontSize: 13.5, display: 'block' }}>Share Diagnostic Lab Report Availability</strong>
                      <span style={{ fontSize: 12, color: '#64748B' }}>Caregivers can view which reports are needed and help collect physical copies.</span>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.share_reports}
                      onChange={(e) => setPreferences({ ...preferences, share_reports: e.target.checked })}
                      style={{ width: 18, height: 18 }}
                    />
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#FEF2F2', borderRadius: 10, border: '1px solid #FECACA', cursor: 'pointer' }}>
                    <div>
                      <strong style={{ fontSize: 13.5, display: 'block', color: '#991B1B' }}>Allow Emergency SOS Alerts</strong>
                      <span style={{ fontSize: 12, color: '#7F1D1D' }}>Broadcasts high-priority alerts to caregivers when the SOS button is triggered.</span>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.broadcast_sos_to_caregivers}
                      onChange={(e) => setPreferences({ ...preferences, broadcast_sos_to_caregivers: e.target.checked })}
                      style={{ width: 18, height: 18 }}
                    />
                  </label>
                </div>

                <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: 14, borderRadius: 10, fontSize: 12, color: '#475569', lineHeight: 1.5 }}>
                  <ShieldCheck size={16} style={{ color: '#16A34A', verticalAlign: 'middle', marginRight: 6 }} />
                  <strong>DPDP Act Compliance:</strong> Caregiver access is read-only for clinical orders. Caregivers cannot alter prescription doses or delete clinician notes. Access can be revoked anytime from the Caregivers tab.
                </div>

                <button className="button button-primary" disabled={busy}>
                  <Save size={15} /> {busy ? 'Saving…' : 'Save Sharing Permissions'}
                </button>
              </form>
            </div>
          )}

          {/* TAB 5: Data & Export */}
          {activeTab === 'data' && (
            <div>
              <div className="settings-card-head">
                <span className="settings-icon"><Database size={19} /></span>
                <div>
                  <h2>Data Portability & Offline Storage</h2>
                  <p>Download your complete recovery journey records or manage local cache.</p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 16, background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 12, flexWrap: 'wrap', gap: 12 }}>
                  <div>
                    <strong style={{ fontSize: 14, display: 'block' }}>Export Complete Medical Record (JSON)</strong>
                    <span style={{ fontSize: 12, color: '#64748B' }}>Download a portable copy of your medications, journey milestones, and emergency ID.</span>
                  </div>
                  <button type="button" className="button button-secondary" onClick={exportData}>
                    <Download size={15} /> Export JSON
                  </button>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 16, background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 12, flexWrap: 'wrap', gap: 12 }}>
                  <div>
                    <strong style={{ fontSize: 14, display: 'block' }}>Print Physical Emergency Card</strong>
                    <span style={{ fontSize: 12, color: '#64748B' }}>Generate a wallet-sized printable medical card with scannable QR code.</span>
                  </div>
                  <button type="button" className="button button-outline" onClick={() => window.print()}>
                    <Printer size={15} /> Print Card
                  </button>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 16, background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 12, flexWrap: 'wrap', gap: 12 }}>
                  <div>
                    <strong style={{ fontSize: 14, display: 'block', color: '#991B1B' }}>Clear Local Offline Cache</strong>
                    <span style={{ fontSize: 12, color: '#7F1D1D' }}>Resets local cached state and forces a fresh sync with cloud servers.</span>
                  </div>
                  <button type="button" className="button button-outline" style={{ borderColor: '#FCA5A5', color: '#DC2626' }} onClick={clearCache}>
                    <Trash2 size={15} /> Clear Cache
                  </button>
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* Sidebar Summary Card */}
        <div className="settings-side">
          <Card>
            <div className="settings-card-head">
              <span className="settings-icon settings-icon-green"><LockKeyhole size={19} /></span>
              <div>
                <h3>Privacy and access</h3>
                <p>Your journey is private unless you share it.</p>
              </div>
            </div>
            <div className="setting-detail">
              <ShieldCheck size={15} />
              <span>Caregiver access can be revoked at any time.</span>
            </div>
            <div className="setting-detail">
              <Database size={15} />
              <span>Dual SQLite / PostgreSQL compliant storage.</span>
            </div>
            <div className="setting-detail">
              <ShieldAlert size={15} color="#DC2626" />
              <span>Emergency ICE Passport active (<a href={`/ice/${profile.id || 1}`} target="_blank" rel="noreferrer" style={{ color: '#2563EB', fontWeight: 600 }}>Preview</a>).</span>
            </div>
          </Card>

          <Card>
            <div className="settings-card-head">
              <span className="settings-icon settings-icon-purple"><Globe2 size={19} /></span>
              <div>
                <h3>Workspace Details</h3>
                <p>{user.role === 'patient' ? 'Patient workspace' : 'Caregiver workspace'}</p>
              </div>
            </div>
            <div className="workspace-detail">
              <span>Blood Group</span>
              <strong style={{ color: '#DC2626' }}>{preferences.blood_group}</strong>
            </div>
            <div className="workspace-detail">
              <span>Notifications</span>
              <strong>In-app & Scheduled</strong>
            </div>
            <div className="workspace-detail">
              <span>Bilingual AI</span>
              <strong>English & हिंदी</strong>
            </div>
            <div className="workspace-detail">
              <span>Demo Mode</span>
              <strong>{profile.is_demo ? 'Active (Fictional)' : 'Off'}</strong>
            </div>
          </Card>
        </div>
      </div>

      <div className="safety-footnote" style={{ marginTop: 24 }}>
        CareBridge AI is a healthcare coordination system. For changes to prescription treatment, consult your physician.
      </div>
    </div>
  )
}
