import { useEffect, useRef, useState } from 'react'
import { AlertTriangle, Check, CheckCircle2, FileText, FileUp, Image as ImageIcon, LoaderCircle, Plus, ShieldCheck, Sparkles, Upload, X } from 'lucide-react'
import api, { errorMessage } from '../api'
import { Card, EmptyState, Loading, Notice, PageHeading, StatusBadge } from '../components/UI'

export default function Documents() {
  const inputRef = useRef(null)
  const [docs, setDocs] = useState(null)
  const [selected, setSelected] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [objectUrl, setObjectUrl] = useState('')
  const [selectedTasks, setSelectedTasks] = useState({})
  const [editedTasks, setEditedTasks] = useState({})
  const [confirmed, setConfirmed] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [consented, setConsented] = useState(false)

  async function loadDocs(preferredId) {
    const { data } = await api.get('/documents')
    setDocs(data)
    const id = preferredId || selected?.id || data[0]?.id
    if (id) await selectDocument(id)
    else setSelected(null)
  }
  async function selectDocument(id) {
    setError(''); setConfirmed(false); setSelectedTasks({}); setEditedTasks({}); setConsented(false)
    try {
      const { data } = await api.get(`/documents/${id}`)
      setSelected(data)
    } catch (e) { setError(errorMessage(e)) }
  }
  useEffect(() => { loadDocs().catch((e) => setError(errorMessage(e))) }, [])
  useEffect(() => {
    let active = true
    let previewUrl = ''
    if (!selected?.id) { setObjectUrl(''); return }
    api.get(`/documents/${selected.id}/preview`, { responseType: 'blob' }).then(({ data }) => {
      if (active) { previewUrl = URL.createObjectURL(data); setObjectUrl(previewUrl) }
    }).catch(() => { if (active) setObjectUrl('') })
    return () => { active = false; if (previewUrl) URL.revokeObjectURL(previewUrl) }
  }, [selected?.id])

  async function upload(file) {
    if (!file) return
    setError(''); setUploading(true); setProgress(0)
    const form = new FormData(); form.append('file', file)
    try {
      const { data } = await api.post('/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: (e) => setProgress(Math.round(e.loaded / (e.total || file.size) * 100)) })
      await loadDocs(data.id)
    } catch (e) { setError(errorMessage(e)) } finally { setUploading(false); setProgress(0); if (inputRef.current) inputRef.current.value = '' }
  }
  async function analyze() {
    if (!selected) return
    setAnalyzing(true); setError('')
    try { const { data } = await api.post(`/documents/${selected.id}/analyze`, { consent: true }); setSelected((old) => ({ ...old, ...data, analysis_mode: data.analysis_mode, analyzed: true }))
      const defaults = {}; (data.analysis?.clinician_tasks || []).forEach((_, index) => { defaults[index] = true }); setSelectedTasks(defaults)
    } catch (e) { setError(errorMessage(e)) } finally { setAnalyzing(false) }
  }
  async function confirmTasks() {
    setConfirming(true); setError('')
    const tasks = (selected.analysis?.clinician_tasks || []).map((task, index) => ({ task, index })).filter(({ index }) => selectedTasks[index]).map(({ task, index }) => ({ ...task, ...editedTasks[index], source_text: task.source_text }))
    try { await api.post(`/documents/${selected.id}/confirm`, { confirmed: true, tasks }); setConfirmed(true); await loadDocs(selected.id) }
    catch (e) { setError(errorMessage(e)) } finally { setConfirming(false) }
  }
  if (!docs) return <Loading />
  const analysis = selected?.analysis
  const suggested = analysis?.clinician_tasks || []
  const previewType = selected?.content_type || ''

  return <div><PageHeading eyebrow="YOUR HEALTH DOCUMENTS" title="Documents" description="Keep discharge paperwork and care documents together. Review extracted details before creating journey tasks." action={<button className="button button-primary" onClick={() => inputRef.current?.click()} disabled={uploading}><Upload size={16} /> Upload document</button>} />
    {error && <div className="form-error"><AlertTriangle size={16} />{error}</div>}
    <input ref={inputRef} hidden type="file" accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" onChange={(e) => upload(e.target.files?.[0])} />
    {uploading && <div className="upload-progress"><div className="upload-progress-head"><span><LoaderCircle size={16} className="spin" /> Uploading securely…</span><strong>{progress}%</strong></div><div className="progress-track"><i style={{ width: `${progress}%` }} /></div></div>}
    <div className="documents-layout">
      <Card className="document-library"><div className="library-head"><div><h2>Document library</h2><span>{docs.length} file{docs.length === 1 ? '' : 's'}</span></div><button className="icon-link" onClick={() => inputRef.current?.click()} aria-label="Upload"><Plus size={18} /></button></div>
        {docs.length ? <div className="document-items">{docs.map((doc) => <button key={doc.id} onClick={() => selectDocument(doc.id)} className={`document-list-item ${selected?.id === doc.id ? 'selected' : ''}`}><span className="file-type-icon"><FileText size={18} /></span><span className="document-list-copy"><strong>{doc.filename}</strong><small>{doc.document_type || doc.content_type} · {new Date(doc.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</small></span><span className="document-state">{doc.confirmed ? <CheckCircle2 size={16} /> : doc.analyzed ? <Sparkles size={15} /> : <span />}</span></button>)}</div> : <EmptyState icon={FileUp} title="No documents yet" detail="Upload a PDF or image of your care paperwork." />}
        <button className="upload-drop" onClick={() => inputRef.current?.click()} onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files?.[0]) }}><span><Upload size={18} /></span><strong>Upload a document</strong><small>PDF, JPG or PNG · up to 10 MB</small></button>
      </Card>
      {selected ? <div className="document-review"><div className="document-review-head"><div><div className="eyebrow">DOCUMENT REVIEW</div><h2>{selected.filename}</h2></div>{selected.analysis_mode === 'simulated' && <span className="simulated-tag">SIMULATED</span>}</div>
        {selected.analysis_mode === 'simulated' && <Notice>Demo mode is active. This result is simulated; no AI medical analysis was performed.</Notice>}
        <div className="document-split"><Card className="original-preview"><div className="subcard-head"><strong>Original document</strong><span>Private to your account</span></div>{objectUrl && previewType.startsWith('image/') ? <img className="document-image-preview" src={objectUrl} alt="Uploaded original document" /> : objectUrl && previewType === 'application/pdf' ? <iframe title="Original uploaded PDF" src={objectUrl} /> : objectUrl ? <pre className="document-text-preview">{selected.extracted_text}</pre> : <div className="preview-placeholder"><FileText size={28} /><span>Preview unavailable</span></div>}</Card>
          <Card className="extracted-panel"><div className="subcard-head"><strong>Extracted information</strong>{selected.analyzed && <StatusBadge status={selected.confirmed ? 'Completed' : 'Needs Verification'} />}</div>
            {!selected.analyzed ? <div className="analyze-prompt"><div className="analyze-icon"><Sparkles size={20} /></div><h3>Review this document</h3><p>Extracted text and a simple-language draft will appear here. You’ll review the results before adding any tasks.</p><label className="analysis-consent"><input type="checkbox" checked={consented} onChange={(event) => setConsented(event.target.checked)} /><span>I consent to document processing for this organizational draft. When an AI provider is configured, extracted text and the uploaded image may be sent to it.</span></label><button className="button button-primary" onClick={analyze} disabled={analyzing || !consented}>{analyzing ? <><LoaderCircle className="spin" size={16} /> Analyzing…</> : <><Sparkles size={16} /> Start analysis</>}</button></div> : <div className="analysis-content">
              <div className="analysis-summary"><span>Simple-language explanation</span><p>{selected.explanation || analysis?.simple_explanation || 'No explanation available.'}</p></div>
              <div className="extracted-fields"><InfoField label="Document type" value={analysis?.document_type || selected.document_type} /><InfoField label="Document date" value={analysis?.document_date || selected.document_date} /><InfoField label="Hospital" value={analysis?.hospital_name || selected.hospital_name} /></div>
              {analysis?.uncertain_fields?.length > 0 && <div className="uncertainty-box"><AlertTriangle size={15} /><span>Verify: {analysis.uncertain_fields.join(', ')}</span></div>}
              {analysis?.medication_information?.length > 0 && <div className="analysis-list"><strong>Medication information, as written</strong>{analysis.medication_information.map((x, i) => <p key={i}>• {x}</p>)}</div>}
              <div className="source-extract"><strong>Extracted text</strong><pre>{selected.extracted_text}</pre></div>
            </div>}
          </Card></div>
        {selected.analyzed && <Card className="suggested-tasks"><div className="suggested-head"><div><div className="eyebrow">HUMAN REVIEW REQUIRED</div><h3>Suggested journey tasks</h3></div><span className="verification-chip"><ShieldCheck size={14} /> Verify before saving</span></div>
          {suggested.length ? <div className="suggestion-list">{suggested.map((task, i) => <div className="suggestion-row" key={i}><input aria-label={`Include ${task.title}`} type="checkbox" checked={Boolean(selectedTasks[i])} onChange={(e) => setSelectedTasks({ ...selectedTasks, [i]: e.target.checked })} /><span><input className="suggestion-edit" aria-label="Edit suggested task title" value={editedTasks[i]?.title ?? task.title} onChange={(e) => setEditedTasks({ ...editedTasks, [i]: { ...editedTasks[i], title: e.target.value } })} /><textarea className="suggestion-edit-description" aria-label="Edit suggested task details" rows="2" value={editedTasks[i]?.description ?? task.description} onChange={(e) => setEditedTasks({ ...editedTasks, [i]: { ...editedTasks[i], description: e.target.value } })} /><em>Original source: “{task.source_text}”</em></span><StatusBadge status="Needs Verification" /></div>)}</div> : <div className="no-suggestions">No tasks were generated. You can still confirm the extracted information, then add verified steps from your journey page.</div>}
          {selected.confirmed || confirmed ? <Notice tone="success">Document review confirmed. Any saved tasks still need clinician verification.</Notice> : <div className="confirm-row"><label className="confirm-check"><input type="checkbox" checked={confirmed || Boolean(selectedTasks.__ack)} onChange={(e) => setSelectedTasks({ ...selectedTasks, __ack: e.target.checked })} /><span>I reviewed this draft against my original document.</span></label><button className="button button-primary" disabled={confirming || !selectedTasks.__ack} onClick={confirmTasks}>{confirming ? 'Saving…' : 'Confirm review'}<Check size={16} /></button></div>}
        </Card>}
      </div> : <Card className="no-document-selected"><EmptyState icon={ImageIcon} title="Select a document to review" detail="Choose a document from your library, or upload a new file." /></Card>}
    </div>
    <div className="safety-footnote">Extracted content is a draft. CareBridge AI does not modify treatment instructions or replace your clinician’s guidance.</div>
  </div>
}

function InfoField({ label, value }) { return <div><small>{label}</small><strong>{value || 'Not found'}</strong></div> }
