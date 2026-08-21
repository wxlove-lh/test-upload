<template>
  <div class="transaction-list">
    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多了"
      loading-text="正在加载数据，请稍候…"
      @load="onLoad"
    >
      <van-cell
        v-for="item in transactions"
        :key="item.id"
        class="transaction-item"
        clickable
        @click="$emit('edit', item)"
      >
        <template #title>
          <div class="transaction-header">
            <span class="date">{{ item.transaction_date }}</span>
            <van-tag v-if="item.category" type="primary" plain size="medium" class="category-tag">
              {{ item.category }}
            </van-tag>
          </div>
        </template>
        <template #label>
          <div class="transaction-info">
            <span class="supplier">{{ item.supplier || '未知供应商' }}</span>
            <van-tag
              :type="statusTagType(item.status)"
              size="medium"
              class="status-tag"
            >
              {{ statusText(item.status) }}
            </van-tag>
            <span
              class="voucher-link"
              @click.stop="$emit('voucher', item)"
            >
              <van-icon name="photo-o" />
              <span v-if="item.voucher_urls && item.voucher_urls.length > 0">
                凭证({{ item.voucher_urls.length }})
              </span>
              <span v-else>凭证</span>
            </span>
          </div>
        </template>
        <template #value>
          <span class="amount" :class="item.type">
            {{ item.type === 'income' ? '+' : '-' }}¥{{ formatAmount(item.amount) }}
          </span>
        </template>
      </van-cell>

      <!-- 空状态 -->
      <van-empty
        v-if="!loading && finished && transactions.length === 0"
        description="暂无交易记录"
      />
    </van-list>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getTransactions } from '@/api/transaction'

const props = defineProps({
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' },
  category: { type: String, default: '' },
  type: { type: String, default: '' },
})

const emit = defineEmits(['edit', 'voucher', 'totalChange'])

const transactions = ref([])
const loading = ref(false)
const finished = ref(false)
const page = ref(1)
const totalCount = ref(0)

/** 格式化金额 */
function formatAmount(amount) {
  return parseFloat(amount || 0).toFixed(2)
}

/** 状态文字 */
function statusText(status) {
  const map = {
    confirmed: '已确认',
    modified: '已修改',
    pending: '待确认',
  }
  return map[status] || status
}

/** 状态标签类型 */
function statusTagType(status) {
  const map = {
    confirmed: 'success',
    modified: 'warning',
    pending: 'default',
  }
  return map[status] || 'default'
}

/** 加载一页数据 */
async function onLoad() {
  try {
    const params = {
      page: page.value,
      per_page: 20,
    }
    if (props.startDate) params.start_date = props.startDate
    if (props.endDate) params.end_date = props.endDate
    if (props.category) params.category = props.category
    if (props.type) params.type = props.type

    const res = await getTransactions(params)
    const items = res.items || []

    if (page.value === 1) {
      transactions.value = items
    } else {
      transactions.value.push(...items)
    }

    totalCount.value = res.total || 0
    emit('totalChange', totalCount.value)

    if (transactions.value.length >= totalCount.value || items.length < 20) {
      finished.value = true
    } else {
      page.value++
    }
  } catch (error) {
    finished.value = true
  } finally {
    loading.value = false
  }
}

/** 重置列表并重新加载 */
function reload() {
  page.value = 1
  transactions.value = []
  finished.value = false
  loading.value = true
  // 手动触发加载，van-list 不会仅因 loading 变 true 就自动触发 @load
  onLoad()
}

/** 暴露 reload 给父组件 */
defineExpose({ reload })

/** 监听筛选条件变化自动重新查询 */
watch(
  () => [props.startDate, props.endDate, props.category, props.type],
  () => {
    reload()
  }
)
</script>

<style scoped>
.transaction-list {
  background: #fff;
}

.transaction-item {
  border-bottom: 1px solid #f5f5f5;
}

.transaction-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.transaction-header .date {
  font-size: 14px;
  color: #333;
}

.category-tag {
  flex-shrink: 0;
}

.transaction-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.transaction-info .supplier {
  font-size: 12px;
  color: #999;
}

.status-tag {
  flex-shrink: 0;
}

.voucher-link {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #1989fa;
  cursor: pointer;
  padding: 2px 6px;
  background: #e8f4ff;
  border-radius: 4px;
  flex-shrink: 0;
}

.amount {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.amount.income {
  color: #07c160;
}

.amount.expense {
  color: #ee0a24;
}
</style>
