import { useEffect, useRef, useState } from 'react'
import {
  AlertTriangle, Check, CheckCircle2, Copy, Download, ExternalLink,
  Eye, FileText, FileUp, Filter, Image as ImageIcon, LoaderCircle, Maximize2,
  Minimize2, Plus, RotateCcw, Search, ShieldCheck, Sparkles, Trash2, Upload, X, ZoomIn, ZoomOut
} from 'lucide-react'
import api, { errorMessage } from '../api'
import { Card, EmptyState, Loading, Notice, PageHeading, StatusBadge } from '../components/UI'

const CATEGORIES = [
  'Discharge Summary',
  'Lab Report',
  'Prescription',
  'Radiology / Scan',
  'Insurance / Bill',
  'Other'
]

function formatFileSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function Documents() {
  const inputRef = useRef(null)
  const [docs, setDocs] = useState(null)
  const [selected, setSelected] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [objectUrl, setObjectUrl] = useState('')
  const [selectedTasks, setSelectedTasks] = useState({})
  const [editedTasks, setEditedTasks] = useState({})
  const [confirmed, setConfirmed] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [consented, setConsented] = useState(false)
  const [search, setSearch] = useState('')
  const [libraryFilter, setLibraryFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [dragging, setDragging] = useState(false)

  // Staged files for pre-upload review
  const [stagedFiles, setStagedFiles] = useState([])
  const [stagedCategory, setStagedCategory] = useState('Discharge Summary')

  // Lightbox / Fullscreen Modal
  const [fullscreenOpen, setFullscreenOpen] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [copiedText, setCopiedText] = useState(false)
  const [showRawText, setShowRawText] = useState(false)

  async function loadDocs(preferredId) {
    const { data } = await api.get('/documents')
    setDocs(data)
    const id = preferredId || selected?.id || data[0]?.id
    if (id) await selectDocument(id)
    else setSelected(null)
  }

  async function selectDocument(id) {
    setError('')
    setSuccessMsg('')
    setConfirmed(false)
    setSelectedTasks({})
    setEditedTasks({})
    setConsented(false)
    setZoomLevel(1)
    try {
      const { data } = await api.get(`/documents/${id}`)
      setSelected(data)
    } catch (e) {
      setError(errorMessage(e))
    }
  }

  useEffect(() => {
    loadDocs().catch((e) => setError(errorMessage(e)))
  }, [])

  useEffect(() => {
    let active = true
    let previewUrl = ''
    if (!selected?.id) {
      setObjectUrl('')
      return
    }
    api.get(`/documents/${selected.id}/preview`, { responseType: 'blob' })
      .then(({ data }) => {
        if (active) {
          previewUrl = URL.createObjectURL(data)
          setObjectUrl(previewUrl)
        }
      })
      .catch(() => {
        if (active) setObjectUrl('')
      })
    return () => {
      active = false
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [selected?.id])

  // Handle file staging when user selects or drops files
  function handleFilesSelected(files) {
    const fileList = Array.from(files || [])
    if (!fileList.length) return
    const allowed = /\.(pdf|jpe?g|png)$/i
    const invalid = fileList.find((file) => !allowed.test(file.name) || file.size > 10 * 1024 * 1024)
    if (invalid) {
      setError(`${invalid.name}: Please choose a valid PDF, JPG, or PNG file up to 10 MB.`)
      if (inputRef.current) inputRef.current.value = ''
      return
    }
    setError('')
    setStagedFiles((prev) => [...prev, ...fileList])
    if (inputRef.current) inputRef.current.value = ''
  }

  function removeStagedFile(index) {
    setStagedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  async function executeUpload() {
    if (!stagedFiles.length) return
    setError('')
    setUploading(true)
    setProgress(0)
    try {
      let lastId
      for (let i = 0; i < stagedFiles.length; i++) {
        const file = stagedFiles[i]
        const form = new FormData()
        form.append('file', file)
        const { data } = await api.post('/documents/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (e) => {
            const filePct = Math.round((e.loaded / (e.total || file.size)) * 100)
            const overall = Math.round(((i + filePct / 100) / stagedFiles.length) * 100)
            setProgress(overall)
          }
        })
        lastId = data.id
      }
      setStagedFiles([])
      setSuccessMsg(`Successfully uploaded ${stagedFiles.length} document${stagedFiles.length > 1 ? 's' : ''}!`)
      setTimeout(() => setSuccessMsg(''), 4000)
      await loadDocs(lastId)
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  async function deleteCurrentDocument(docId) {
    const idToDelete = docId || selected?.id
    if (!idToDelete) return
    if (!window.confirm('Are you sure you want to delete this document? Any associated review draft will also be removed.')) {
      return
    }
    setError('')
    try {
      await api.delete(`/documents/${idToDelete}`)
      setSuccessMsg('Document deleted successfully.')
      setTimeout(() => setSuccessMsg(''), 4000)
      if (selected?.id === idToDelete) {
        setSelected(null)
      }
      await loadDocs()
    } catch (e) {
      setError(errorMessage(e))
    }
  }

  async function analyze() {
    if (!selected) return
    setAnalyzing(true)
    setError('')
    try {
      const { data } = await api.post(`/documents/${selected.id}/analyze`, { consent: true })
      setSelected((old) => ({
        ...old,
        ...data,
        analysis_mode: data.analysis_mode,
        analyzed: true
      }))
      const defaults = {}
      ;(data.analysis?.clinician_tasks || []).forEach((_, index) => {
        defaults[index] = true
      })
      setSelectedTasks(defaults)
      setSuccessMsg('Analysis completed. Please verify the suggested recovery steps below.')
      setTimeout(() => setSuccessMsg(''), 5000)
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setAnalyzing(false)
    }
  }

  async function confirmTasks() {
    setConfirming(true)
    setError('')
    const tasks = (selected.analysis?.clinician_tasks || [])
      .map((task, index) => ({ task, index }))
      .filter(({ index }) => selectedTasks[index])
      .map(({ task, index }) => ({
        ...task,
        ...editedTasks[index],
        source_text: task.source_text
      }))
    try {
      await api.post(`/documents/${selected.id}/confirm`, { confirmed: true, tasks })
      setConfirmed(true)
      setSuccessMsg(`Document confirmed! ${tasks.length} task${tasks.length === 1 ? '' : 's'} added to your healthcare journey.`)
      setTimeout(() => setSuccessMsg(''), 6000)
      await loadDocs(selected.id)
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setConfirming(false)
    }
  }

  function copyExtracted() {
    if (!selected?.extracted_text) return
    navigator.clipboard.writeText(selected.extracted_text)
    setCopiedText(true)
    setTimeout(() => setCopiedText(false), 2500)
  }

  function toggleAllTasks(check) {
    const next = {}
    ;(selected?.analysis?.clinician_tasks || []).forEach((_, i) => {
      next[i] = check
    })
    next.__ack = selectedTasks.__ack
    setSelectedTasks(next)
  }

  if (!docs) return <Loading />

  const analysis = selected?.analysis
  const suggested = analysis?.clinician_tasks || []
  const previewType = selected?.content_type || ''

  // Filter docs by search, status, and document type
  const visibleDocs = docs.filter((doc) => {
    const matchesSearch = `${doc.filename} ${doc.document_type || ''} ${doc.content_type || ''}`
      .toLowerCase()
      .includes(search.toLowerCase())
    const matchesStatus =
      libraryFilter === 'all' ||
      (libraryFilter === 'review' ? !doc.confirmed : Boolean(doc.confirmed))
    const matchesType =
      typeFilter === 'all' ||
      (doc.document_type || '').toLowerCase().includes(typeFilter.toLowerCase())
    return matchesSearch && matchesStatus && matchesType
  })

  const allTasksSelected =
    suggested.length > 0 && suggested.every((_, i) => selectedTasks[i])

  return (
    <div className="documents-page-root">
      <PageHeading
        eyebrow="YOUR HEALTH RECORDS & PAPERWORK"
        title="Medical Documents"
        description="Securely store hospital discharge summaries, diagnostic reports, and prescriptions. Review AI-extracted instructions before adding verified steps to your recovery journey."
        action={
          <button
            className="button button-primary doc-upload-trigger"
            onClick={() => inputRef.current?.click()}
            disabled={uploading}
          >
            <Upload size={18} />
            <span>Upload Documents</span>
          </button>
        }
      />

      {error && (
        <div className="doc-alert doc-alert-error">
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="doc-alert doc-alert-success">
          <CheckCircle2 size={20} />
          <span>{successMsg}</span>
        </div>
      )}

      <input
        ref={inputRef}
        hidden
        type="file"
        multiple
        accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
        onChange={(e) => handleFilesSelected(e.target.files)}
      />

      {/* STAGED FILES UPLOAD DRAWER / MODAL */}
      {stagedFiles.length > 0 && (
        <Card className="staged-upload-panel">
          <div className="staged-header">
            <div>
              <h3>Files Ready to Upload ({stagedFiles.length})</h3>
              <p>Review your selected documents before saving to your secure vault.</p>
            </div>
            <button
              className="button button-ghost button-small"
              onClick={() => setStagedFiles([])}
              disabled={uploading}
            >
              <X size={16} /> Cancel All
            </button>
          </div>

          <div className="staged-list">
            {stagedFiles.map((file, idx) => (
              <div key={idx} className="staged-item">
                <span className="staged-file-icon">
                  {file.type === 'application/pdf' ? (
                    <FileText size={22} className="pdf-icon" />
                  ) : (
                    <ImageIcon size={22} className="img-icon" />
                  )}
                </span>
                <div className="staged-file-info">
                  <strong>{file.name}</strong>
                  <small>{formatFileSize(file.size)} &middot; {file.type || 'Document'}</small>
                </div>
                <button
                  type="button"
                  className="staged-remove-btn"
                  onClick={() => removeStagedFile(idx)}
                  disabled={uploading}
                  aria-label="Remove file"
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>

          {uploading && (
            <div className="upload-progress-box">
              <div className="upload-progress-head">
                <span>
                  <LoaderCircle size={18} className="spin" /> Uploading to secure vault…
                </span>
                <strong>{progress}%</strong>
              </div>
              <div className="progress-track">
                <i style={{ width: `${progress}%` }} />
              </div>
            </div>
          )}

          <div className="staged-actions">
            <button
              className="button button-primary"
              onClick={executeUpload}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <LoaderCircle className="spin" size={18} />
                  <span>Uploading {stagedFiles.length} file{stagedFiles.length > 1 ? 's' : ''}…</span>
                </>
              ) : (
                <>
                  <Upload size={18} />
                  <span>Confirm & Upload {stagedFiles.length} File{stagedFiles.length > 1 ? 's' : ''}</span>
                </>
              )}
            </button>
          </div>
        </Card>
      )}

      {/* MAIN TWO-COLUMN WORKSPACE */}
      <div className="documents-layout">
        {/* LEFT COLUMN: DOCUMENT LIBRARY */}
        <Card className="document-library">
          <div className="library-head">
            <div>
              <h2>Document Library</h2>
              <span className="library-count-badge">
                {docs.length} file{docs.length === 1 ? '' : 's'}
              </span>
            </div>
            <button
              className="button button-outline button-small"
              onClick={() => inputRef.current?.click()}
              title="Add new document"
            >
              <Plus size={16} /> Add File
            </button>
          </div>

          {/* Search Box */}
          <div className="document-search-box">
            <Search size={18} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by file name or type…"
              aria-label="Search documents"
            />
            {search && (
              <button
                type="button"
                className="search-clear-btn"
                onClick={() => setSearch('')}
                aria-label="Clear search"
              >
                <X size={16} />
              </button>
            )}
          </div>

          {/* Review Status Filters */}
          <div className="document-status-filters" role="group" aria-label="Filter documents">
            <button
              className={libraryFilter === 'all' ? 'active' : ''}
              onClick={() => setLibraryFilter('all')}
            >
              All <span>({docs.length})</span>
            </button>
            <button
              className={libraryFilter === 'review' ? 'active' : ''}
              onClick={() => setLibraryFilter('review')}
            >
              Needs Review <span>({docs.filter((d) => !d.confirmed).length})</span>
            </button>
            <button
              className={libraryFilter === 'confirmed' ? 'active' : ''}
              onClick={() => setLibraryFilter('confirmed')}
            >
              Reviewed <span>({docs.filter((d) => d.confirmed).length})</span>
            </button>
          </div>

          {/* Document Type Filter */}
          <div className="doc-type-filter-wrap">
            <label htmlFor="docTypeSelect">
              <Filter size={14} /> Type:
            </label>
            <select
              id="docTypeSelect"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="all">All Document Types</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Document List */}
          <div className="document-items">
            {visibleDocs.length ? (
              visibleDocs.map((doc) => {
                const isPdf = (doc.content_type || '').includes('pdf') || doc.filename.endsWith('.pdf')
                return (
                  <div
                    key={doc.id}
                    onClick={() => selectDocument(doc.id)}
                    className={`document-list-item ${selected?.id === doc.id ? 'selected' : ''}`}
                    role="button"
                    tabIndex={0}
                  >
                    <span className={`file-type-icon ${isPdf ? 'pdf' : 'image'}`}>
                      {isPdf ? <FileText size={22} /> : <ImageIcon size={22} />}
                    </span>
                    <div className="document-list-copy">
                      <strong title={doc.filename}>{doc.filename}</strong>
                      <div className="doc-item-meta">
                        <span>{doc.document_type || (isPdf ? 'PDF' : 'Scan')}</span>
                        <span>&bull;</span>
                        <span>
                          {new Date(doc.created_at).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'short',
                            year: 'numeric'
                          })}
                        </span>
                      </div>
                    </div>
                    <div className="document-item-actions">
                      {doc.confirmed ? (
                        <span className="state-badge-verified" title="Reviewed & Confirmed">
                          <CheckCircle2 size={18} />
                        </span>
                      ) : doc.analyzed ? (
                        <span className="state-badge-ready" title="Analyzed (Needs Review)">
                          <Sparkles size={18} />
                        </span>
                      ) : (
                        <span className="state-badge-pending" title="Awaiting Analysis">
                          &bull;
                        </span>
                      )}
                      <button
                        className="doc-quick-delete"
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteCurrentDocument(doc.id)
                        }}
                        title="Delete document"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                )
              })
            ) : (
              <EmptyState
                icon={Search}
                title="No matching documents"
                detail="Try another keyword or filter."
              />
            )}
          </div>

          {/* Drag & Drop Upload Trigger */}
          <div
            className={`upload-drop-zone ${dragging ? 'dragging' : ''}`}
            onClick={() => inputRef.current?.click()}
            onDragEnter={(e) => {
              e.preventDefault()
              setDragging(true)
            }}
            onDragOver={(e) => e.preventDefault()}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault()
              setDragging(false)
              handleFilesSelected(e.dataTransfer.files)
            }}
          >
            <div className="drop-icon-circle">
              <Upload size={24} />
            </div>
            <strong>Drag & Drop Files Here</strong>
            <p>or click to browse from device</p>
            <div className="supported-formats-pills">
              <span>PDF</span>
              <span>JPG</span>
              <span>PNG</span>
              <span>Max 10 MB</span>
            </div>
          </div>
        </Card>

        {/* RIGHT COLUMN: DOCUMENT INSPECTOR & REVIEW */}
        {selected ? (
          <div className="document-review">
            {/* Review Header Banner */}
            <div className="document-review-head">
              <div className="review-title-block">
                <div className="eyebrow">DOCUMENT INSPECTOR</div>
                <h2>{selected.filename}</h2>
                <div className="review-file-badges">
                  <span className="doc-meta-pill">
                    {selected.content_type || 'Document'}
                  </span>
                  {selected.document_date && (
                    <span className="doc-meta-pill">
                      Date: {selected.document_date}
                    </span>
                  )}
                  {selected.hospital_name && (
                    <span className="doc-meta-pill">
                      🏥 {selected.hospital_name}
                    </span>
                  )}
                  {selected.analysis_mode === 'simulated' && (
                    <span className="simulated-tag">SIMULATED DEMO</span>
                  )}
                </div>
              </div>

              <div className="review-action-toolbar">
                {objectUrl && (
                  <>
                    <button
                      className="button button-outline button-small"
                      onClick={() => setFullscreenOpen(true)}
                      title="Inspect in full screen"
                    >
                      <Maximize2 size={16} />
                      <span>Fullscreen</span>
                    </button>
                    <a
                      className="button button-outline button-small"
                      href={objectUrl}
                      target="_blank"
                      rel="noreferrer"
                      title="Open file in new tab"
                    >
                      <ExternalLink size={16} />
                      <span>Open File</span>
                    </a>
                  </>
                )}
                <button
                  className="button button-outline button-small btn-danger-soft"
                  onClick={() => deleteCurrentDocument(selected.id)}
                  title="Delete this document"
                >
                  <Trash2 size={16} />
                  <span>Delete</span>
                </button>
              </div>
            </div>

            {selected.analysis_mode === 'simulated' && (
              <Notice>
                Demo mode is active. This analysis is simulated for review testing; no real patient data is transmitted to AI services.
              </Notice>
            )}

            {/* Split Preview and Analysis Cards */}
            <div className="document-split">
              {/* ORIGINAL DOCUMENT PREVIEW CARD */}
              <Card className="original-preview-card">
                <div className="subcard-head">
                  <div>
                    <strong>Original Document</strong>
                    <span className="subcard-subtext">Private & encrypted view</span>
                  </div>
                  {objectUrl && (
                    <button
                      className="icon-btn-subtle"
                      onClick={() => setFullscreenOpen(true)}
                      title="Expand to Fullscreen"
                    >
                      <Maximize2 size={18} />
                    </button>
                  )}
                </div>

                <div className="preview-container">
                  {objectUrl && previewType.startsWith('image/') ? (
                    <div className="image-preview-wrapper" onClick={() => setFullscreenOpen(true)}>
                      <img
                        className="document-image-preview"
                        src={objectUrl}
                        alt="Uploaded document preview"
                      />
                      <div className="preview-zoom-overlay">
                        <ZoomIn size={24} />
                        <span>Click to expand view</span>
                      </div>
                    </div>
                  ) : objectUrl && previewType === 'application/pdf' ? (
                    <iframe
                      className="document-pdf-preview"
                      title="Original PDF Document"
                      src={objectUrl}
                    />
                  ) : objectUrl ? (
                    <pre className="document-text-preview">{selected.extracted_text}</pre>
                  ) : (
                    <div className="preview-placeholder">
                      <FileText size={38} />
                      <span>Document preview is loading or unavailable.</span>
                    </div>
                  )}
                </div>
              </Card>

              {/* EXTRACTED INFORMATION CARD */}
              <Card className="extracted-panel-card">
                <div className="subcard-head">
                  <div>
                    <strong>Clinical Intelligence</strong>
                    <span className="subcard-subtext">AI-assisted draft extract</span>
                  </div>
                  {selected.analyzed && (
                    <StatusBadge
                      status={selected.confirmed ? 'Completed' : 'Needs Verification'}
                    />
                  )}
                </div>

                {!selected.analyzed ? (
                  <div className="analyze-prompt-box">
                    <div className="analyze-icon-large">
                      <Sparkles size={32} />
                    </div>
                    <h3>Analyze Document with AI</h3>
                    <p>
                      CareBridge will securely parse clinician instructions, follow-up appointments, and required lab reports into an editable draft for your review.
                    </p>

                    <label className="analysis-consent-label">
                      <input
                        type="checkbox"
                        checked={consented}
                        onChange={(e) => setConsented(e.target.checked)}
                      />
                      <span>
                        I consent to automated optical text recognition and drafting for this document. I understand AI outputs require human verification.
                      </span>
                    </label>

                    <button
                      className="button button-primary analyze-cta-btn"
                      onClick={analyze}
                      disabled={analyzing || !consented}
                    >
                      {analyzing ? (
                        <>
                          <LoaderCircle className="spin" size={20} />
                          <span>Extracting Clinical Instructions…</span>
                        </>
                      ) : (
                        <>
                          <Sparkles size={20} />
                          <span>Start Analysis</span>
                        </>
                      )}
                    </button>
                  </div>
                ) : (
                  <div className="analysis-content-box">
                    {/* Plain Language Summary */}
                    <div className="explanation-card">
                      <div className="explanation-head">
                        <Sparkles size={18} />
                        <strong>Plain-Language Explanation</strong>
                      </div>
                      <p>
                        {selected.explanation ||
                          analysis?.simple_explanation ||
                          'No narrative explanation available.'}
                      </p>
                    </div>

                    {/* Metadata Badges */}
                    <div className="extracted-meta-grid">
                      <MetaField
                        label="Document Type"
                        value={analysis?.document_type || selected.document_type}
                      />
                      <MetaField
                        label="Document Date"
                        value={analysis?.document_date || selected.document_date}
                      />
                      <MetaField
                        label="Hospital / Clinic"
                        value={analysis?.hospital_name || selected.hospital_name}
                      />
                    </div>

                    {/* Uncertain Fields Warning */}
                    {analysis?.uncertain_fields?.length > 0 && (
                      <div className="doc-uncertainty-banner">
                        <AlertTriangle size={18} />
                        <div>
                          <strong>Verification Recommended:</strong>
                          <span> Please double check: {analysis.uncertain_fields.join(', ')}</span>
                        </div>
                      </div>
                    )}

                    {/* Medications As Written */}
                    {analysis?.medication_information?.length > 0 && (
                      <div className="medication-extract-box">
                        <strong>Prescribed Regimen (as written):</strong>
                        <div className="med-pills-list">
                          {analysis.medication_information.map((med, idx) => (
                            <div key={idx} className="med-pill-item">
                              <span>💊</span>
                              <span>{med}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Extracted Raw Text with Copy */}
                    <div className="raw-text-accordion">
                      <div className="raw-text-head">
                        <button
                          type="button"
                          className="accordion-toggle-btn"
                          onClick={() => setShowRawText(!showRawText)}
                        >
                          <strong>Raw Extracted Text</strong>
                          <span className="raw-text-meta">({selected.extracted_text?.length || 0} characters)</span>
                        </button>
                        <button
                          type="button"
                          className="button button-ghost button-small copy-btn"
                          onClick={copyExtracted}
                        >
                          {copiedText ? (
                            <>
                              <Check size={16} className="text-emerald" /> Copied!
                            </>
                          ) : (
                            <>
                              <Copy size={16} /> Copy Text
                            </>
                          )}
                        </button>
                      </div>

                      {showRawText && (
                        <pre className="extracted-raw-code">
                          {selected.extracted_text || 'No readable text was extracted.'}
                        </pre>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            </div>

            {/* SUGGESTED TASKS FOR HUMAN VERIFICATION */}
            {selected.analyzed && (
              <Card className="suggested-tasks-card">
                <div className="suggested-tasks-head">
                  <div>
                    <div className="eyebrow">HUMAN IN THE LOOP</div>
                    <h3>Suggested Journey Tasks</h3>
                    <p className="suggested-subtitle">
                      Verify each task before adding it to your shared recovery schedule.
                    </p>
                  </div>
                  <div className="suggested-head-actions">
                    <span className="verification-chip">
                      <ShieldCheck size={16} /> Patient Verification Required
                    </span>
                    {suggested.length > 0 && (
                      <button
                        type="button"
                        className="button button-ghost button-small"
                        onClick={() => toggleAllTasks(!allTasksSelected)}
                      >
                        {allTasksSelected ? 'Deselect All' : 'Select All'}
                      </button>
                    )}
                  </div>
                </div>

                {suggested.length ? (
                  <div className="suggested-tasks-list">
                    {suggested.map((task, i) => (
                      <div
                        className={`suggested-task-card ${selectedTasks[i] ? 'task-checked' : 'task-unchecked'}`}
                        key={i}
                      >
                        <div className="task-checkbox-col">
                          <input
                            aria-label={`Include ${task.title}`}
                            type="checkbox"
                            checked={Boolean(selectedTasks[i])}
                            onChange={(e) =>
                              setSelectedTasks({ ...selectedTasks, [i]: e.target.checked })
                            }
                          />
                        </div>

                        <div className="task-content-col">
                          <div className="task-title-row">
                            <input
                              className="task-edit-title"
                              aria-label="Edit task title"
                              value={editedTasks[i]?.title ?? task.title}
                              onChange={(e) =>
                                setEditedTasks({
                                  ...editedTasks,
                                  [i]: { ...editedTasks[i], title: e.target.value }
                                })
                              }
                            />
                            <StatusBadge status="Needs Verification" />
                          </div>

                          <textarea
                            className="task-edit-description"
                            aria-label="Edit task instructions"
                            rows="2"
                            value={editedTasks[i]?.description ?? task.description}
                            onChange={(e) =>
                              setEditedTasks({
                                ...editedTasks,
                                [i]: { ...editedTasks[i], description: e.target.value }
                              })
                            }
                          />

                          <div className="task-source-quote">
                            <strong>Source Reference:</strong>
                            <em> &ldquo;{task.source_text}&rdquo;</em>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-tasks-state">
                    <p>No actionable tasks were identified in this document. You can confirm the document and manually add tasks from your Journey page.</p>
                  </div>
                )}

                {/* Confirmation Footer */}
                {selected.confirmed || confirmed ? (
                  <div className="confirmed-success-notice">
                    <CheckCircle2 size={22} />
                    <div>
                      <strong>Document Review Confirmed</strong>
                      <p>Approved tasks have been incorporated into your care journey timeline.</p>
                    </div>
                  </div>
                ) : (
                  <div className="confirm-action-bar">
                    <label className="confirm-checkbox-label">
                      <input
                        type="checkbox"
                        checked={Boolean(selectedTasks.__ack)}
                        onChange={(e) =>
                          setSelectedTasks({ ...selectedTasks, __ack: e.target.checked })
                        }
                      />
                      <span>
                        I have verified these instructions against my original discharge paperwork.
                      </span>
                    </label>

                    <button
                      className="button button-primary confirm-save-btn"
                      disabled={confirming || !selectedTasks.__ack}
                      onClick={confirmTasks}
                    >
                      {confirming ? (
                        <>
                          <LoaderCircle className="spin" size={18} />
                          <span>Saving to Journey…</span>
                        </>
                      ) : (
                        <>
                          <Check size={18} />
                          <span>Confirm & Save Tasks</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </Card>
            )}
          </div>
        ) : (
          <Card className="no-document-selected-card">
            <EmptyState
              icon={FileUp}
              title="Select a Document to Inspect"
              detail="Choose any file from your library on the left, or upload a new medical document."
            />
          </Card>
        )}
      </div>

      {/* FULLSCREEN LIGHTBOX MODAL */}
      {fullscreenOpen && objectUrl && (
        <div className="doc-modal-overlay" onClick={() => setFullscreenOpen(false)}>
          <div className="doc-modal-window" onClick={(e) => e.stopPropagation()}>
            <div className="doc-modal-head">
              <div className="doc-modal-title">
                <FileText size={20} />
                <strong>{selected.filename}</strong>
              </div>
              <div className="doc-modal-controls">
                <button
                  type="button"
                  className="icon-btn-modal"
                  onClick={() => setZoomLevel((z) => Math.max(0.5, z - 0.25))}
                  title="Zoom Out"
                >
                  <ZoomOut size={18} />
                </button>
                <span className="zoom-indicator">{Math.round(zoomLevel * 100)}%</span>
                <button
                  type="button"
                  className="icon-btn-modal"
                  onClick={() => setZoomLevel((z) => Math.min(3, z + 0.25))}
                  title="Zoom In"
                >
                  <ZoomIn size={18} />
                </button>
                <button
                  type="button"
                  className="icon-btn-modal"
                  onClick={() => setZoomLevel(1)}
                  title="Reset Zoom"
                >
                  <RotateCcw size={18} />
                </button>
                <button
                  type="button"
                  className="icon-btn-modal close-btn"
                  onClick={() => setFullscreenOpen(false)}
                  title="Close Modal"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            <div className="doc-modal-body">
              {previewType.startsWith('image/') ? (
                <img
                  src={objectUrl}
                  alt="Fullscreen view"
                  style={{
                    transform: `scale(${zoomLevel})`,
                    transformOrigin: 'top center',
                    transition: 'transform 0.15s ease-out'
                  }}
                />
              ) : previewType === 'application/pdf' ? (
                <iframe
                  src={objectUrl}
                  title="Fullscreen PDF"
                  className="modal-pdf-frame"
                />
              ) : (
                <pre className="modal-text-view">{selected.extracted_text}</pre>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="safety-footnote">
        Safety Notice: Extracted content is an assistive draft. CareBridge does not diagnose, prescribe, or override clinical directives.
      </div>
    </div>
  )
}

function MetaField({ label, value }) {
  return (
    <div className="doc-meta-field">
      <small>{label}</small>
      <strong>{value || 'Not specified'}</strong>
    </div>
  )
}
