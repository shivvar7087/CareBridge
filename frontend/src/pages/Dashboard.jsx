import { useEffect, useState } from 'react'
import { Activity, ArrowRight, CalendarDays, CheckCircle2, ChevronRight, Clock3, FileCheck2, FileText, HeartHandshake, ListTodo, TriangleAlert, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import api, { errorMessage } from '../api'
import { Card, EmptyState, Loading, PageHeading, StatusBadge } from '../components/UI'
import { getNonZeroStatusRows, getProgressPercentage } from '../utils/dashboard'

const colors = ['#159b8c', '#90b7d4', '#79b5a0', '#e89166', '#b7a6df']
const dateLabel = (value) => value ? new Date(`${value}T12:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'Date to be confirmed'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.get('/dashboard').then(({ data: response }) => setData(response)).catch((e) => setError(errorMessage(e))) }, [])
  if (error) return <div className="form-error">{error}</div>
  if (!data) return <Loading />
  const { summary, task_status: taskStatus, journey_progress: progress } = data
  const percentage = getProgressPercentage(summary.completed_tasks, summary.total_tasks)
  const todayYMD = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}-${String(new Date().getDate()).padStart(2, '0')}`
  return <div className="dashboard-page">
    <div className="welcome-strip"><div><div className="eyebrow">YOUR CARE, COORDINATED</div><h1>Good to see you, {data.patient.name.split(' ')[0]} <span className="wave">✦</span></h1><p>Here’s what’s happening across your healthcare journey.</p></div><div className="welcome-art"><div className="art-ring ring-one" /><div className="art-ring ring-two" /><span><Activity size={28} /></span></div></div>
    {data.patient.is_demo && <div className="demo-banner"><span className="demo-label">FICTIONAL DEMO</span> You’re viewing sample information. It does not represent a real patient or medical record.</div>}
    {data.missing_steps.length > 0 && <div className="alert-strip"><span className="alert-icon"><TriangleAlert size={17} /></span><div><strong>{data.missing_steps.length} journey step{data.missing_steps.length > 1 ? 's' : ''} need attention</strong><span>{data.missing_steps[0].title} · {data.missing_steps[0].reason}</span></div><Link to="/journey" className="alert-link">Review steps <ArrowRight size={15} /></Link></div>}
    <div className="stats-grid">
      <StatCard label="Journey tasks" value={summary.total_tasks} foot={`${summary.completed_tasks} completed`} icon={ListTodo} tint="blue" />
      <StatCard label="Completed" value={summary.completed_tasks} foot={`${percentage}% of your journey`} icon={CheckCircle2} tint="green" />
      <StatCard label="Still in progress" value={summary.pending_tasks} foot="Tasks awaiting completion" icon={Clock3} tint="amber" />
      <StatCard label="Overdue" value={summary.overdue_tasks} foot="Administrative follow-up" icon={TriangleAlert} tint="rose" />
    </div>
    <div className="dashboard-grid dashboard-grid-main">
      <Card className="journey-progress-card"><div className="card-head"><div><div className="eyebrow">JOURNEY OVERVIEW</div><h2>Your progress</h2></div><Link to="/journey" className="text-link">View journey <ChevronRight size={16} /></Link></div>
        <div className="progress-content"><div className="progress-chart-wrap"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={[{ name: 'Completed', value: progress.completed }, { name: 'Remaining', value: progress.remaining }]} dataKey="value" innerRadius="72%" outerRadius="91%" stroke="none" startAngle={90} endAngle={-270}><Cell fill="#169a8d" /><Cell fill="#e6edf3" /></Pie><Tooltip /></PieChart></ResponsiveContainer><div className="progress-center"><strong>{percentage}%</strong><span>complete</span></div></div><div className="progress-details"><strong>{summary.completed_tasks} <span>of {summary.total_tasks} tasks</span></strong><p>You’re moving through your care plan one step at a time.</p><div className="progress-legend"><span><i className="legend-teal" /> Completed</span><span><i className="legend-gray" /> Remaining</span></div></div></div>
      </Card>
      <Card className="status-card"><div className="card-head"><div><div className="eyebrow">TASK SNAPSHOT</div><h2>Task status</h2></div><Link to="/tasks" className="icon-link" aria-label="View tasks"><ArrowRight size={17} /></Link></div>
        {summary.total_tasks === 0 ? <EmptyState title="No tasks yet" detail="Add a task to begin your healthcare journey." /> : <div className="status-chart-area"><div className="status-chart"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={getNonZeroStatusRows(taskStatus)} dataKey="value" innerRadius="63%" outerRadius="91%" paddingAngle={4} stroke="none">{taskStatus.map((entry, index) => <Cell key={entry.name} fill={colors[index]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer><div className="status-center"><strong>{summary.total_tasks}</strong><span>tasks</span></div></div><div className="status-legend">{taskStatus.map((entry, index) => <div key={entry.name}><span><i style={{ background: colors[index] }} />{entry.name}</span><strong>{entry.value}</strong></div>)}</div></div>}
      </Card>
    </div>
    <div className="dashboard-grid dashboard-grid-lower">
      <Card className="appointments-card"><div className="card-head"><div><div className="eyebrow">ON YOUR CALENDAR</div><h2>Upcoming appointments</h2></div><span className="card-icon soft-blue"><CalendarDays size={18} /></span></div>
        {data.upcoming_appointments.length ? <div className="appointment-list">{data.upcoming_appointments.map((appointment) => {
          const isApptToday = appointment.due_date === todayYMD
          return <div className={`appointment-row ${isApptToday ? 'appointment-row-today' : ''}`} key={appointment.id}>
            <div className={`calendar-date ${isApptToday ? 'calendar-date-today' : ''}`}>
              <strong>{new Date(`${appointment.due_date}T12:00:00`).getDate()}</strong>
              <span>{isApptToday ? 'TODAY' : new Date(`${appointment.due_date}T12:00:00`).toLocaleDateString('en-IN', { month: 'short' })}</span>
            </div>
            <div className="appointment-copy">
              <div className="appt-title-wrap">
                <strong>{appointment.title}</strong>
                {isApptToday && <span className="task-date-tag tag-today">⚡ TODAY</span>}
              </div>
              <span>{appointment.description || 'Appointment date from your healthcare journey'}</span>
            </div>
            <StatusBadge status={appointment.status} />
          </div>
        })}</div> : <EmptyState icon={CalendarDays} title="Nothing scheduled yet" detail="Confirmed appointments from your care plan will appear here." />}
        <Link to="/journey" className="card-footer-link">Open healthcare journey <ArrowRight size={15} /></Link>
      </Card>
      <Card className="reports-card"><div className="card-head"><div><div className="eyebrow">DOCUMENT CHECKLIST</div><h2>Report readiness</h2></div><Link to="/reports" className="icon-link" aria-label="View report readiness"><ArrowRight size={17} /></Link></div>
        <div className="reports-summary"><span className="report-summary-icon"><FileCheck2 size={19} /></span><div><strong>{data.reports.filter((r) => ['Available', 'Verified'].includes(r.status)).length} of {summary.required_reports} reports available</strong><span>Document availability only</span></div></div>
        <div className="mini-report-list">{data.reports.map((report) => <div className="mini-report" key={report.id}><FileText size={15} /><span>{report.name}</span><StatusBadge status={report.status} /></div>)}</div>
        <Link to="/reports" className="card-footer-link">Open report checklist <ArrowRight size={15} /></Link>
      </Card>
      <Card className="activity-card"><div className="card-head"><div><div className="eyebrow">RECENT UPDATES</div><h2>Notifications</h2></div><Link to="/notifications" className="text-link">See all <ChevronRight size={16} /></Link></div>
        {data.recent_notifications.length ? <div className="activity-list">{data.recent_notifications.map((n) => {
          const isNotificationToday = n.title?.includes('TODAY') || n.message?.includes('today') || n.message?.includes('TODAY')
          return <div className={`activity-row ${isNotificationToday ? 'activity-row-today' : ''}`} key={n.id}>
            <span className={`activity-dot activity-${n.kind} ${isNotificationToday ? 'dot-pulse' : ''}`} />
            <div>
              <div className="activity-title-wrap">
                <strong>{n.title}</strong>
                {isNotificationToday && <span className="task-date-tag tag-today mini-tag">TODAY</span>}
              </div>
              <p>{n.message}</p>
              <small>{new Date(n.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</small>
            </div>
          </div>
        })}</div> : <EmptyState title="You’re all caught up" detail="Journey reminders will show up here." />}
      </Card>
      <Card className="caregiver-card"><div className="caregiver-card-top"><div className="caregiver-illustration"><HeartHandshake size={23} /></div><div><div className="eyebrow">CARE, SHARED</div><h2>Caregiver activity</h2></div><Link to="/caregivers" className="icon-link" aria-label="Manage caregivers"><ArrowRight size={16} /></Link></div>
        {data.caregiver_activity.length ? <div className="care-activity-list">{data.caregiver_activity.slice(0, 3).map((activity) => <div className="care-activity-row" key={activity.task_id}><span className="caregiver-mini-avatar"><UserRound size={13} /></span><div><strong>{activity.caregiver_name}</strong><small>{activity.task_title}</small></div><StatusBadge status={activity.status} /></div>)}</div> : <div className="care-empty"><p>{summary.caregiver_count ? 'No caregiver tasks have been assigned yet.' : 'Connect a caregiver to share selected journey tasks.'}</p><Link to="/caregivers" className="button button-secondary">Manage caregivers <ArrowRight size={15} /></Link></div>}
      </Card>
    </div>
    <div className="dashboard-footnote">CareBridge AI helps organize clinician-provided instructions. It does not diagnose or replace your healthcare team.</div>
  </div>
}

function StatCard({ label, value, foot, icon: Icon, tint }) { return <div className="stat-card"><div className={`stat-icon tint-${tint}`}><Icon size={18} /></div><div className="stat-value">{value}</div><div className="stat-label">{label}</div><div className="stat-foot">{foot}</div></div> }
