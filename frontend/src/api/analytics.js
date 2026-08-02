import api from './index'

export function getDailyData(params) {
  return api.get('/analytics/daily', { params })
}

export function getTrendData(params) {
  return api.get('/analytics/trend', { params })
}

export function getCategoryRatio(params) {
  return api.get('/analytics/category-ratio', { params })
}

export function getComparison(params) {
  return api.get('/analytics/comparison', { params })
}
