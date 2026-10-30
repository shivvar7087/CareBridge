import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Activity, Bell, CalendarDays, CheckSquare, ChevronDown, ClipboardCheck, FileText, HeartHandshake, LayoutDashboard, LifeBuoy, LogOut, Menu, Settings, ShieldCheck, X } from 'lucide-react'
import { useAuth } from '../auth'
import api from '../api'

const navItems = [
  ['/', 'Dashboard', LayoutDashboard], ['/journey', 'My Healthcare Journey', Activity], ['/documents', 'Documents', FileText],
  ['/tasks', 'My Tasks', CheckSquare], ['/reports', 'Report Readiness', ClipboardCheck], ['/caregivers', 'Caregivers', HeartHandshake],
  ['/barriers', 'Access Barriers', LifeBuoy], ['/notifications', 'Notifications', Bell], ['/settings', 'Settings', Settings],
]
const titles = Object.fromEntries(navItems.map(([path, title]) => [path, title]))

export default function AppShell() {
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [unread, setUnread] = useState(0)
  const location = useLocation()
  const navigate = useNavigate()
  useEffect(() => { setMobileOpen(false) }, [location.pathname])
  useEffect(() => { api.get('/notifications').then(({ data }) => setUnread(data.filter((n) => !n.is_read).length)).catch(() => {}) }, [location.pathname])

  function signOut() { logout(); navigate('/login') }
  const sidebar = <>
    <div className="brand-lockup"><span className="brand-mark"><Activity size={21} strokeWidth={2.6} /></span><span>carebridge<span className="brand-ai"> AI</span></span><button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><X size={19} /></button></div>
    <div className="workspace-label">{user?.role === 'patient' ? 'PATIENT WORKSPACE' : 'CAREGIVER WORKSPACE'}</div>
    <nav className="side-nav">
      {navItems.filter(([path]) => user?.role === 'patient' || !['/documents', '/reports'].includes(path)).map(([path, label, Icon]) => <NavLink key={path} to={path} end={path === '/'} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
        <Icon size={18} strokeWidth={1.8} /><span>{label}</span>{label === 'Notifications' && unread > 0 && <span className="nav-badge">{unread}</span>}
      </NavLink>)}
    </nav>
    <div className="sidebar-bottom"><div className="privacy-card"><ShieldCheck size={17} /><div><strong>Your information</strong><span>Private and protected</span></div></div>
      <button className="profile-switch" onClick={signOut}><span className="avatar">{user?.full_name?.[0] || 'C'}</span><span className="profile-info"><strong>{user?.full_name}</strong><small>{user?.role === 'patient' ? 'Patient account' : 'Caregiver account'}</small></span><LogOut size={16} /></button>
    </div>
  </>

  return <div className="app-frame">
    {mobileOpen && <button className="mobile-scrim" onClick={() => setMobileOpen(false)} aria-label="Close menu" />}
    <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>{sidebar}</aside>
    <div className="main-column">
      <header className="topbar"><button className="mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Menu size={21} /></button><div className="breadcrumb"><span>CareBridge</span><span className="crumb-slash">/</span><strong>{titles[location.pathname] || 'Dashboard'}</strong></div>
        <div className="topbar-actions"><span className="secure-pill"><ShieldCheck size={14} /> Secure workspace</span><button className="top-icon" onClick={() => navigate('/notifications')} aria-label="Notifications"><Bell size={18} />{unread > 0 && <i />}</button><span className="top-avatar">{user?.full_name?.[0] || 'C'}</span></div></header>
      <main className="page-wrap"><Outlet /></main>
    </div>
  </div>
}
