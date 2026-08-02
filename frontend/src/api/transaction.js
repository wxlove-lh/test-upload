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
