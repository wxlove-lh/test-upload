import axios from 'axios'
import { showToast } from 'vant'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30秒（AI识别较慢）
})

// 请求拦截器：附加JWT token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      showToast('登录已过期，请重新登录')
    } else {
      showToast(error.response?.data?.message || '网络错误，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default api
