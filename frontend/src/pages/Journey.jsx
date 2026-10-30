import { useEffect, useMemo, useState } from 'react'
import { Activity, CalendarDays, Plus, SlidersHorizontal } from 'lucide-react'
import api, { errorMessage } from '../api'
import { useAuth } from '../auth'
import { Card, Loading, PageHeading, StatusBadge } from '../components/UI'
import { AddTaskForm, TaskAction, TaskHistoryButton } from './Tasks'

const categoryIcon = { Appointment: CalendarDays, 'Diagnostic Test': Activity, 'Report Collection': FileSymbol, 'Hospital Discharge': Activity }
function FileSymbol(props) { return <Activity {...props} /> }
function readableDate(value) { return value ? new Date(`${value}T12:00:00`).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }) : 'Date to be confirmed' }

export default function Journey() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState(null)
  const [filter, setFilter] = useState('All steps')
  const [openAdd, setOpenAdd] = useState(false)
  const [error, setError] = useState('')
  const patient = user?.role === 'patient'
  const load = () => api.get('/journey/timeline').then(({ data }) => setTasks(data)).catch((e) => setError(errorMessage(e)))
  useEffect(() => { load() }, [])
  const filtered = useMemo(() => tasks?.filter((task) => filter === 'All steps' || task.status === filter) || [], [tasks, filter])
  const grouped = useMemo(() => filtered.reduce((acc, task) => { const key = task.due_date || 'undated'; (acc[key] ||= []).push(task); return acc }, {}), [filtered])
  if (!tasks) return <Loading />
  return <div><PageHeading eyebrow="YOUR CARE PLAN, AT A GLANCE" title="My Healthcare Journey" description="A timeline of the care tasks and appointments you’re coordinating." action={patient && <button className="button button-primary" onClick={() => setOpenAdd(true)}><Plus size={17} /> Add a task</button>} />
    <div className="journey-toolbar"><div className="journey-legend"><span><i className="legend-dot dot-complete" /> Completed</span><span><i className="legend-dot dot-active" /> In progress</span><span><i className="legend-dot dot-upcoming" /> Upcoming</span></div><label className="filter-control"><SlidersHorizontal size={15} /><select value={filter} onChange={(e) => setFilter(e.target.value)}><option>All steps</option>{['Pending', 'In Progress', 'Completed', 'Overdue', 'Needs Verification', 'Scheduled'].map((x) => <option key={x}>{x}</option>)}</select></label></div>
    {!filtered.length ? <Card><div className="empty-state"><span className="empty-icon"><Activity size={22} /></span><strong>No journey steps found</strong><p>{filter === 'All steps' ? 'Add a task or confirm tasks from a reviewed document.' : 'Try another status filter.'}</p></div></Card> : <div className="timeline">{Object.entries(grouped).map(([date, dayTasks]) => <div className="timeline-group" key={date}><div className="timeline-date"><span>{date === 'undated' ? 'DATE TO BE CONFIRMED' : readableDate(date)}</span><i /></div>{dayTasks.map((task) => { const Icon = categoryIcon[task.category] || Activity; return <Card className={`timeline-card ${task.status === 'Completed' ? 'timeline-done' : ''}`} key={task.id}><div className="timeline-marker"><span className={`timeline-category cat-${task.category.toLowerCase().replaceAll(' ', '-')}`}><Icon size={17} /></span></div><div className="timeline-task"><div className="task-title-row"><h3>{task.title}</h3><StatusBadge status={task.status} /></div><p>{task.description || 'No additional details added.'}</p><div className="timeline-meta"><span>{task.category}</span>{task.assigned_to_id && <span>Assigned to a caregiver</span>}{task.source_document_id && <span>From a document</span>}{task.needs_clinician_verification && <span className="verification-note">Clinician verification needed</span>}</div></div><div className="timeline-action"><TaskHistoryButton task={task} /><TaskAction task={task} onChanged={load} compact /></div></Card> })}</div>)}</div>}
    {openAdd && <AddTaskForm onClose={() => setOpenAdd(false)} onSaved={() => { setOpenAdd(false); load() }} />}
    <div className="safety-footnote">CareBridge AI keeps the original instruction on file. Changes to clinician instructions are flagged for verification.</div>
  </div>
}
