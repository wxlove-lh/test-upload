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

// 按分类汇总（收入/支出/结余）
export function getCategorySummary(params) {
  return api.get('/analytics/category-summary', { params })
}

// 按季度汇总（year=2026）
export function getQuarterly(params) {
  return api.get('/analytics/quarterly', { params })
}
