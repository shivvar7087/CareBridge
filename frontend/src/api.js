import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api' })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('carebridge_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function errorMessage(error) {
  if (!error?.response) {
    if (error?.code === 'ERR_NETWORK' || error?.message === 'Network Error') {
      return 'Cannot connect to backend server. Please make sure the backend API is running on port 8000.'
    }
  }
  return error?.response?.data?.detail || error?.message || 'Something went wrong. Please try again.'
}
export default api
