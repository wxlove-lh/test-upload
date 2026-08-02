<template>
  <div class="calendar-view">
    <van-calendar
      type="range"
      :show-confirm="false"
      :poppable="false"
      :default-date="defaultDate"
      @select="onDateSelect"
    >
      <template #day-content="{ date }">
        <div class="day-cell">
          <span class="day-number">{{ date.getDate() }}</span>
          <div v-if="getDayData(date)" class="day-data">
            <span class="income">{{ formatMini(getDayData(date).income) }}</span>
            <span class="expense">{{ formatMini(getDayData(date).expense) }}</span>
          </div>
        </div>
      </template>
    </van-calendar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDailyData } from '@/api/analytics'

const emit = defineEmits(['date-select'])

const defaultDate = ref(new Date())
const dailyMap = ref({})

// 格式化迷你金额（日历格子内用）
function formatMini(val) {
  if (val === undefined || val === null) return '--'
  const num = Number(val)
  if (Math.abs(num) >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (Math.abs(num) >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toFixed(0)
}

// 根据日期获取当天数据
function getDayData(date) {
  const key = formatDateKey(date)
  return dailyMap.value[key] || null
}

// 日期格式化为 YYYY-MM-DD
function formatDateKey(date) {
  if (!date) return ''
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// 获取当月及前后月的日历数据
async function fetchMonthData(date) {
  try {
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    // 获取当月第一天和最后一天
    const startDate = new Date(year, month - 1, 1)
    const endDate = new Date(year, month, 0)
    const start = formatDateKey(startDate)
    const end = formatDateKey(endDate)

    const res = await getDailyData({ start_date: start, end_date: end })
    const map = {}
    if (res && Array.isArray(res.data)) {
      res.data.forEach(item => {
        map[item.date] = item
      })
    } else if (res && typeof res === 'object' && !Array.isArray(res)) {
      // 兼容直接返回map格式
      Object.assign(map, res.data || res)
    }
    dailyMap.value = map
  } catch (e) {
    console.error('获取日历数据失败:', e)
    dailyMap.value = {}
  }
}

function onDateSelect(dates) {
  if (dates && dates.length === 2) {
    emit('date-select', {
      start: formatDateKey(dates[0]),
      end: formatDateKey(dates[1])
    })
  }
}

onMounted(() => {
  fetchMonthData(new Date())
})

// 暴露刷新方法
defineExpose({
  refresh: () => fetchMonthData(new Date())
})
</script>

<style scoped>
.calendar-view {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}

.day-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  padding: 2px 0;
}

.day-number {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.day-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  margin-top: 2px;
}

.day-data .income {
  font-size: 9px;
  color: #07c160;
  line-height: 1.2;
}

.day-data .expense {
  font-size: 9px;
  color: #ee0a24;
  line-height: 1.2;
}

:deep(.van-calendar__day) {
  height: 56px;
}
</style>
