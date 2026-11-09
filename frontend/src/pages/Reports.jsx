import { useEffect, useState } from 'react'
import { AlertCircle, Check, FileCheck2, FilePlus2, FileText, Plus, ShieldCheck, Upload, Sparkles, X, Languages, HelpCircle } from 'lucide-react'
import api, { errorMessage } from '../api'
import { useAuth } from '../auth'
import { Card, EmptyState, Loading, Notice, PageHeading, StatusBadge } from '../components/UI'

export default function Reports() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [docs, setDocs] = useState([])
  const [error, setError] = useState('')
  const [newName, setNewName] = useState('')
  const [adding, setAdding] = useState(false)
  const [busyId, setBusyId] = useState(null)
  const [explainingReport, setExplainingReport] = useState(null)

  async function load() {
    const requests = [api.get('/reports/readiness')]
    if (user?.role === 'patient') requests.push(api.get('/documents'))
    const [readiness, documents] = await Promise.all(requests)
    setData(readiness.data)
    setDocs(documents?.data || [])
  }

  useEffect(() => { load().catch((e) => setError(errorMessage(e))) }, [])

  async function update(report, documentId) {
    setBusyId(report.id)
    setError('')
    try {
      const updateData = documentId
        ? { status: 'Verified', document_id: Number(documentId) }
        : { status: 'Missing' }
      await api.patch(`/reports/${report.id}`, updateData)
      await load()
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setBusyId(null)
    }
  }

  async function addReport(event) {
    event.preventDefault()
    if (!newName.trim()) return
    setAdding(true)
    setError('')
    try {
      await api.post('/reports', { name: newName.trim(), status: 'Missing' })
      setNewName('')
      await load()
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setAdding(false)
    }
  }

  if (!data) return error ? <div className="form-error">{error}</div> : <Loading />

  return <div>
    <PageHeading eyebrow="APPOINTMENT DOCUMENTS" title="Report Readiness & Biomarker Explainer" description="Track requested diagnostic reports, verify availability, and translate complex clinical biomarkers into plain language." />
    {error && <div className="form-error">{error}</div>}
    <Notice>This checklist tracks administrative document availability only. It does not assess medical readiness for treatment.</Notice>

    <div className="readiness-overview">
      <Card className="readiness-score">
        <div className="readiness-score-copy">
          <div className="eyebrow">DOCUMENT AVAILABILITY</div>
          <h2>{data.readiness_percentage}% <span>ready</span></h2>
          <p>{data.available_count} of {data.total_count} required documents are marked verified.</p>
          <div className="readiness-track"><i style={{ width: `${data.readiness_percentage}%` }} /></div>
          <small>{data.total_count - data.available_count} document{data.total_count - data.available_count === 1 ? '' : 's'} still need attention</small>
        </div>
        <div className="readiness-graphic"><div className="readiness-ring"><span><FileCheck2 size={25} /></span></div></div>
      </Card>
      <Card className="readiness-note">
        <span className="secure-note-icon"><Sparkles size={21} color="#2563EB" /></span>
        <h3>Plain-Language AI Explainer</h3>
        <p>Confused by dense medical jargon, lab biomarkers, or fasting values? Tap <strong>Explain Report</strong> on any item to get clear, reassuring bilingual guidance.</p>
        <span className="secure-note-foot"><AlertCircle size={14} /> Reassuring guidance · Not autonomous diagnosis</span>
      </Card>
    </div>

    <Card className="report-checklist-card">
      <div className="card-head">
        <div><div className="eyebrow">REQUIRED DOCUMENTS</div><h2>Checklist</h2></div>
        {user?.role === 'patient' && <span className="checklist-count">{data.total_count} items</span>}
      </div>
      {data.reports.length > 0
        ? <div className="report-checklist">
            {data.reports.map((report) => (
              <ReportRow
                key={report.id}
                report={report}
                docs={docs}
                patient={user?.role === 'patient'}
                busy={busyId === report.id}
                onUpdate={update}
                onExplain={() => setExplainingReport(report.name)}
              />
            ))}
          </div>
        : <EmptyState icon={FileCheck2} title="No documents required yet" detail="Add a checklist item when your care team requests a document." />}
    </Card>

    {user?.role === 'patient' && <Card className="add-report-card">
      <div><div className="eyebrow">KEEP THE LIST CURRENT</div><h3>Add a required document</h3><p>Add a report or document your care team asked you to bring.</p></div>
      <form onSubmit={addReport}><input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="e.g. Previous diagnostic report" required /><button className="button button-secondary" disabled={adding}><Plus size={15} /> Add item</button></form>
    </Card>}

    {user?.role === 'patient' && <div className="upload-nudge">
      <span><FilePlus2 size={19} /></span>
      <div><strong>Need to add a missing report?</strong><small>Upload it from Documents, then attach it to the matching checklist item.</small></div>
      <a href="/documents" className="button button-outline button-small">Go to documents <Upload size={14} /></a>
    </div>}

    {/* Plain-Language Explainer Modal */}
    {explainingReport && (
      <ReportExplainerModal
        reportName={explainingReport}
        onClose={() => setExplainingReport(null)}
      />
    )}
  </div>
}

