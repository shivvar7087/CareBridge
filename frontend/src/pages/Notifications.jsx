import { useEffect, useState } from 'react'
import { Bell, Check, CheckCheck, ClipboardCheck, FileText, HeartHandshake, ListTodo } from 'lucide-react'
import api, { errorMessage } from '../api'
import { Card, EmptyState, Loading, PageHeading } from '../components/UI'

const icons = { task: ListTodo, document: FileText, appointment: ClipboardCheck, share: HeartHandshake }

export default function Notifications() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const load = () => api.get('/notifications').then(({ data }) => setItems(data)).catch((e) => setError(errorMessage(e)))
  useEffect(() => { load() }, [])
  async function markRead(item) {
    try { await api.patch(`/notifications/${item.id}/read`); await load() } catch (e) { setError(errorMessage(e)) }
  }
  async function markAll() { await Promise.all((items || []).filter((x) => !x.is_read).map((x) => api.patch(`/notifications/${x.id}/read`))); load() }
  if (!items) return error ? <div className="form-error">{error}</div> : <Loading />
  const unread = items.filter((x) => !x.is_read).length
  return <div><PageHeading eyebrow="JOURNEY UPDATES" title="Notifications" description="In-app reminders about tasks, appointments, and shared activity." action={unread > 0 && <button className="button button-outline" onClick={markAll}><CheckCheck size={16} /> Mark all read</button>} />
    {error && <div className="form-error">{error}</div>}
    {items.length === 0 ? <Card><EmptyState icon={Bell} title="You’re all caught up" detail="CareBridge notifications will appear here when something changes in your journey." /></Card> : <div className="notification-list">{items.map((item) => { const Icon = icons[item.kind] || Bell; return <Card className={`notification-card ${item.is_read ? 'notification-read' : ''}`} key={item.id}><span className={`notification-icon notification-${item.kind}`}><Icon size={18} /></span><div className="notification-copy"><div className="notification-title-row"><strong>{item.title}</strong>{!item.is_read && <span className="unread-label">NEW</span>}</div><p>{item.message}</p><small>{new Date(item.created_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}</small></div>{!item.is_read && <button className="mark-read" onClick={() => markRead(item)} aria-label="Mark as read"><Check size={17} /></button>}</Card> })}</div>}
    <div className="external-notification-note">CareBridge currently provides in-app notifications. Email, SMS, and WhatsApp notifications are not configured.</div>
  </div>
}
