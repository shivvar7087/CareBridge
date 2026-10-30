import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth'
import AppShell from './components/AppShell'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import Journey from './pages/Journey'
import Documents from './pages/Documents'
import Tasks from './pages/Tasks'
import Reports from './pages/Reports'
import Caregivers from './pages/Caregivers'
import Barriers from './pages/Barriers'
import Notifications from './pages/Notifications'
import SettingsPage from './pages/SettingsPage'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="screen-loader"><span className="spinner" /> Loading your workspace…</div>
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/" element={<Protected><AppShell /></Protected>}>
      <Route index element={<Dashboard />} />
      <Route path="journey" element={<Journey />} />
      <Route path="documents" element={<Documents />} />
      <Route path="tasks" element={<Tasks />} />
      <Route path="reports" element={<Reports />} />
      <Route path="caregivers" element={<Caregivers />} />
      <Route path="barriers" element={<Barriers />} />
      <Route path="notifications" element={<Notifications />} />
      <Route path="settings" element={<SettingsPage />} />
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
}
