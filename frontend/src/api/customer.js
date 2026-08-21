import api from './index'

// 客户台账相关接口
export function listCustomers(params = {}) {
  return api.get('/customers', { params })
}

export function createCustomer(data) {
  return api.post('/customers', data)
}

export function updateCustomer(id, data) {
  return api.put(`/customers/${id}`, data)
}

export function deleteCustomer(id) {
  return api.delete(`/customers/${id}`)
}
