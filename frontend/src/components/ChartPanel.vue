<template>
  <div class="chart-panel">
    <!-- 表格视图 -->
    <div v-if="chartType === 'table'" class="table-view">
      <van-cell-group inset v-if="tableData.length > 0">
        <van-cell
          v-for="item in tableData"
          :key="item.date"
          :title="item.date"
        >
          <template #label>
            <div class="table-row">
              <span class="income-text">收入: {{ formatAmount(item.income) }}</span>
              <span class="expense-text">支出: {{ formatAmount(item.expense) }}</span>
              <span :class="['profit-text', item.profit >= 0 ? 'positive' : 'negative']">
                利润: {{ formatAmount(item.profit) }}
              </span>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
      <van-empty v-else description="暂无数据" />
    </div>

    <!-- ECharts图表视图 -->
    <div v-else ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { getTrendData, getCategoryRatio } from '@/api/analytics'

// ECharts 按需引入
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart, LineChart, PieChart,
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, DatasetComponent, CanvasRenderer
])

const props = defineProps({
  chartType: {
    type: String,
    default: 'bar',
    validator: (v) => ['bar', 'line', 'pie', 'table'].includes(v)
  },
  timeDimension: {
    type: String,
    default: 'week'
  },
  dateRange: {
    type: Object,
    default: () => ({ start: null, end: null })
  }
})

const chartRef = ref(null)
let chartInstance = null
const tableData = ref([])

// 金额格式化：千分位 + 2位小数
function formatAmount(val) {
  if (val === undefined || val === null) return '¥0.00'
  const num = Number(val)
  return '¥' + num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 构建请求参数
function buildParams() {
  const params = { dimension: props.timeDimension }
  if (props.timeDimension === 'custom' && props.dateRange.start && props.dateRange.end) {
    params.start_date = props.dateRange.start
    params.end_date = props.dateRange.end
  }
  return params
}

// 获取趋势数据
async function fetchTrendData() {
  try {
    const res = await getTrendData(buildParams())
    return res.data || res || []
  } catch (e) {
    console.error('获取趋势数据失败:', e)
    return []
  }
}

// 获取分类占比数据
async function fetchCategoryRatio() {
  try {
    const res = await getCategoryRatio(buildParams())
    return res.data || res || []
  } catch (e) {
    console.error('获取分类占比失败:', e)
    return []
  }
}

// 渲染柱状图
function renderBarChart(data) {
  if (!chartInstance) return
  const dates = data.map(d => d.date)
  const profits = data.map(d => Number(d.profit || 0))

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/>利润: ${formatAmount(p.value)}`
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 10 ? 45 : 0,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val) => {
          if (Math.abs(val) >= 10000) return (val / 10000).toFixed(1) + 'w'
          if (Math.abs(val) >= 1000) return (val / 1000).toFixed(1) + 'k'
          return val
        }
      }
    },
    series: [{
      type: 'bar',
      data: profits.map(v => ({
        value: v,
        itemStyle: {
          color: v >= 0 ? '#07c160' : '#ee0a24'
        }
      })),
      barMaxWidth: 30
    }]
  }, true)
}

// 渲染折线图
function renderLineChart(data) {
  if (!chartInstance) return
  const dates = data.map(d => d.date)
  const profits = data.map(d => Number(d.profit || 0))

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/>利润: ${formatAmount(p.value)}`
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 10 ? 45 : 0,
        fontSize: 11
      },
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val) => {
          if (Math.abs(val) >= 10000) return (val / 10000).toFixed(1) + 'w'
          if (Math.abs(val) >= 1000) return (val / 1000).toFixed(1) + 'k'
          return val
        }
      }
    },
    series: [{
      type: 'line',
      data: profits,
      smooth: true,
      lineStyle: { color: '#1989fa', width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(25,137,250,0.3)' },
          { offset: 1, color: 'rgba(25,137,250,0.05)' }
        ])
      },
      itemStyle: { color: '#1989fa' }
    }]
  }, true)
}

// 渲染饼图
function renderPieChart(data) {
  if (!chartInstance) return
  const pieData = data.map(d => ({
    name: d.category_name || d.name || d.category,
    value: Number(d.amount || d.value || 0)
  }))

  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        return `${params.name}<br/>${formatAmount(params.value)} (${params.percent}%)`
      }
    },
    legend: {
      orient: 'horizontal',
      bottom: '0%',
      type: 'scroll',
      textStyle: { fontSize: 11 }
    },
    series: [{
      type: 'pie',
      radius: ['35%', '60%'],
      center: ['50%', '45%'],
      data: pieData,
      label: {
        formatter: '{b}\n{d}%',
        fontSize: 11
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      }
    }]
  }, true)
}

// 加载并渲染表格数据
async function loadTableData() {
  const data = await fetchTrendData()
  tableData.value = Array.isArray(data) ? data : []
}

// 更新图表
async function updateChart() {
  if (props.chartType === 'table') {
    await loadTableData()
    return
  }

  await nextTick()
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  chartInstance.clear()

  if (props.chartType === 'pie') {
    const data = await fetchCategoryRatio()
    renderPieChart(Array.isArray(data) ? data : [])
  } else {
    const data = await fetchTrendData()
    const arr = Array.isArray(data) ? data : []
    if (props.chartType === 'bar') {
      renderBarChart(arr)
    } else if (props.chartType === 'line') {
      renderLineChart(arr)
    }
  }
}

// resize处理
function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(
  () => [props.chartType, props.timeDimension, props.dateRange],
  () => {
    updateChart()
  },
  { deep: true }
)

onMounted(() => {
  updateChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 暴露刷新方法
defineExpose({ refresh: updateChart })
</script>

<style scoped>
.chart-panel {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.table-view {
  max-height: 300px;
  overflow-y: auto;
}

.table-row {
  display: flex;
  gap: 12px;
  font-size: 12px;
  margin-top: 4px;
}

.income-text {
  color: #07c160;
}

.expense-text {
  color: #ee0a24;
}

.profit-text.positive {
  color: #07c160;
}

.profit-text.negative {
  color: #ee0a24;
}
</style>
