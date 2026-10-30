import { AlertCircle, Check, CheckCircle2, Clock3, LoaderCircle } from 'lucide-react'

export function PageHeading({ eyebrow, title, description, action }) {
  return <div className="page-heading"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1>{description && <p>{description}</p>}</div>{action && <div className="heading-action">{action}</div>}</div>
}
export function Card({ children, className = '', ...props }) { return <section className={`card ${className}`} {...props}>{children}</section> }
export function StatusBadge({ status }) {
  const cls = String(status || '').toLowerCase().replaceAll(' ', '-')
  const Icon = status === 'Completed' || status === 'Available' || status === 'Verified' ? CheckCircle2 : status === 'Overdue' || status === 'Missing' ? AlertCircle : Clock3
  return <span className={`status-badge status-${cls}`}><Icon size={13} />{status}</span>
}
export function EmptyState({ icon: Icon = CheckCircle2, title, detail }) { return <div className="empty-state"><span className="empty-icon"><Icon size={22} /></span><strong>{title}</strong><p>{detail}</p></div> }
export function Loading() { return <div className="loading-inline"><LoaderCircle className="spin" size={19} /> Loading…</div> }
export function Notice({ children, tone = 'info' }) { return <div className={`notice notice-${tone}`}>{tone === 'success' ? <Check size={17} /> : <AlertCircle size={17} />}<span>{children}</span></div> }
export function Field({ label, hint, ...props }) { return <label className="field"><span>{label}</span><input {...props} />{hint && <small>{hint}</small>}</label> }
