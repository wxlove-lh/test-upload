import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBookkeepingStore = defineStore('bookkeeping', () => {
  // 当前识别结果（待确认的数据）
  const recognitionResult = ref(null)
  const isRecognizing = ref(false)

  // 今日记录
  const todayTransactions = ref([])
  const todaySummary = ref({ total_income: 0, total_expense: 0, total_profit: 0 })

  function setRecognitionResult(result) {
    recognitionResult.value = result
  }

  function clearRecognitionResult() {
    recognitionResult.value = null
  }

  function addToToday(transaction) {
    todayTransactions.value.unshift(transaction)
    // 更新汇总
    if (transaction.type === 'income') {
      todaySummary.value.total_income += parseFloat(transaction.amount)
    } else {
      todaySummary.value.total_expense += parseFloat(transaction.amount)
    }
    todaySummary.value.total_profit = todaySummary.value.total_income - todaySummary.value.total_expense
  }

  function resetToday() {
    todayTransactions.value = []
    todaySummary.value = { total_income: 0, total_expense: 0, total_profit: 0 }
  }

  return {
    recognitionResult, isRecognizing,
    todayTransactions, todaySummary,
    setRecognitionResult, clearRecognitionResult, addToToday, resetToday
  }
})
