import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_URL
  || (import.meta.env.DEV ? 'http://localhost:8000/api' : '')

const api = axios.create({ baseURL: apiBaseUrl })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('carebridge_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function errorMessage(error) {
  if (!error?.response) {
    if (error?.code === 'ERR_NETWORK' || error?.message === 'Network Error') {
      return import.meta.env.DEV
        ? 'Cannot connect to backend server. Please make sure the backend API is running on port 8000.'
        : 'Cannot connect to the deployed backend API. Check the GitHub Actions VITE_API_URL configuration and Render service status.'
    }
  }
  return error?.response?.data?.detail || error?.message || 'Something went wrong. Please try again.'
}
export default api
