import api from './index'

// 确认入库
export function createTransaction(data) {
  return api.post('/transactions', data)
}

// 分页查账
export function getTransactions(params) {
  return api.get('/transactions', { params })
}

// 修改已入账数据
export function updateTransaction(id, data) {
  return api.put(`/transactions/${id}`, data)
}

// 时间段汇总
export function getTransactionSummary(params) {
  return api.get('/transactions/summary', { params })
}

// 导出Excel
export function exportTransactions(params) {
  return api.get('/transactions/export', { params, responseType: 'blob' })
}

// 上传凭证图片
export function uploadVouchers(id, fileList) {
  const formData = new FormData()
  fileList.forEach(file => formData.append('images', file))
  return api.post(`/transactions/${id}/vouchers`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
}
