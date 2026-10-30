import { useEffect, useState } from 'react'
import { CalendarDays, Check, Circle, Clock3, History, Plus, UserRound, X } from 'lucide-react'
import { useAuth } from '../auth'
import api, { errorMessage } from '../api'
import { Card, EmptyState, Loading, PageHeading, StatusBadge } from '../components/UI'

export function TaskAction({ task, onChanged, compact = false }) {
  const { user } = useAuth()
  const [busy, setBusy] = useState(false)
  if (task.status === 'Completed') return <span className="completed-check"><Check size={16} />{compact ? 'Done' : 'Completed'}</span>
  const canComplete = user?.role === 'patient' || task.assigned_to_id === user?.id
  if (!canComplete) return null
  async function complete() {
    setBusy(true)
    try { await api.patch(`/tasks/${task.id}/status`, { status: 'Completed' }); onChanged?.() } catch (e) { window.alert(errorMessage(e)) } finally { setBusy(false) }
  }
  return <button className={compact ? 'complete-round' : 'button button-outline button-small'} onClick={complete} disabled={busy}>{compact ? <Check size={15} /> : <><Check size={14} /> Mark complete</>}{busy && <span className="mini-spinner" />}</button>
}

export function TaskHistoryButton({ task }) {
  const [history, setHistory] = useState(null)
  const [error, setError] = useState('')
  async function open() {
    setError('')
    try { const { data } = await api.get(`/tasks/${task.id}/history`); setHistory(data) }
    catch (e) { setError(errorMessage(e)) }
  }
  return <>
    <button className="history-button" onClick={open}><History size={14} /> History</button>
    {error && <div className="form-error">{error}</div>}
    {history && <div className="modal-backdrop" onClick={() => setHistory(null)}><div className="modal-card history-modal" onClick={(event) => event.stopPropagation()}>
      <div className="modal-head"><div><div className="eyebrow">TASK RECORD</div><h2>{task.title}</h2></div><button className="icon-link" onClick={() => setHistory(null)} aria-label="Close task history"><X size={17} /></button></div>
      <h3>Activity</h3>{history.events.length ? <div className="history-events">{history.events.map((event, index) => <div className="history-event" key={`${event.action}-${index}`}><span className="history-dot" /><div><strong>{event.action.replaceAll('.', ' ')}</strong><small>{event.actor} · {new Date(event.at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}</small></div></div>)}</div> : <p className="history-empty">No activity has been recorded.</p>}
      <h3>Caregiver assignments</h3>{history.assignments.length ? <div className="history-events">{history.assignments.map((assignment, index) => <div className="history-event" key={`${assignment.caregiver}-${index}`}><span className={`history-dot ${assignment.active ? 'history-dot-active' : ''}`} /><div><strong>{assignment.caregiver}{assignment.active ? ' · Active' : ' · Previous'}</strong><small>Assigned {new Date(assignment.assigned_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}{assignment.unassigned_at ? ` · Removed ${new Date(assignment.unassigned_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}` : ''}</small></div></div>)}</div> : <p className="history-empty">This task has not been assigned to a caregiver.</p>}
    </div></div>}
  </>
}

export function AddTaskForm({ onClose, onSaved }) {
  const [form, setForm] = useState({ title: '', description: '', category: 'Other', due_date: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(e) {
    e.preventDefault(); setError(''); setBusy(true)
    try { await api.post('/tasks', { ...form, due_date: form.due_date || null }); onSaved() } catch (err) { setError(errorMessage(err)) } finally { setBusy(false) }
  }
  return <div className="modal-backdrop" onClick={onClose}><div className="modal-card" onClick={(e) => e.stopPropagation()}><div className="modal-head"><div><div className="eyebrow">JOURNEY STEP</div><h2>Add a task</h2></div><button className="icon-link" onClick={onClose}>×</button></div>{error && <div className="form-error">{error}</div>}<form onSubmit={submit} className="form-grid"><label className="field span-two"><span>Task title</span><input required minLength="2" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Collect a diagnostic report" /></label><label className="field span-two"><span>Description</span><textarea rows="3" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Add administrative details or context" /></label><label className="field"><span>Category</span><select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{['Other', 'Appointment', 'Diagnostic Test', 'Report Collection', 'Hospital Discharge', 'Follow-up', 'Administrative'].map((c) => <option key={c}>{c}</option>)}</select></label><label className="field"><span>Due date</span><input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></label><div className="span-two modal-actions"><button className="button button-quiet" type="button" onClick={onClose}>Cancel</button><button className="button button-primary" disabled={busy}>{busy ? 'Saving…' : 'Add to journey'}</button></div></form></div></div>
}

export default function Tasks() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState(null)
  const [filter, setFilter] = useState('All')
  const [openAdd, setOpenAdd] = useState(false)
  const [error, setError] = useState('')
  const load = () => api.get('/tasks').then(({ data }) => setTasks(data)).catch((e) => setError(errorMessage(e)))
  useEffect(() => { load() }, [])
  const shown = tasks?.filter((t) => filter === 'All' || t.status === filter) || []
  if (!tasks) return <Loading />
  return <div><PageHeading eyebrow="YOUR TO-DO LIST" title="My Tasks" description="Keep track of care journey steps, due dates, and shared responsibilities." action={user?.role === 'patient' && <button className="button button-primary" onClick={() => setOpenAdd(true)}><Plus size={17} /> Add a task</button>} />
    {error && <div className="form-error">{error}</div>}
    <div className="task-filters">{['All', 'Pending', 'In Progress', 'Scheduled', 'Overdue', 'Needs Verification', 'Completed'].map((s) => <button key={s} className={filter === s ? 'filter-chip selected' : 'filter-chip'} onClick={() => setFilter(s)}>{s}{s === 'All' ? <span>{tasks.length}</span> : <span>{tasks.filter((t) => t.status === s).length}</span>}</button>)}</div>
    {shown.length === 0 ? <Card><EmptyState icon={Circle} title="No tasks in this view" detail="Try another status or add a task to your journey." /></Card> : <div className="task-list">{shown.map((task) => <Card className="task-card" key={task.id}><div className={`task-status-icon task-${task.status.toLowerCase().replaceAll(' ', '-')}`}>{task.status === 'Completed' ? <Check size={18} /> : task.status === 'Overdue' ? <Clock3 size={18} /> : <Circle size={17} />}</div><div className="task-card-body"><div className="task-title-row"><h3>{task.title}</h3><StatusBadge status={task.status} /></div><p>{task.description || 'No description provided.'}</p><div className="task-card-meta"><span><CalendarDays size={14} />{task.due_date ? new Date(`${task.due_date}T12:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'No due date'}</span><span><span className="meta-dot" />{task.category}</span>{task.assigned_to_id && <span><UserRound size={14} /> Shared with caregiver</span>}{task.needs_clinician_verification && <span className="verification-note">Needs clinician verification</span>}</div></div><div className="task-card-action"><TaskHistoryButton task={task} /><TaskAction task={task} onChanged={load} /></div></Card>)}</div>}
    {openAdd && <AddTaskForm onClose={() => setOpenAdd(false)} onSaved={() => { setOpenAdd(false); load() }} />}
  </div>
}
