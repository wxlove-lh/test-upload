<template>
  <div class="page-container">
    <van-nav-bar title="记账" />

    <van-tabs v-model:active="activeTab" sticky>
      <!-- Tab 1: 拍照记账 -->
      <van-tab title="拍照记账">
        <ReceiptUploader @refresh="loadTodayData" />
      </van-tab>

      <!-- Tab 2: 语音记账 -->
      <van-tab title="语音记账">
        <VoiceRecorder />
      </van-tab>

      <!-- Tab 3: 今日快览 -->
      <van-tab title="今日快览">
        <div class="today-list">
          <van-pull-refresh v-model="refreshing" @refresh="onPullRefresh">
            <van-empty v-if="!loading && transactions.length === 0" description="今日暂无记录" />
            <van-list
              v-else
              :loading="loading"
              :finished="finished"
              finished-text="没有更多了"
              @load="loadMore"
            >
              <van-cell
                v-for="item in transactions"
                :key="item.id"
                :title="item.category || '未分类'"
                :label="`${item.transaction_date} · ${item.supplier || '-'} · ${item.notes || ''}`"
                class="transaction-cell"
              >
                <template #value>
                  <span :class="item.type === 'income' ? 'amount-income' : 'amount-expense'">
                    {{ item.type === 'income' ? '+' : '-' }}¥{{ formatAmount(item.amount) }}
                  </span>
                </template>
              </van-cell>
            </van-list>
          </van-pull-refresh>
        </div>

        <!-- 底部汇总 -->
        <div class="summary-bar">
          <div class="summary-item">
            <span class="summary-label">收入</span>
            <span class="summary-value income">¥{{ formatAmount(summary.total_income) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">支出</span>
            <span class="summary-value expense">¥{{ formatAmount(summary.total_expense) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">净利润</span>
            <span class="summary-value" :class="summary.total_profit >= 0 ? 'income' : 'expense'">
              ¥{{ formatAmount(summary.total_profit) }}
            </span>
          </div>
        </div>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getTransactions, getTransactionSummary } from '@/api/transaction'
import { useBookkeepingStore } from '@/stores/bookkeeping'
import ReceiptUploader from '@/components/ReceiptUploader.vue'
import VoiceRecorder from '@/components/VoiceRecorder.vue'

const store = useBookkeepingStore()
const activeTab = ref(0)

// 今日快览数据
const transactions = ref([])
const summary = ref({ total_income: 0, total_expense: 0, total_profit: 0 })
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)

function getToday() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function loadTodayData() {
  page.value = 1
  transactions.value = []
  finished.value = false
  await loadMore()
  await loadSummary()
}

async function loadMore() {
  loading.value = true
  try {
    const today = getToday()
    const res = await getTransactions({
      start_date: today,
      end_date: today,
      page: page.value,
      per_page: 20
    })
    if (res.items && res.items.length > 0) {
      transactions.value.push(...res.items)
    }
    if (page.value >= res.pages) {
      finished.value = true
    } else {
      page.value++
    }
  } catch (e) {
    finished.value = true
  } finally {
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const today = getToday()
    const res = await getTransactionSummary({
      start_date: today,
      end_date: today
    })
    summary.value = {
      total_income: res.total_income || 0,
      total_expense: res.total_expense || 0,
      total_profit: res.total_profit || 0
    }
  } catch (e) {
    // ignore
  }
}

function onPullRefresh() {
  refreshing.value = false
  loadTodayData()
}

function formatAmount(val) {
  const num = parseFloat(val) || 0
  return num.toFixed(2)
}

// 切到今日快览tab时自动加载
watch(activeTab, (val) => {
  if (val === 2 && transactions.value.length === 0) {
    loadTodayData()
  }
})

onMounted(() => {
  // 如果初始就在今日快览tab则加载
  if (activeTab.value === 2) {
    loadTodayData()
  }
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 50px; /* 底部tabbar空间 */
}

.today-list {
  min-height: 300px;
}

.transaction-cell :deep(.van-cell__value) {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.amount-income {
  color: #07c160;
  font-size: 16px;
  font-weight: bold;
}

.amount-expense {
  color: #ee0a24;
  font-size: 16px;
  font-weight: bold;
}

.summary-bar {
  position: fixed;
  bottom: 50px; /* tabbar高度 */
  left: 0;
  right: 0;
  display: flex;
  background: #fff;
  padding: 12px 16px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.summary-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: #969799;
}

.summary-value {
  font-size: 16px;
  font-weight: bold;
}

.summary-value.income {
  color: #07c160;
}

.summary-value.expense {
  color: #ee0a24;
}
</style>
