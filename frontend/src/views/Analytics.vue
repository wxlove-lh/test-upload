<template>
  <div class="analytics-page">
    <van-nav-bar title="数据分析" />

    <div class="page-content">
      <!-- 日历视图 -->
      <CalendarView ref="calendarRef" @date-select="onCalendarDateSelect" />

      <!-- 时间维度切换 -->
      <div class="dimension-section">
        <van-tabs
          v-model:active="activeDimension"
          shrink
          @change="onDimensionChange"
        >
          <van-tab title="日" name="day" />
          <van-tab title="周" name="week" />
          <van-tab title="月" name="month" />
          <van-tab title="年" name="year" />
          <van-tab title="自定义" name="custom" />
        </van-tabs>
      </div>

      <div class="chart-type-section">
        <div class="btn-group">
          <van-button
            size="small"
            :type="chartType === 'bar' ? 'primary' : 'default'"
            @click="chartType = 'bar'"
          >柱状图</van-button>
          <van-button
            size="small"
            :type="chartType === 'line' ? 'primary' : 'default'"
            @click="chartType = 'line'"
          >折线图</van-button>
          <van-button
            size="small"
            :type="chartType === 'pie' ? 'primary' : 'default'"
            @click="chartType = 'pie'"
          >饼图</van-button>
          <van-button
            size="small"
            :type="chartType === 'table' ? 'primary' : 'default'"
            @click="chartType = 'table'"
          >表格</van-button>
        </div>
      </div>

      <!-- 图表面板 -->
      <ChartPanel
        ref="chartRef"
        :chart-type="chartType"
        :time-dimension="timeDimension"
        :date-range="dateRange"
      />

      <!-- 分析数据区 -->
      <div class="analysis-section">
        <!-- 数字卡片 -->
        <van-grid :column-num="3" :border="false" class="summary-grid">
          <van-grid-item>
            <div class="summary-card">
              <div class="summary-label">总收入</div>
              <div class="summary-value income">{{ formatAmount(summary.totalIncome) }}</div>
            </div>
          </van-grid-item>
          <van-grid-item>
            <div class="summary-card">
              <div class="summary-label">总支出</div>
              <div class="summary-value expense">{{ formatAmount(summary.totalExpense) }}</div>
            </div>
          </van-grid-item>
          <van-grid-item>
            <div class="summary-card">
              <div class="summary-label">总利润</div>
              <div :class="['summary-value', summary.totalProfit >= 0 ? 'income' : 'expense']">
                {{ formatAmount(summary.totalProfit) }}
              </div>
            </div>
          </van-grid-item>
        </van-grid>

        <!-- 同比/环比数据 -->
        <div class="comparison-section" v-if="comparison.yoy || comparison.mom">
          <div class="comparison-block" v-if="comparison.yoy">
            <div class="comparison-title">同比</div>
            <div class="comparison-items">
              <span class="comparison-item">
                收入 <span :class="getTrendClass(comparison.yoy.income)">
                  {{ formatPercent(comparison.yoy.income) }}
                </span>
              </span>
              <span class="comparison-item">
                支出 <span :class="getTrendClass(comparison.yoy.expense)">
                  {{ formatPercent(comparison.yoy.expense) }}
                </span>
              </span>
              <span class="comparison-item">
                利润 <span :class="getTrendClass(comparison.yoy.profit)">
                  {{ formatPercent(comparison.yoy.profit) }}
                </span>
              </span>
            </div>
          </div>

          <div class="comparison-block" v-if="comparison.mom">
            <div class="comparison-title">环比</div>
            <div class="comparison-items">
              <span class="comparison-item">
                收入 <span :class="getTrendClass(comparison.mom.income)">
                  {{ formatPercent(comparison.mom.income) }}
                </span>
              </span>
              <span class="comparison-item">
                支出 <span :class="getTrendClass(comparison.mom.expense)">
                  {{ formatPercent(comparison.mom.expense) }}
                </span>
              </span>
              <span class="comparison-item">
                利润 <span :class="getTrendClass(comparison.mom.profit)">
                  {{ formatPercent(comparison.mom.profit) }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 自定义日期范围弹窗 -->
    <van-calendar
      v-model:show="showDatePicker"
      type="range"
      :min-date="minDate"
      :max-date="maxDate"
      @confirm="onDateConfirm"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { getComparison } from '@/api/analytics'
import CalendarView from '@/components/CalendarView.vue'
import ChartPanel from '@/components/ChartPanel.vue'

const store = useAnalyticsStore()

// 状态
const calendarRef = ref(null)
const chartRef = ref(null)
const activeDimension = ref(1) // 默认"周"索引
const timeDimension = ref(store.timeDimension || 'week')
const chartType = ref(store.chartType || 'bar')
const dateRange = ref({ ...store.dateRange })
const showDatePicker = ref(false)

const minDate = new Date(2020, 0, 1)
const maxDate = new Date()

// 汇总数据
const summary = reactive({
  totalIncome: 0,
  totalExpense: 0,
  totalProfit: 0
})

// 同比/环比数据
const comparison = reactive({
  yoy: null,
  mom: null
})

// 维度名称映射
const dimensionMap = {
  0: 'day',
  1: 'week',
  2: 'month',
  3: 'year',
  4: 'custom'
}

// 金额格式化
function formatAmount(val) {
  if (val === undefined || val === null) return '¥0.00'
  const num = Number(val)
  return '¥' + num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 百分比格式化
function formatPercent(val) {
  if (val === undefined || val === null) return '--'
  const num = Number(val)
  const prefix = num >= 0 ? '+' : ''
  return prefix + num.toFixed(2) + '%'
}

// 获取趋势样式类
function getTrendClass(val) {
  if (val === undefined || val === null) return ''
  return Number(val) >= 0 ? 'trend-up' : 'trend-down'
}

// 维度切换
function onDimensionChange(index) {
  const dim = dimensionMap[index]
  if (dim === 'custom') {
    showDatePicker.value = true
  } else {
    timeDimension.value = dim
    store.timeDimension = dim
  }
}

// 日历日期选择
function onCalendarDateSelect(range) {
  dateRange.value = { start: range.start, end: range.end }
  store.dateRange = { ...dateRange.value }
}

// 自定义日期确认
function onDateConfirm(dates) {
  if (dates && dates.length === 2) {
    const fmt = (d) => {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    }
    dateRange.value = { start: fmt(dates[0]), end: fmt(dates[1]) }
    timeDimension.value = 'custom'
    store.timeDimension = 'custom'
    store.dateRange = { ...dateRange.value }
    showDatePicker.value = false
  }
}

// 获取对比数据
async function fetchComparison() {
  try {
    const params = { dimension: timeDimension.value }
    if (timeDimension.value === 'custom') {
      params.start_date = dateRange.value.start
      params.end_date = dateRange.value.end
    }
    const res = await getComparison(params)
    const data = res.data || res

    summary.totalIncome = data.total_income ?? data.totalIncome ?? 0
    summary.totalExpense = data.total_expense ?? data.totalExpense ?? 0
    summary.totalProfit = data.total_profit ?? data.totalProfit ?? 0
    comparison.yoy = data.yoy || data.year_over_year || null
    comparison.mom = data.mom || data.month_over_month || null
  } catch (e) {
    console.error('获取对比数据失败:', e)
  }
}

// 监听维度变化，重新获取对比数据
watch(
  () => [timeDimension.value, dateRange.value],
  () => {
    fetchComparison()
  },
  { deep: true }
)

onMounted(() => {
  fetchComparison()
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background-color: var(--bg);
}

.page-content {
  padding: 12px;
  padding-bottom: 80px;
}

/* 维度切换 */
.dimension-section {
  background: var(--card);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-1);
}

/* 图表类型切换 */
.chart-type-section {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.chart-type-section .btn-group {
  display: flex;
  width: 100%;
  gap: 0;
}

.chart-type-section .btn-group .van-button {
  flex: 1;
  font-size: 13px;
  border-radius: 0;
}

.chart-type-section .btn-group .van-button:first-child {
  border-radius: 4px 0 0 4px;
}

.chart-type-section .btn-group .van-button:last-child {
  border-radius: 0 4px 4px 0;
}

/* 分析数据区 */
.analysis-section {
  margin-top: 12px;
}

.summary-grid {
  background: var(--card);
  border-radius: var(--radius-sm);
  padding: 16px 0;
  box-shadow: var(--shadow-1);
}

.summary-card {
  text-align: center;
}

.summary-label {
  font-size: 13px;
  color: var(--ink-3);
  margin-bottom: 6px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
}

.summary-value.income {
  color: var(--up);
}

.summary-value.expense {
  color: var(--down);
}

/* 同比环比 */
.comparison-section {
  background: var(--card);
  border-radius: var(--radius-sm);
  padding: 16px;
  margin-top: 12px;
  box-shadow: var(--shadow-1);
}

.comparison-block {
  margin-bottom: 12px;
}

.comparison-block:last-child {
  margin-bottom: 0;
}

.comparison-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 8px;
}

.comparison-items {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.comparison-item {
  font-size: 13px;
  color: var(--ink-2);
}

.trend-up {
  color: var(--up);
  font-weight: 500;
}

.trend-down {
  color: var(--down);
  font-weight: 500;
}
</style>
