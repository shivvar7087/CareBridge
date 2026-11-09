import { useEffect, useRef, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity, Bell, CalendarDays, CheckSquare, ChevronDown, ClipboardCheck,
  FileText, HeartHandshake, LayoutDashboard, LifeBuoy, LogOut, Menu,
  Settings, ShieldAlert, ShieldCheck, UserRound, X
} from 'lucide-react'
import { useAuth } from '../auth'
import api from '../api'
import EmergencyModal from './EmergencyModal'
import AiCopilotDrawer from './AiCopilotDrawer'

const navItems = [
  ['/', 'Dashboard', LayoutDashboard],
  ['/journey', 'My Healthcare Journey', Activity],
  ['/documents', 'Documents', FileText],
  ['/tasks', 'My Tasks', CheckSquare],
  ['/reports', 'Report Readiness', ClipboardCheck],
  ['/caregivers', 'Caregivers', HeartHandshake],
  ['/barriers', 'Access Barriers', LifeBuoy],
  ['/notifications', 'Notifications', Bell],
  ['/settings', 'Settings', Settings],
]
const titles = Object.fromEntries(navItems.map(([path, title]) => [path, title]))

export default function AppShell() {
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [emergencyOpen, setEmergencyOpen] = useState(false)
  const [unread, setUnread] = useState(0)
  const location = useLocation()
  const navigate = useNavigate()
  const menuRef = useRef(null)

  useEffect(() => {
    setMobileOpen(false)
    setMenuOpen(false)
  }, [location.pathname])

  useEffect(() => {
    function handleOpenEmergency() {
      setEmergencyOpen(true)
    }
    window.addEventListener('open-emergency-modal', handleOpenEmergency)
    return () => window.removeEventListener('open-emergency-modal', handleOpenEmergency)
  }, [])

  useEffect(() => {
    api.get('/notifications')
      .then(({ data }) => setUnread(data.filter((n) => !n.is_read).length))
      .catch(() => {})
  }, [location.pathname])

  // Close dropdown menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function signOut() {
    logout()
    navigate('/login')
  }

  const userInitial = user?.full_name ? user.full_name[0].toUpperCase() : 'U'

  const sidebar = (
    <>
      <div className="brand-lockup">
        <span className="brand-mark">
          <Activity size={21} strokeWidth={2.6} />
        </span>
        <span style={{ fontWeight: 800, fontSize: 18, letterSpacing: -0.5 }}>CareBridge</span>
        <button
          className="mobile-close"
          onClick={() => setMobileOpen(false)}
          aria-label="Close navigation"
        >
          <X size={19} />
        </button>
      </div>

      <div className="workspace-label">
        {user?.role === 'patient' ? 'PATIENT WORKSPACE' : 'CAREGIVER WORKSPACE'}
      </div>

      <nav className="side-nav">
        {navItems
          .filter(
            ([path]) =>
              user?.role === 'patient' || !['/documents', '/reports'].includes(path)
          )
          .map(([path, label, Icon]) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
              {label === 'Notifications' && unread > 0 && (
                <span className="nav-badge">{unread}</span>
              )}
            </NavLink>
          ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="privacy-card">
          <ShieldCheck size={17} />
          <div>
            <strong>Your information</strong>
            <span>Private & protected</span>
          </div>
        </div>

        <button
          type="button"
          className="profile-switch"
          onClick={() => navigate('/settings')}
          title="Account settings"
        >
          <span className="avatar">{userInitial}</span>
          <span className="profile-info">
            <strong>{user?.full_name || 'My Account'}</strong>
            <small>{user?.role === 'patient' ? 'Patient account' : 'Caregiver account'}</small>
          </span>
          <Settings size={16} />
        </button>
      </div>
    </>
  )

  return (
    <div className="app-frame">
      {mobileOpen && (
        <button
          className="mobile-scrim"
          onClick={() => setMobileOpen(false)}
          aria-label="Close menu"
        />
      )}
      <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
        {sidebar}
      </aside>

      <div className="main-column">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={21} />
          </button>

          <div className="breadcrumb">
            <span>CareBridge</span>
            <span className="crumb-slash">/</span>
            <strong>{titles[location.pathname] || 'Dashboard'}</strong>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="emergency-top-btn"
              onClick={() => setEmergencyOpen(true)}
              title="View In-Case-of-Emergency (ICE) Medical Passport"
            >
              <ShieldAlert size={15} />
              <span>Emergency Card</span>
            </button>

            <span className="secure-pill">
              <ShieldCheck size={14} /> Secure workspace
            </span>

            <button
              className="top-icon"
              onClick={() => navigate('/notifications')}
              aria-label="Notifications"
            >
              <Bell size={18} />
              {unread > 0 && <i />}
            </button>

            {/* INTERACTIVE USER PROFILE DROPDOWN */}
            <div className="user-menu-wrapper" ref={menuRef}>
              <button
                type="button"
                className="top-avatar-btn"
                onClick={() => setMenuOpen(!menuOpen)}
                aria-label="User profile menu"
                aria-expanded={menuOpen}
              >
                <span className="top-avatar">{userInitial}</span>
              </button>

              {menuOpen && (
                <div className="user-dropdown-menu">
                  <div className="dropdown-user-header">
                    <div className="dropdown-avatar-large">
                      {userInitial}
                    </div>
                    <div className="dropdown-user-details">
                      <strong>{user?.full_name || 'CareBridge User'}</strong>
                      <span className="dropdown-user-email">{user?.email}</span>
                      <span className="dropdown-role-badge">
                        {user?.role === 'patient' ? 'Patient' : 'Caregiver'}
                      </span>
                    </div>
                  </div>

                  <div className="dropdown-divider" />

                  <div className="dropdown-nav-links">
                    <button
                      type="button"
                      className="dropdown-item"
                      onClick={() => {
                        setMenuOpen(false)
                        navigate('/settings')
                      }}
                    >
                      <UserRound size={16} />
                      <span>My Profile & Settings</span>
                    </button>

                    <button
                      type="button"
                      className="dropdown-item"
                      onClick={() => {
                        setMenuOpen(false)
                        navigate('/tasks')
                      }}
                    >
                      <CheckSquare size={16} />
                      <span>My Tasks</span>
                    </button>

                    <button
                      type="button"
                      className="dropdown-item"
                      onClick={() => {
                        setMenuOpen(false)
                        setEmergencyOpen(true)
                      }}
                    >
                      <ShieldAlert size={16} />
                      <span>Emergency Medical Passport</span>
                    </button>

                    <button
                      type="button"
                      className="dropdown-item"
                      onClick={() => {
                        setMenuOpen(false)
                        navigate('/notifications')
                      }}
                    >
                      <Bell size={16} />
                      <span>Notifications</span>
                      {unread > 0 && <span className="dropdown-badge">{unread}</span>}
                    </button>
                  </div>

                  <div className="dropdown-divider" />

                  <button
                    type="button"
                    className="dropdown-item dropdown-logout"
                    onClick={signOut}
                  >
                    <LogOut size={16} />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="page-wrap">
          <Outlet />
        </main>
      </div>

      <EmergencyModal isOpen={emergencyOpen} onClose={() => setEmergencyOpen(false)} />
      <AiCopilotDrawer openEmergencyModal={() => setEmergencyOpen(true)} />
    </div>
  )
}
