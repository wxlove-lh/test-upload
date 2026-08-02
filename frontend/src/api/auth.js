import api from './index'

export function loginApi(phone, password) {
  return api.post('/auth/login', { phone, password })
}

export function registerApi(phone, password, industry, referral_code) {
  return api.post('/auth/register', { phone, password, industry, referral_code })
}

export function getMeApi() {
  return api.get('/auth/me')
}
