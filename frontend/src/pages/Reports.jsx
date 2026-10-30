import { useEffect, useState } from 'react'
import { AlertCircle, Check, FileCheck2, FilePlus2, FileText, Plus, ShieldCheck, Upload } from 'lucide-react'
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
    <PageHeading eyebrow="APPOINTMENT DOCUMENTS" title="Report Readiness" description="Check whether the requested documents are available for your upcoming appointments." />
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
        <span className="secure-note-icon"><ShieldCheck size={21} /></span>
        <h3>Keep documents in one place</h3>
        <p>Attach an uploaded report to the checklist when it is available. Your care team can verify its contents.</p>
        <span className="secure-note-foot"><AlertCircle size={14} /> Availability is not clinical approval</span>
      </Card>
    </div>

    <Card className="report-checklist-card">
      <div className="card-head">
        <div><div className="eyebrow">REQUIRED DOCUMENTS</div><h2>Checklist</h2></div>
        {user?.role === 'patient' && <span className="checklist-count">{data.total_count} items</span>}
      </div>
      {data.reports.length > 0
        ? <div className="report-checklist">{data.reports.map((report) => <ReportRow key={report.id} report={report} docs={docs} patient={user?.role === 'patient'} busy={busyId === report.id} onUpdate={update} />)}</div>
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
  </div>
}

function ReportRow({ report, docs, patient, busy, onUpdate }) {
  const statusClass = report.status.toLowerCase().replaceAll(' ', '-')
  const dateText = report.appointment_date
    ? `For appointment - ${new Date(`${report.appointment_date}T12:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}`
    : 'No appointment date linked'
  const isVerified = report.status === 'Verified'

  return <div className="report-check-row">
    <div className={`report-doc-icon report-${statusClass}`}><FileText size={18} /></div>
    <div className="report-doc-copy"><strong>{report.name}</strong><span>{dateText}</span></div>
    <StatusBadge status={report.status} />
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
