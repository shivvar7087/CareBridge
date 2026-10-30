import { useEffect, useState } from 'react'
import { CircleAlert, Filter, LifeBuoy, Plus, Send, SlidersHorizontal } from 'lucide-react'
import api, { errorMessage } from '../api'
import { useAuth } from '../auth'
import { Card, EmptyState, Loading, PageHeading, StatusBadge } from '../components/UI'

export default function Barriers() {
  const { user } = useAuth()
  const [items, setItems] = useState(null)
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('All barriers')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', category: 'Other', related_task_id: '', status: 'Open', follow_up_notes: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function load() {
    const [barriers, taskRows] = await Promise.all([api.get('/barriers'), api.get('/tasks')])
    setItems(barriers.data); setTasks(taskRows.data)
  }
  useEffect(() => { load().catch((e) => setError(errorMessage(e))) }, [])
  async function submit(e) {
    e.preventDefault(); setBusy(true); setError('')
    try { await api.post('/barriers', { ...form, related_task_id: form.related_task_id ? Number(form.related_task_id) : null }); setForm({ title: '', description: '', category: 'Other', related_task_id: '', status: 'Open', follow_up_notes: '' }); setShowForm(false); await load() }
    catch (e) { setError(errorMessage(e)) } finally { setBusy(false) }
  }
  async function resolve(item) {
    try { await api.put(`/barriers/${item.id}`, { status: item.status === 'Resolved' ? 'Open' : 'Resolved' }); await load() }
    catch (e) { setError(errorMessage(e)) }
  }
  if (!items) return error ? <div className="form-error">{error}</div> : <Loading />
  const shown = items.filter((item) => filter === 'All barriers' || item.status === filter)
  const categories = ['Missed appointment', 'Report unavailable', 'Travel difficulty', 'Hospital coordination issue', 'Document-related issue', 'Other']
  return <div><PageHeading eyebrow="PRACTICAL SUPPORT NOTES" title="Access Barriers" description="Record practical challenges so you and your caregivers can follow up on them." action={user?.role === 'patient' && <button className="button button-primary" onClick={() => setShowForm(!showForm)}><Plus size={17} /> Log a barrier</button>} />
    {error && <div className="form-error">{error}</div>}
    {showForm && <Card className="barrier-form-card"><div className="card-head"><div><div className="eyebrow">NEW FOLLOW-UP NOTE</div><h2>Log an access barrier</h2></div><button className="icon-link" onClick={() => setShowForm(false)}>×</button></div><form className="form-grid" onSubmit={submit}><label className="field span-two"><span>Barrier title</span><input required minLength="2" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="What made it harder to access care?" /></label><label className="field"><span>Category</span><select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{categories.map((x) => <option key={x}>{x}</option>)}</select></label><label className="field"><span>Related task</span><select value={form.related_task_id} onChange={(e) => setForm({ ...form, related_task_id: e.target.value })}><option value="">No linked task</option>{tasks.map((t) => <option value={t.id} key={t.id}>{t.title}</option>)}</select></label><label className="field span-two"><span>Description</span><textarea rows="3" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Add a few details" /></label><label className="field span-two"><span>Follow-up notes</span><textarea rows="2" value={form.follow_up_notes} onChange={(e) => setForm({ ...form, follow_up_notes: e.target.value })} placeholder="Who will follow up, and what is the next step?" /></label><div className="span-two modal-actions"><button className="button button-quiet" type="button" onClick={() => setShowForm(false)}>Cancel</button><button className="button button-primary" disabled={busy}><Send size={15} /> {busy ? 'Saving…' : 'Save barrier'}</button></div></form></Card>}
    <div className="barrier-toolbar"><div className="barrier-insight"><span><LifeBuoy size={19} /></span><div><strong>{items.filter((i) => i.status !== 'Resolved').length} open item{items.filter((i) => i.status !== 'Resolved').length === 1 ? '' : 's'}</strong><small>Practical access challenges logged in this journey</small></div></div><label className="filter-control"><SlidersHorizontal size={15} /><select value={filter} onChange={(e) => setFilter(e.target.value)}><option>All barriers</option><option>Open</option><option>Resolved</option></select></label></div>
    {!shown.length ? <Card><EmptyState icon={CircleAlert} title="No barriers recorded" detail="Log a practical access challenge to keep a record for follow-up." /></Card> : <div className="barrier-list">{shown.map((item) => <Card className="barrier-card" key={item.id}><div className={`barrier-category-icon ${item.status === 'Resolved' ? 'barrier-resolved' : ''}`}><CircleAlert size={18} /></div><div className="barrier-copy"><div className="barrier-title-row"><h3>{item.title}</h3><StatusBadge status={item.status === 'Resolved' ? 'Completed' : 'In Progress'} /></div><p>{item.description || 'No description added.'}</p><div className="barrier-meta"><span>{item.category}</span><span>{new Date(item.barrier_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>{item.related_task_id && <span>Related task #{item.related_task_id}</span>}</div>{item.follow_up_notes && <div className="followup-note"><strong>Follow-up:</strong> {item.follow_up_notes}</div>}</div>{user?.role === 'patient' && <button className="button button-outline button-small" onClick={() => resolve(item)}>{item.status === 'Resolved' ? 'Reopen' : 'Mark resolved'}</button>}</Card>)}</div>}
  </div>
}
