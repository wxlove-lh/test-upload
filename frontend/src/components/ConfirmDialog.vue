<template>
  <van-dialog
    v-model:show="visible"
    title="确认入库"
    :show-cancel-button="false"
    :show-confirm-button="false"
    :close-on-click-overlay="false"
  >
    <div class="confirm-content">
      <div class="field-list">
        <div class="field-item">
          <span class="field-label">交易日期</span>
          <span class="field-value">{{ formData.transaction_date || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">金额</span>
          <span class="field-value amount">¥{{ formData.amount || '0' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">类型</span>
          <span class="field-value" :class="formData.type === 'income' ? 'text-green' : 'text-red'">
            {{ formData.type === 'income' ? '收入' : '支出' }}
          </span>
        </div>
        <div class="field-item">
          <span class="field-label">分类</span>
          <span class="field-value">{{ formData.category || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">供应商</span>
          <span class="field-value">{{ formData.supplier || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">备注</span>
          <span class="field-value">{{ formData.notes || '-' }}</span>
        </div>
      </div>
      <div class="warning-text">确认后无法撤销，请逐条核对</div>
    </div>
    <div class="dialog-actions">
      <van-button plain block class="action-btn" @click="onCancel">返回修改</van-button>
      <van-button type="primary" block class="action-btn" :loading="submitting" @click="onConfirm">
        我已核对，确认入账
      </van-button>
    </div>
  </van-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { createTransaction } from '@/api/transaction'

const props = defineProps({
  formData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:show', 'success'])

const visible = ref(false)
const submitting = ref(false)

function open() {
  visible.value = true
}

function close() {
  visible.value = false
  emit('update:show', false)
}

function onCancel() {
  close()
}

async function onConfirm() {
  submitting.value = true
  try {
    await createTransaction(props.formData)
    showToast('入库成功')
    close()
    emit('success')
  } catch (e) {
    // 错误已在axios拦截器中统一处理
  } finally {
    submitting.value = false
  }
}

defineExpose({ open, close })
</script>

<style scoped>
.confirm-content {
  padding: 16px 20px;
}

.field-list {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 12px 16px;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebedf0;
}

.field-item:last-child {
  border-bottom: none;
}

.field-label {
  font-size: 14px;
  color: #969799;
  flex-shrink: 0;
}

.field-value {
  font-size: 14px;
  color: #323233;
  text-align: right;
  word-break: break-all;
}

.field-value.amount {
  font-size: 18px;
  font-weight: bold;
}

.text-green {
  color: #07c160;
}

.text-red {
  color: #ee0a24;
}

.warning-text {
  color: #ee0a24;
  font-size: 12px;
  text-align: center;
  margin-top: 12px;
}

.dialog-actions {
  display: flex;
  gap: 8px;
  padding: 0 20px 16px;
}

.action-btn {
  flex: 1;
}
</style>
