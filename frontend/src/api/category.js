import api from './index'

// 分类管理（系统默认 + 自己加的，因人而异可自由调整）
export function getCategories() {
  return api.get('/categories')
}

export function createCategory(data) {
  return api.post('/categories', data)
}

export function updateCategory(id, data) {
  return api.put(`/categories/${id}`, data)
}

export function deleteCategory(id) {
  return api.delete(`/categories/${id}`)
}