function ReportRow({ report, docs, patient, busy, onUpdate, onExplain }) {
  const statusClass = report.status.toLowerCase().replaceAll(' ', '-')
  const dateText = report.appointment_date
    ? `For appointment - ${new Date(`${report.appointment_date}T12:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}`
    : 'No appointment date linked'
  const isVerified = report.status === 'Verified'

  return <div className="report-check-row" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
    <div className={`report-doc-icon report-${statusClass}`}><FileText size={18} /></div>
    <div className="report-doc-copy" style={{ flex: 1 }}><strong>{report.name}</strong><span>{dateText}</span></div>
    
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <button
        type="button"
        className="button button-small button-outline"
        style={{ borderColor: '#93C5FD', color: '#1D4ED8', background: '#EFF6FF', display: 'flex', alignItems: 'center', gap: 4 }}
        onClick={onExplain}
        title="Translate complex lab biomarkers into plain language"
      >
        <Sparkles size={13} color="#2563EB" /> Explain
      </button>

      <StatusBadge status={report.status} />
    </div>

    {patient && <div className="report-action">
      {isVerified
        ? <span className="completed-check"><Check size={16} /> Verified</span>
        : <select aria-label={`Attach document for ${report.name}`} value="" disabled={busy} onChange={(event) => onUpdate(report, event.target.value)}>
            <option value="">Attach document...</option>
            {docs.map((doc) => <option value={doc.id} key={doc.id}>{doc.filename}</option>)}
          </select>}
    </div>}
  </div>
}

function ReportExplainerModal({ reportName, onClose }) {
  const [lang, setLang] = useState('en')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    api.post('/copilot/explain-report', { report_name: reportName, language: lang })
      .then((res) => {
        setData(res.data)
        setLoading(false)
      })
      .catch((err) => {
        setError(errorMessage(err))
        setLoading(false)
      })
  }, [reportName, lang])

  return (
    <div className="modal-backdrop" onClick={onClose} style={{ zIndex: 1100 }}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 640, width: '92%' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E2E8F0', paddingBottom: 14, marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ background: '#EFF6FF', color: '#2563EB', padding: 8, borderRadius: 10 }}>
              <Sparkles size={20} />
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 800, color: '#2563EB', textTransform: 'uppercase', letterSpacing: 0.8 }}>
                AI BIOMARKER & REPORT EXPLAINER
              </div>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800 }}>{reportName}</h3>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {/* Language Switcher */}
            <div style={{ display: 'flex', background: '#F1F5F9', padding: 3, borderRadius: 8 }}>
              <button
                type="button"
                onClick={() => setLang('en')}
                style={{
                  border: 'none',
                  padding: '4px 10px',
                  borderRadius: 6,
                  fontSize: 12,
                  fontWeight: 700,
                  cursor: 'pointer',
                  background: lang === 'en' ? '#fff' : 'transparent',
                  color: lang === 'en' ? '#0F172A' : '#64748B',
                  boxShadow: lang === 'en' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                }}
              >
                English
              </button>
              <button
                type="button"
                onClick={() => setLang('hi')}
                style={{
                  border: 'none',
                  padding: '4px 10px',
                  borderRadius: 6,
                  fontSize: 12,
                  fontWeight: 700,
                  cursor: 'pointer',
                  background: lang === 'hi' ? '#fff' : 'transparent',
                  color: lang === 'hi' ? '#0F172A' : '#64748B',
                  boxShadow: lang === 'hi' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                }}
              >
                हिंदी
              </button>
            </div>

            <button type="button" onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748B' }}>
              <X size={20} />
            </button>
          </div>
        </div>

        {error && <div className="form-error">{error}</div>}

        {loading ? (
          <div style={{ padding: '30px 0', textAlign: 'center', color: '#64748B' }}>
            <Sparkles size={32} style={{ color: '#2563EB', margin: '0 auto 12px', animation: 'spin 2s linear infinite' }} />
            <p>Simplifying medical biomarkers into plain language…</p>
          </div>
        ) : data ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Plain Summary */}
            <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', padding: '14px 16px', borderRadius: 12 }}>
              <div style={{ fontWeight: 800, fontSize: 13, color: '#1E40AF', marginBottom: 4 }}>
                {lang === 'hi' ? '💡 यह टेस्ट क्या जांचता है?' : '💡 What This Test Measures:'}
              </div>
              <p style={{ margin: 0, fontSize: 13.5, color: '#1E3A8A', lineHeight: 1.5 }}>
                {data.plain_summary}
              </p>
            </div>

            {/* Biomarkers Table */}
            <div>
              <div style={{ fontWeight: 800, fontSize: 13, color: '#0F172A', marginBottom: 8 }}>
                {lang === 'hi' ? 'प्रमुख बायोमार्कर्स और सामान्य सीमा:' : 'Key Biomarkers & Expected Ranges:'}
              </div>
              <div style={{ border: '1px solid #E2E8F0', borderRadius: 10, overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
                  <thead>
                    <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', textAlign: 'left', color: '#475569' }}>
                      <th style={{ padding: '8px 12px' }}>{lang === 'hi' ? 'बायोमार्कर' : 'Biomarker'}</th>
                      <th style={{ padding: '8px 12px' }}>{lang === 'hi' ? 'सामान्य सीमा' : 'Normal Reference'}</th>
                      <th style={{ padding: '8px 12px' }}>{lang === 'hi' ? 'मरीज के लिए अर्थ' : 'Clinical Meaning'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.biomarkers.map((b, i) => (
                      <tr key={i} style={{ borderBottom: i < data.biomarkers.length - 1 ? '1px solid #F1F5F9' : 'none' }}>
                        <td style={{ padding: '8px 12px', fontWeight: 700, color: '#0F172A' }}>{b.name}</td>
                        <td style={{ padding: '8px 12px', color: '#2563EB', fontWeight: 600 }}>{b.range}</td>
                        <td style={{ padding: '8px 12px', color: '#475569' }}>{b.meaning}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Practical Guidance */}
            <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', padding: '12px 16px', borderRadius: 12 }}>
              <div style={{ fontWeight: 800, fontSize: 13, color: '#166534', marginBottom: 4 }}>
                {lang === 'hi' ? '🩺 मरीज के लिए व्यावहारिक सलाह:' : '🩺 Practical Patient Next Steps:'}
              </div>
              <p style={{ margin: 0, fontSize: 13, color: '#14532D', lineHeight: 1.5 }}>
                {data.reassuring_guidance}
              </p>
            </div>

            <div style={{ fontSize: 11, color: '#94A3B8', borderTop: '1px solid #F1F5F9', paddingTop: 10, textAlign: 'center' }}>
              {data.safety_disclaimer}
            </div>
          </div>
        ) : null}

        <div style={{ marginTop: 20, textAlign: 'right' }}>
          <button type="button" className="button button-primary" onClick={onClose}>
            {lang === 'hi' ? 'समझ गया' : 'Got it, Close'}
          </button>
        </div>

      </div>
    </div>
  )
}
