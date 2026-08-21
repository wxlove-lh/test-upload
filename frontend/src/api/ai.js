import api from './index'

// 图片识别
export function recognizeReceipt(imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)
  return api.post('/ai/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000 // AI识别可能较慢
  })
}

// 语音记账（预留）
export function voiceToText(audioFile) {
  const formData = new FormData()
  formData.append('audio', audioFile)
  return api.post('/ai/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 一键生成报税底稿
// params: kind(this-month/last-month/this-quarter/last-quarter/this-year/all)、
//         start_date/end_date、use_ai(1 时AI解读)
export function getTaxDraft(params = {}) {
  return api.get('/ai/tax-draft', { params })
}

// 报税日历（真实申报时间表 + 倒计时）
export function getTaxCalendar() {
  return api.get('/tax/calendar')
}

// 自由对话：跟AI商量生意/账务/税务问题
// feature: 当前界面id；history: 本对话框最近的聊天记录（AI有记忆）
export function chatWithAi(message, feature = '', history = []) {
  return api.post('/ai/chat', { message, feature, history }, { timeout: 60000 })
}
