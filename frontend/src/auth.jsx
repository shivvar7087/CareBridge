import { createContext, useContext, useEffect, useState } from 'react'
import api from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('carebridge_token')
    if (!token) { setLoading(false); return }
    api.get('/auth/me').then(({ data }) => setUser(data)).catch(() => localStorage.removeItem('carebridge_token')).finally(() => setLoading(false))
  }, [])

  async function login(credentials) {
    const { data } = await api.post('/auth/login', credentials)
    localStorage.setItem('carebridge_token', data.access_token)
    setUser(data.user)
  }
  async function register(details) {
    const { data } = await api.post('/auth/register', details)
    localStorage.setItem('carebridge_token', data.access_token)
    setUser(data.user)
  }
  function logout() {
    localStorage.removeItem('carebridge_token')
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() { return useContext(AuthContext) }
