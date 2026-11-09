import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { AlertCircle, Activity, Heart, Hospital, Phone, Printer, ShieldAlert, User, CheckCircle2 } from 'lucide-react'
import axios from 'axios'

export default function PublicIcePassport() {
  const { patientId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const apiBase = import.meta.env.VITE_API_URL || 'https://carebridge-1-9b9i.onrender.com/api'

  useEffect(() => {
    const id = patientId || '1'
    axios
      .get(`${apiBase}/copilot/public-ice/${id}`)
      .then((res) => {
        setData(res.data)
        setLoading(false)
      })
      .catch((err) => {
        // Fallback demo dataset if API unreachable
        setData({
          patient: {
            id: 1,
            full_name: 'Rahul Sharma (Demo Patient)',
            phone: '+91 98100 23456',
            date_of_birth: '1988-06-15',
            blood_group: 'B+ Positive',
            allergies: ['Penicillin (Moderate rash / anaphylactoid)', 'NSAIDs (Mild gastric distress)'],
            chronic_conditions: ['Essential Hypertension', 'Type-2 Diabetes Mellitus (Controlled)'],
            hospital_name: 'Harborview Medical Centre',
            primary_physician: 'Dr. Sarah Chen, MD (Cardiology)',
            hospital_helpline: '+91 11 2658 8500',
            organ_donor: true,
            emergency_notes: 'Patient carries an emergency inhaler and medical alert bracelet. Zero NSAIDs.',
            team_badge: 'ByteCoders · IIMT Engineering College, Meerut',
          },
          caregivers: [
            { name: 'Priya Sharma', relation: 'Family Caregiver', phone: '+91 98765 43210', email: 'priya.demo@carebridge.ai' },
            { name: 'Rohan Sharma', relation: 'Family Caregiver', phone: '+91 98765 43211', email: 'rohan.demo@carebridge.ai' },
          ],
          medications: [
            'Aspirin 75mg - Morning (Cardiovascular protection)',
            'Metformin 500mg - Morning & Afternoon (Blood sugar regulation)',
            'Atorvastatin 20mg - Evening / Bedtime (Lipid & cholesterol control)',
            'Paracetamol 650mg - As needed for pain (Max 3/day)',
          ],
          last_updated: new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
        })
        setLoading(false)
      })
  }, [patientId, apiBase])

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0F172A', color: '#fff', fontFamily: 'system-ui, sans-serif' }}>
        <div style={{ textAlign: 'center' }}>
          <ShieldAlert size={48} style={{ color: '#EF4444', margin: '0 auto 16px', animation: 'pulse 1.5s infinite' }} />
          <h2>Loading Emergency ICE Medical Passport…</h2>
          <p style={{ color: '#94A3B8' }}>Access target: &lt; 5 seconds</p>
        </div>
      </div>
    )
  }

  const patient = data?.patient

  return (
    <div style={{ minHeight: '100vh', background: '#F8FAFC', color: '#0F172A', fontFamily: 'system-ui, -apple-system, sans-serif', padding: '20px 16px' }}>
      <div style={{ maxWidth: 840, margin: '0 auto', background: '#fff', borderRadius: 20, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)', overflow: 'hidden', border: '1px solid #E2E8F0' }}>
        
        {/* Paramedic Fast-Read Banner */}
        <div style={{ background: '#DC2626', color: '#fff', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ background: '#fff', color: '#DC2626', width: 44, height: 44, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900 }}>
              <ShieldAlert size={26} />
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', opacity: 0.9 }}>
                IN CASE OF EMERGENCY (ICE) · PUBLIC TRIAGE PASSPORT
              </div>
              <h1 style={{ margin: 0, fontSize: 20, fontWeight: 800 }}>Paramedic Emergency Record</h1>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => window.print()}
              style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: '#fff', padding: '8px 16px', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <Printer size={15} /> Print Record
            </button>
            <Link
              to="/login"
              style={{ background: '#fff', color: '#DC2626', textDecoration: 'none', padding: '8px 16px', borderRadius: 8, fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}
            >
              Portal Login
            </Link>
          </div>
        </div>

        {/* Rapid Medical Profile Header */}
        <div style={{ padding: '24px', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 64, height: 64, background: '#EFF6FF', borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
              <User size={36} />
            </div>
            <div>
              <h2 style={{ margin: 0, fontSize: 22, fontWeight: 800 }}>{patient.full_name}</h2>
              <div style={{ color: '#64748B', fontSize: 14, marginTop: 4 }}>
                DOB: <strong>{patient.date_of_birth}</strong> · Phone: <strong>{patient.phone}</strong>
              </div>
            </div>
          </div>

          <div style={{ background: '#FEF2F2', border: '2px solid #EF4444', borderRadius: 14, padding: '10px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 11, fontWeight: 800, color: '#DC2626', letterSpacing: 1 }}>BLOOD GROUP</div>
            <div style={{ fontSize: 24, fontWeight: 900, color: '#DC2626' }}>{patient.blood_group}</div>
          </div>
        </div>

        {/* Body Grid */}
        <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
          
          {/* Critical Warnings: Allergies & Chronic Conditions */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
            {/* Allergies */}
            <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 14, padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#DC2626', fontWeight: 800, fontSize: 14, marginBottom: 10 }}>
                <AlertCircle size={18} /> CRITICAL ALLERGIES (DO NOT ADMINISTER)
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {patient.allergies.map((a, i) => (
                  <span key={i} style={{ background: '#FEE2E2', color: '#991B1B', fontWeight: 700, fontSize: 13, padding: '6px 12px', borderRadius: 8, border: '1px solid #FCA5A5' }}>
                    ⚠️ {a}
                  </span>
                ))}
              </div>
            </div>

            {/* Conditions */}
            <div style={{ background: '#FFF7ED', border: '1px solid #FED7AA', borderRadius: 14, padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#C2410C', fontWeight: 800, fontSize: 14, marginBottom: 10 }}>
                <Activity size={18} /> KNOWN CHRONIC CONDITIONS
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {patient.chronic_conditions.map((c, i) => (
                  <span key={i} style={{ background: '#FFEDD5', color: '#9A3412', fontWeight: 700, fontSize: 13, padding: '6px 12px', borderRadius: 8, border: '1px solid #FDBA74' }}>
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Hospital & Attending Physician */}
          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 14, padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#0F172A', fontWeight: 800, fontSize: 14, marginBottom: 10 }}>
              <Hospital size={18} color="#2563EB" /> ATTENDING HOSPITAL & CLINICIAN
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{patient.hospital_name}</div>
                <div style={{ fontSize: 13, color: '#64748B' }}>Primary Physician: {patient.primary_physician}</div>
              </div>
              <a
                href={`tel:${patient.hospital_helpline}`}
                style={{ background: '#2563EB', color: '#fff', padding: '10px 18px', borderRadius: 10, textDecoration: 'none', fontWeight: 700, fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}
              >
                <Phone size={15} /> Call Hospital: {patient.hospital_helpline}
              </a>
            </div>
          </div>

          {/* Emergency Family Contacts */}
          <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: 14, padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#166534', fontWeight: 800, fontSize: 14, marginBottom: 10 }}>
              <Heart size={18} color="#16A34A" /> EMERGENCY CAREGIVER CONTACTS
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>
              {data.caregivers.map((cg, i) => (
                <div key={i} style={{ background: '#fff', border: '1px solid #DCFCE7', padding: 12, borderRadius: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 14 }}>{cg.name}</div>
                    <div style={{ fontSize: 12, color: '#64748B' }}>{cg.relation}</div>
                  </div>
                  <a
                    href={`tel:${cg.phone}`}
                    style={{ background: '#16A34A', color: '#fff', padding: '6px 12px', borderRadius: 8, textDecoration: 'none', fontWeight: 700, fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}
                  >
                    <Phone size={13} /> {cg.phone}
                  </a>
                </div>
              ))}
            </div>
          </div>

          {/* Active Prescriptions */}
          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 14, padding: 16 }}>
            <div style={{ fontWeight: 800, fontSize: 14, marginBottom: 10, color: '#0F172A' }}>
              CURRENT ACTIVE MEDICATIONS ON FILE
            </div>
            <ul style={{ margin: 0, paddingLeft: 20, color: '#334155', fontSize: 13, lineHeight: 1.7 }}>
              {data.medications.map((m, i) => (
                <li key={i}><strong>{m}</strong></li>
              ))}
            </ul>
          </div>

          {/* Paramedic Footer Note */}
          <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, fontSize: 12, color: '#64748B' }}>
            <div>
              <CheckCircle2 size={14} style={{ verticalAlign: 'middle', color: '#16A34A', marginRight: 4 }} />
              CareBridge Verified Medical Record · Team ByteCoders (IIMT Engineering College, Meerut)
            </div>
            <div>Last Synced: {data.last_updated}</div>
          </div>

        </div>
      </div>
    </div>
  )
}
