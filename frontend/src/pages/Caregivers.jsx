import { useEffect, useState } from 'react'
import { Clipboard, HeartHandshake, Link2, Mail, Plus, ShieldCheck, Trash2, UserRound, Users } from 'lucide-react'
import api, { errorMessage } from '../api'
import { useAuth } from '../auth'
import { Card, EmptyState, Loading, Notice, PageHeading, StatusBadge } from '../components/UI'

export default function Caregivers() {
  const { user } = useAuth()
  const [people, setPeople] = useState(null)
  const [tasks, setTasks] = useState([])
  const [email, setEmail] = useState('')
  const [invite, setInvite] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [assignment, setAssignment] = useState({})
  async function load() {
    const [caregivers, taskData] = await Promise.all([api.get('/caregivers'), user?.role === 'patient' ? api.get('/tasks') : Promise.resolve({ data: [] })])
    setPeople(caregivers.data); setTasks(taskData.data)
  }
  useEffect(() => { load().catch((e) => setError(errorMessage(e))) }, [])
  async function inviteCaregiver(e) {
    e.preventDefault(); setError(''); setInvite(null); setBusy(true)
    try { const { data } = await api.post('/caregivers/invite', { email }); setInvite(data); setEmail(''); await load() }
    catch (err) { setError(errorMessage(err)) } finally { setBusy(false) }
  }
  async function assign(taskId) {
    const caregiverId = assignment[taskId]; if (!caregiverId) return
    setError('')
    try { await api.post('/caregivers/assign-task', { task_id: Number(taskId), caregiver_id: Number(caregiverId) }); await load() }
    catch (e) { setError(errorMessage(e)) }
  }
  async function remove(person) {
    if (!window.confirm(`Remove access for ${person.name || person.email}?`)) return
    try { await api.delete(`/caregivers/${person.id}`); await load() } catch (e) { setError(errorMessage(e)) }
  }
  async function copyCode(code) { try { await navigator.clipboard.writeText(code); setInvite({ ...invite, copied: true }) } catch { setError('Copy the invitation code manually.') } }
  if (!people) return error ? <div className="form-error">{error}</div> : <Loading />
  const active = people.filter((p) => p.active)
  return <div><PageHeading eyebrow="SUPPORT, SHARED ON YOUR TERMS" title="Caregivers" description={user?.role === 'patient' ? 'Invite someone you trust and choose which journey tasks they can help with.' : 'View the patient journey shared with your caregiver account.'} />
    {error && <div className="form-error">{error}</div>}
    {user?.role === 'patient' ? <>
      <Card className="invite-card"><div className="invite-visual"><HeartHandshake size={27} /></div><div className="invite-copy"><div className="eyebrow">INVITE A CAREGIVER</div><h2>Make room for support</h2><p>Caregivers see the shared journey and tasks assigned to them. They can update task status, but can’t change clinical instructions.</p></div><form className="invite-form" onSubmit={inviteCaregiver}><label className="field"><span>Caregiver email address</span><div className="input-with-icon"><Mail size={17} /><input type="email" value={email} required onChange={(e) => setEmail(e.target.value)} placeholder="family@example.com" /></div></label><button className="button button-primary" disabled={busy}><Plus size={16} /> {busy ? 'Creating invite…' : 'Create invitation'}</button></form></Card>
      {invite && <div className="invite-result"><div><strong>{invite.registered ? 'Caregiver access is active' : 'Invitation created'}</strong><span>{invite.instructions}</span></div><code>{invite.invitation_code}</code><button className="button button-outline button-small" onClick={() => copyCode(invite.invitation_code)}><Clipboard size={14} />{invite.copied ? 'Copied' : 'Copy code'}</button></div>}
      <div className="section-heading-row"><div><div className="eyebrow">YOUR SUPPORT CIRCLE</div><h2>Connected caregivers <span className="count-pill">{active.length}</span></h2></div><span className="access-label"><ShieldCheck size={14} /> You control access</span></div>
      {people.length ? <div className="caregiver-list">{people.map((person) => <Card key={person.id} className="caregiver-row-card"><div className="caregiver-avatar"><UserRound size={20} /></div><div className="caregiver-person"><strong>{person.name || person.email}</strong><span>{person.email}</span></div><StatusBadge status={person.active ? person.name ? 'Available' : 'Pending' : 'Missing'} /><div className="caregiver-permission"><ShieldCheck size={14} /> Journey access {person.active ? 'on' : 'removed'}</div>{person.active && <button className="button button-quiet button-small danger-action" onClick={() => remove(person)}><Trash2 size={15} /> Remove access</button>}</Card>)}</div> : <Card><EmptyState icon={Users} title="No caregivers yet" detail="Create an invitation to share journey steps with someone you trust." /></Card>}
      <Card className="assignment-card"><div className="card-head"><div><div className="eyebrow">SHARE THE TO-DO LIST</div><h2>Assign a task</h2></div><span className="card-icon soft-teal"><Link2 size={18} /></span></div><div className="assign-intro">Choose a task and a caregiver with active access. The task’s due date and description will be visible to them.</div>
        {active.some((p) => p.caregiver_user_id) && tasks.length ? <div className="assignment-list">{tasks.filter((task) => task.status !== 'Completed').map((task) => <div className="assignment-row" key={task.id}><div><strong>{task.title}</strong><small>{task.due_date ? `Due ${new Date(`${task.due_date}T12:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}` : 'No due date'}</small></div><select aria-label={`Assign ${task.title}`} value={task.assigned_to_id || assignment[task.id] || ''} onChange={(e) => { setAssignment({ ...assignment, [task.id]: e.target.value }); if (e.target.value) assign(task.id) }}><option value="">Choose caregiver…</option>{active.filter((p) => p.caregiver_user_id).map((p) => <option value={p.caregiver_user_id} key={p.id}>{p.name}</option>)}</select></div>)}</div> : <div className="assignment-empty">Invite a registered caregiver to start assigning tasks.</div>}
      </Card>
    </> : <><Card className="caregiver-shared-banner"><div className="caregiver-illustration"><HeartHandshake size={25} /></div><div><div className="eyebrow">SHARED WITH YOU</div><h2>{people[0]?.patient_name || 'Patient journey'}</h2><p>You can view the shared timeline and update tasks assigned to you. For changes to care instructions, contact the patient or their healthcare team.</p></div></Card><Card className="assignment-card"><div className="card-head"><div><div className="eyebrow">YOUR RESPONSIBILITIES</div><h2>Assigned tasks</h2></div></div>{tasks.length ? tasks.map((task) => <div className="assignment-row caregiver-task-row" key={task.id}><div><strong>{task.title}</strong><small>{task.description} {task.due_date ? `· Due ${new Date(`${task.due_date}T12:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}` : ''}</small></div><StatusBadge status={task.status} /></div>) : <EmptyState icon={HeartHandshake} title="No tasks assigned yet" detail="Tasks shared with you will appear here." />}</Card></>}
    <Notice>CareBridge does not send invitations by email. Share the invitation code directly with the caregiver.</Notice>
  </div>
}
