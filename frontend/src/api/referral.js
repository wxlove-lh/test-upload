import api from './index'

export function getReferralInfo() {
  return api.get('/referral/info')
}
