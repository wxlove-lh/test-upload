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
