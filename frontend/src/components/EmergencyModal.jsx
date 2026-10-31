import { useState, useEffect } from 'react'
import { AlertCircle, Heart, Phone, Printer, ShieldAlert, User, X, Check, Activity, Hospital } from 'lucide-react'
import api, { errorMessage } from '../api'

export default function EmergencyModal({ isOpen, onClose }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sosSent, setSosSent] = useState(false)
  const [sendingSos, setSendingSos] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isOpen) return
    setLoading(true)
    setSosSent(false)
    api.get('/copilot/emergency-card')
      .then(({ data: cardData }) => {
        setData(cardData)
        setLoading(false)
      })
      .catch((err) => {
        setError(errorMessage(err))
        setLoading(false)
      })
  }, [isOpen])

  if (!isOpen) return null

  async function handleSendSos() {
    if (!window.confirm('Broadcast an urgent emergency alert to all connected family members and caregivers?')) {
      return
    }
    setSendingSos(true)
    try {
      await api.post('/copilot/emergency-sos')
      setSosSent(true)
    } catch (err) {
      alert(errorMessage(err))
    } finally {
      setSendingSos(false)
    }
  }

  function handlePrint() {
    window.print()
  }

  const patient = data?.patient

  return (
    <div className="modal-backdrop emergency-backdrop" onClick={onClose}>
      <div className="modal-card emergency-modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="emergency-header">
          <div className="emergency-title-lockup">
            <div className="sos-badge-icon">
              <ShieldAlert size={24} />
            </div>
            <div>
              <div className="emergency-eyebrow">IN CASE OF EMERGENCY (ICE)</div>
              <h2>Digital Emergency Medical Passport</h2>
            </div>
          </div>
          <div className="emergency-top-actions">
            <button className="button button-small button-outline print-hide" onClick={handlePrint}>
              <Printer size={15} /> Print / Save
            </button>
            <button className="icon-link print-hide" onClick={onClose} aria-label="Close emergency modal">
              <X size={20} />
            </button>
          </div>
        </div>

        {error && <div className="form-error">{error}</div>}

        {loading ? (
          <div className="emergency-loading">Loading medical passport data…</div>
        ) : patient ? (
          <div className="emergency-body">
            {/* Urgent SOS Broadcast Bar */}
            <div className="sos-broadcast-strip print-hide">
              <div className="sos-info">
                <strong>Need Immediate Assistance?</strong>
                <span>One-tap broadcast sends SMS & in-app alerts to your emergency caregiver contacts.</span>
              </div>
              <button
                className={`button ${sosSent ? 'button-success-solid' : 'button-danger-solid'}`}
                onClick={handleSendSos}
                disabled={sendingSos || sosSent}
              >
                {sosSent ? <><Check size={16} /> Caregivers Alerted</> : sendingSos ? 'Broadcasting…' : <><Phone size={16} /> Broadcast Emergency SOS</>}
              </button>
            </div>

            {/* Medical Card Grid */}
            <div className="emergency-card-grid">
              {/* Primary Identity Section */}
              <div className="emergency-section identity-section">
                <div className="patient-main-row">
                  <div className="emergency-avatar">
                    <User size={32} />
                  </div>
                  <div>
                    <h3>{patient.full_name}</h3>
                    <div className="patient-demographics">
                      <span>DOB: {patient.date_of_birth}</span>
                      <span>·</span>
                      <span>Phone: {patient.phone}</span>
                    </div>
                  </div>
                  <div className="blood-group-badge">
                    <small>BLOOD GROUP</small>
                    <strong>{patient.blood_group}</strong>
                  </div>
                </div>
              </div>

              {/* Critical Alerts: Allergies & Chronic Conditions */}
              <div className="emergency-two-col">
                <div className="emergency-section alert-box-red">
                  <div className="section-heading-red">
                    <AlertCircle size={17} /> Known Allergies
                  </div>
                  <ul className="pill-list-red">
                    {patient.allergies.map((allergy, i) => (
                      <li key={i}>{allergy}</li>
                    ))}
                  </ul>
                </div>

                <div className="emergency-section alert-box-amber">
                  <div className="section-heading-amber">
                    <Activity size={17} /> Chronic Medical Conditions
                  </div>
                  <ul className="pill-list-amber">
                    {patient.chronic_conditions.map((cond, i) => (
                      <li key={i}>{cond}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Hospital & Attending Physician */}
              <div className="emergency-section hospital-section">
                <div className="section-heading">
                  <Hospital size={17} /> Primary Hospital & Attending Clinician
                </div>
                <div className="hospital-details-row">
                  <div>
                    <strong>{patient.hospital_name}</strong>
                    <p>Primary Physician: {patient.primary_physician}</p>
                  </div>
                  <div className="hospital-helpline">
                    <span>Emergency Helpline:</span>
                    <a href={`tel:${patient.hospital_helpline}`}>{patient.hospital_helpline}</a>
                  </div>
                </div>
              </div>

              {/* Emergency Contacts / Caregivers */}
              <div className="emergency-section caregivers-section">
                <div className="section-heading">
                  <Heart size={17} /> Emergency Contacts & Family Caregivers
                </div>
                <div className="caregiver-cards-row">
                  {data.caregivers.map((cg, i) => (
                    <div className="emergency-cg-card" key={i}>
                      <div>
                        <strong>{cg.name}</strong>
                        <span>{cg.relation} · {cg.email}</span>
                      </div>
                      <a href={`tel:${cg.phone}`} className="button button-small button-outline">
                        <Phone size={13} /> {cg.phone}
                      </a>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Medications List */}
              <div className="emergency-section medications-section">
                <div className="section-heading">Active Prescriptions on Record</div>
                <ul className="emergency-meds-list">
                  {data.medications.map((med, i) => (
                    <li key={i}>
                      <span className="med-bullet" />
                      <span>{med}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="emergency-footer-note">
              <span>Verified CareBridge Medical Passport · Last synced: {data.last_updated}</span>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
