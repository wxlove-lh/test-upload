import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/index.js'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  const subscriptionText = computed(() => {
    if (!userInfo.value) return ''
    const planMap = { free: '免费体验', basic: '基础版', advanced: '进阶版', clerk: '文员版' }
    const typeMap = { daily: '日付', monthly: '月付', yearly: '年付' }
    const plan = planMap[userInfo.value.subscription_plan] || '免费体验'
    const type = typeMap[userInfo.value.subscription_type] || ''
    return `${plan}${type ? '（' + type + '）' : ''}`
  })

  const isExpiringSoon = computed(() => {
    if (!userInfo.value?.subscription_expiry) return false
    const expiry = new Date(userInfo.value.subscription_expiry)
    const now = new Date()
    const daysLeft = (expiry - now) / (1000 * 60 * 60 * 24)
    return daysLeft <= 7 && daysLeft > 0
  })

  const daysUntilExpiry = computed(() => {
    if (!userInfo.value?.subscription_expiry) return null
    const expiry = new Date(userInfo.value.subscription_expiry)
    const now = new Date()
    return Math.ceil((expiry - now) / (1000 * 60 * 60 * 24))
  })

  async function login(phone, password) {
    const res = await api.post('/auth/login', { phone, password })
    token.value = res.token
    localStorage.setItem('token', res.token)
    userInfo.value = res.user
    return res
  }

  async function register(phone, password, industry, referral_code) {
    const res = await api.post('/auth/register', { phone, password, industry, referral_code })
    token.value = res.token
    localStorage.setItem('token', res.token)
    userInfo.value = res.user
    return res
  }

  async function fetchUserInfo() {
    try {
      const res = await api.get('/auth/me')
      userInfo.value = res.user
    } catch (e) {
      // token无效，清除
      logout()
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token, userInfo, isLoggedIn,
    subscriptionText, isExpiringSoon, daysUntilExpiry,
    login, register, fetchUserInfo, logout
  }
})
