<template>
  <div class="ledger-page">
    <van-nav-bar title="台账" />

    <!-- 筛选区 -->
    <div class="filter-bar">
      <!-- 日期范围 -->
      <van-button
        size="small"
        plain
        icon="calendar-o"
        class="date-btn"
        @click="showCalendar = true"
      >
        {{ dateBtnText }}
      </van-button>

      <!-- 分类筛选 -->
      <van-dropdown-menu class="filter-dropdown" active-color="var(--brand)">
        <van-dropdown-item v-model="filterCategory" :options="categoryOptions" />
        <van-dropdown-item v-model="filterType" :options="typeOptions" />
      </van-dropdown-menu>

      <!-- 查询按钮 -->
      <van-button type="primary" size="small" @click="handleQuery">查询</van-button>
    </div>

    <!-- 数据列表 -->
    <div class="list-container">
      <TransactionList
        ref="listRef"
        :start-date="appliedStartDate"
        :end-date="appliedEndDate"
        :category="appliedCategory"
        :type="appliedType"
        @edit="openEdit"
        @voucher="openVoucher"
        @total-change="onTotalChange"
      />
    </div>

    <!-- 底部汇总栏 -->
    <div class="summary-bar">
      <div class="summary-data">
        <span class="summary-item income">
          收入 <strong>¥{{ formatAmount(summary.total_income) }}</strong>
        </span>
        <span class="summary-item expense">
          支出 <strong>¥{{ formatAmount(summary.total_expense) }}</strong>
        </span>
        <span class="summary-item profit">
          利润 <strong>¥{{ formatAmount(summary.total_profit) }}</strong>
        </span>
      </div>
      <ExportButton
        :start-date="appliedStartDate"
        :end-date="appliedEndDate"
        :category="appliedCategory"
        :type="appliedType"
        :total-count="totalCount"
      />
    </div>

    <!-- 日历弹窗 -->
    <van-calendar
      v-model:show="showCalendar"
      type="range"
      :max-date="maxDate"
      @confirm="onCalendarConfirm"
    />

    <!-- 修改弹窗 -->
    <EditTransaction
      v-model:show="showEdit"
      :transaction="currentTransaction"
      @refresh="handleRefresh"
    />

    <!-- 凭证弹窗 -->
    <VoucherPanel
      v-model:show="showVoucher"
      :transaction="currentTransaction"
      @uploaded="handleRefresh"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TransactionList from '@/components/TransactionList.vue'
import EditTransaction from '@/components/EditTransaction.vue'
import ExportButton from '@/components/ExportButton.vue'
import VoucherPanel from '@/components/VoucherPanel.vue'
import { getTransactionSummary } from '@/api/transaction'

// ─── 筛选条件 ───
const filterStartDate = ref('')
const filterEndDate = ref('')
const filterCategory = ref('')
const filterType = ref('')

// 已应用的筛选条件（点"查询"后生效）
const appliedStartDate = ref('')
const appliedEndDate = ref('')
const appliedCategory = ref('')
const appliedType = ref('')

const showCalendar = ref(false)
const maxDate = new Date()

// ─── 数据 ───
const listRef = ref(null)
const totalCount = ref(0)
const currentTransaction = ref(null)
const showEdit = ref(false)
const showVoucher = ref(false)

const summary = ref({
  total_income: 0,
  total_expense: 0,
  total_profit: 0,
  count: 0,
})

// ─── 选项 ───
const categoryOptions = [
  { text: '全部分类', value: '' },
  { text: '餐饮', value: '餐饮' },
  { text: '交通', value: '交通' },
  { text: '购物', value: '购物' },
  { text: '娱乐', value: '娱乐' },
  { text: '医疗', value: '医疗' },
  { text: '教育', value: '教育' },
  { text: '住房', value: '住房' },
  { text: '通讯', value: '通讯' },
  { text: '工资', value: '工资' },
  { text: '奖金', value: '奖金' },
  { text: '投资收益', value: '投资收益' },
  { text: '其他', value: '其他' },
]

const typeOptions = [
  { text: '全部', value: '' },
  { text: '收入', value: 'income' },
  { text: '支出', value: 'expense' },
]

// ─── 计算属性 ───
const dateBtnText = computed(() => {
  if (filterStartDate.value && filterEndDate.value) {
    return `${filterStartDate.value} ~ ${filterEndDate.value}`
  }
  return '选择日期范围'
})

// ─── 方法 ───
function formatAmount(val) {
  return parseFloat(val || 0).toFixed(2)
}

/** 日历确认 */
function onCalendarConfirm([start, end]) {
  filterStartDate.value = formatDate(start)
  filterEndDate.value = formatDate(end)
  showCalendar.value = false
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/** 查询 */
function handleQuery() {
  appliedStartDate.value = filterStartDate.value
  appliedEndDate.value = filterEndDate.value
  appliedCategory.value = filterCategory.value
  appliedType.value = filterType.value
  fetchSummary()
}

/** 获取汇总数据 */
async function fetchSummary() {
  try {
    const params = {}
    if (appliedStartDate.value) params.start_date = appliedStartDate.value
    if (appliedEndDate.value) params.end_date = appliedEndDate.value
    const res = await getTransactionSummary(params)
    summary.value = res
  } catch {
    // 错误由拦截器处理
  }
}

/** 列表总数变化 */
function onTotalChange(count) {
  totalCount.value = count
}

/** 打开编辑弹窗 */
function openEdit(item) {
  currentTransaction.value = { ...item }
  showEdit.value = true
}

/** 打开凭证弹窗 */
function openVoucher(item) {
  currentTransaction.value = { ...item }
  showVoucher.value = true
}

/** 编辑保存后刷新 */
function handleRefresh() {
  if (listRef.value) {
    listRef.value.reload()
  }
  fetchSummary()
}

/** 初始加载 */
onMounted(() => {
  fetchSummary()
})
</script>

<style scoped>
.ledger-page {
  min-height: 100vh;
  background-color: var(--bg);
  padding-bottom: 120px; /* tabbar + summary-bar */
}

/* ── 筛选栏 ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--card);
  border-bottom: 1px solid var(--line);
}

.date-btn {
  flex-shrink: 0;
  font-size: 12px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.filter-dropdown {
  flex: 1;
  min-width: 0;
}

/* ── 列表区 ── */
.list-container {
  min-height: 300px;
}

/* ── 底部汇总栏 ── */
.summary-bar {
  position: fixed;
  bottom: 50px; /* tabbar高度 */
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--card);
  border-top: 1px solid var(--line);
  z-index: 100;
}

.summary-data {
  display: flex;
  gap: 16px;
  flex: 1;
}

.summary-item {
  font-size: 12px;
  color: var(--ink-2);
}

.summary-item strong {
  display: block;
  font-size: 14px;
  margin-top: 2px;
}

.summary-item.income strong {
  color: var(--up);
}

.summary-item.expense strong {
  color: var(--down);
}

.summary-item.profit strong {
  color: var(--brand);
}
</style>
