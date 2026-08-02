import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAnalyticsStore = defineStore('analytics', () => {
  const timeDimension = ref('week')  // day/week/month/year/custom
  const chartType = ref('bar')       // bar/line/pie/table
  const dateRange = ref({ start: null, end: null })  // 自定义日期范围

  return { timeDimension, chartType, dateRange }
})
