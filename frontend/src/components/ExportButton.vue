<template>
  <van-button
    type="primary"
    size="small"
    icon="down"
    :loading="exporting"
    loading-text="导出中..."
    @click="handleExport"
  >
    导出Excel
  </van-button>
</template>

<script setup>
import { ref } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { exportTransactions } from '@/api/transaction'
import { downloadExport } from '@/utils/export'

const props = defineProps({
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' },
  category: { type: String, default: '' },
  type: { type: String, default: '' },
  totalCount: { type: Number, default: 0 },
})

const exporting = ref(false)

async function handleExport() {
  // 大数据量提示
  if (props.totalCount >= 1000) {
    try {
      await showConfirmDialog({
        title: '数据量较大',
        message: `当前筛选结果共 ${props.totalCount} 条记录，导出可能需要较长时间，确定要继续吗？`,
        confirmButtonText: '确定导出',
        cancelButtonText: '取消',
      })
    } catch {
      return // 用户取消
    }
  }

  exporting.value = true
  try {
    const params = {}
    if (props.startDate) params.start_date = props.startDate
    if (props.endDate) params.end_date = props.endDate
    if (props.category) params.category = props.category
    if (props.type) params.type = props.type

    const response = await exportTransactions(params)
    // 从blob中下载
    downloadExport(response)
    showToast({ message: '导出成功', type: 'success' })
  } catch (error) {
    showToast('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}
</script>
