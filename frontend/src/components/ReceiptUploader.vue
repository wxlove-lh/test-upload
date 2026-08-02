<template>
  <div class="receipt-uploader">
    <!-- 上传区域 -->
    <div class="upload-section">
      <van-uploader
        v-model="fileList"
        :max-count="1"
        :after-read="onFileRead"
        accept="image/*"
        capture="camera"
        :preview-size="80"
      >
        <div class="upload-trigger">
          <van-icon name="photograph" size="40" color="#1989fa" />
          <span>拍照或选择图片</span>
        </div>
      </van-uploader>
    </div>

    <!-- 开始识别按钮 -->
    <van-button
      v-if="fileList.length > 0 && !hasResult"
      type="primary"
      block
      :loading="isRecognizing"
      loading-text="AI正在识别中，请稍候..."
      class="recognize-btn"
      @click="startRecognize"
    >
      开始识别
    </van-button>

    <!-- 识别中状态 -->
    <div v-if="isRecognizing" class="loading-area">
      <van-loading size="36" vertical>
        AI正在识别中，请稍候...
      </van-loading>
    </div>

    <!-- 识别结果区域 -->
    <div v-if="hasResult" class="result-section">
      <!-- 待核对提示 -->
      <div v-if="matchStatus === 'needs_check'" class="check-banner">
        <van-tag type="danger" size="large">请核对</van-tag>
        <span>AI识别结果存在不一致，请仔细核对各项信息</span>
      </div>

      <!-- 交易日期 -->
      <div class="field-row" :style="getConfidenceBg('date')">
        <van-field
          v-model="form.transaction_date"
          label="交易日期"
          placeholder="YYYY-MM-DD"
          :border="false"
        />
      </div>

      <!-- 金额 -->
      <div class="field-row" :style="getConfidenceBg('amount')">
        <van-field
          v-model="form.amount"
          label="金额"
          type="number"
          placeholder="请输入金额"
          :border="false"
        >
          <template #button>
            <span class="amount-prefix">¥</span>
          </template>
        </van-field>
      </div>

      <!-- 类型 -->
      <div class="field-row">
        <div class="type-selector">
          <span class="type-label">类型</span>
          <van-radio-group v-model="form.type" direction="horizontal">
            <van-radio name="expense">支出</van-radio>
            <van-radio name="income">收入</van-radio>
          </van-radio-group>
        </div>
      </div>

      <!-- 分类 -->
      <div class="field-row" :style="getConfidenceBg('category')">
        <van-field
          v-model="form.category"
          is-link
          readonly
          label="分类"
          placeholder="请选择分类"
          :border="false"
          @click="showCategoryPicker = true"
        />
      </div>

      <!-- 供应商 -->
      <div class="field-row" :style="getConfidenceBg('supplier')">
        <van-field
          v-model="form.supplier"
          label="供应商"
          placeholder="请输入供应商"
          :border="false"
        />
      </div>

      <!-- 备注 -->
      <div class="field-row">
        <van-field
          v-model="form.notes"
          label="备注"
          type="textarea"
          placeholder="请输入备注信息"
          :border="false"
          autosize
        />
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <van-button plain block @click="resetForm">重新上传</van-button>
        <van-button type="primary" block @click="openConfirm">确认入库</van-button>
      </div>
    </div>

    <!-- 分类选择弹窗 -->
    <van-popup v-model:show="showCategoryPicker" position="bottom" round>
      <van-picker
        :columns="currentCategoryColumns"
        @confirm="onCategoryConfirm"
        @cancel="showCategoryPicker = false"
      />
    </van-popup>

    <!-- 确认弹窗 -->
    <ConfirmDialog ref="confirmDialogRef" :form-data="submitData" @success="onSubmitSuccess" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { showToast } from 'vant'
import { recognizeReceipt } from '@/api/ai'
import { useBookkeepingStore } from '@/stores/bookkeeping'
import ConfirmDialog from './ConfirmDialog.vue'

const store = useBookkeepingStore()

// 文件列表
const fileList = ref([])
const imageFile = ref(null)
const isRecognizing = ref(false)
const hasResult = ref(false)
const matchStatus = ref('')

// 表单数据
const form = ref({
  transaction_date: '',
  amount: '',
  type: 'expense',
  category: '',
  supplier: '',
  notes: ''
})

// 各字段置信度
const confidence = ref({
  date: 'high',
  amount: 'high',
  category: 'high',
  supplier: 'high'
})

// 分类选择
const showCategoryPicker = ref(false)

// 默认12个分类（后续接API）
const expenseCategories = [
  '食材', '酒水饮料', '房租', '工资', '水电燃气',
  '耗材餐具', '设备维修', '运输配送', '税费管理', '其他支出'
]
const incomeCategories = ['营业收入', '其他收入']

const currentCategoryColumns = computed(() => {
  return form.value.type === 'income' ? incomeCategories : expenseCategories
})

// 监听类型切换时重置分类
watch(() => form.value.type, () => {
  form.value.category = ''
})

// 提交数据（转换为后端需要的格式）
const submitData = computed(() => ({
  transaction_date: form.value.transaction_date,
  amount: parseFloat(form.value.amount) || 0,
  type: form.value.type,
  category: form.value.category,
  supplier: form.value.supplier,
  notes: form.value.notes,
  ai_confidence: confidence.value.amount,
  ai_match_status: matchStatus.value
}))

const emit = defineEmits(['refresh'])

const confirmDialogRef = ref(null)

function onFileRead(file) {
  imageFile.value = file.file
  hasResult.value = false
}

async function startRecognize() {
  if (!imageFile.value) {
    showToast('请先选择图片')
    return
  }

  isRecognizing.value = true
  store.isRecognizing = true

  try {
    const result = await recognizeReceipt(imageFile.value)

    // 映射AI返回数据到表单
    // AI返回type为中文"支出"/"收入"，需要转为英文
    const typeMap = { '支出': 'expense', '收入': 'income' }
    form.value.transaction_date = result.transaction_date || ''
    form.value.amount = result.amount != null ? String(result.amount) : ''
    form.value.type = typeMap[result.type] || 'expense'
    form.value.category = result.category || ''
    form.value.supplier = result.supplier || ''
    form.value.notes = result.notes || ''

    // 映射置信度
    if (result.confidence) {
      confidence.value = {
        date: result.confidence.date || 'medium',
        amount: result.confidence.amount || 'medium',
        category: result.confidence.category || 'medium',
        supplier: result.confidence.supplier || 'medium'
      }
    }

    matchStatus.value = result.match_status || 'matched'
    hasResult.value = true
    store.setRecognitionResult(result)
  } catch (e) {
    // 错误已在axios拦截器中统一处理
  } finally {
    isRecognizing.value = false
    store.isRecognizing = false
  }
}

function getConfidenceBg(field) {
  const level = confidence.value[field]
  if (level === 'medium') return { backgroundColor: '#fff9e6' }
  if (level === 'low') return { backgroundColor: '#ffe6e6' }
  return {}
}

function onCategoryConfirm({ selectedValues }) {
  form.value.category = selectedValues[0]
  showCategoryPicker.value = false
}

function openConfirm() {
  if (!form.value.transaction_date) {
    showToast('请填写交易日期')
    return
  }
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    showToast('请填写有效金额')
    return
  }
  confirmDialogRef.value?.open()
}

function resetForm() {
  fileList.value = []
  imageFile.value = null
  hasResult.value = false
  matchStatus.value = ''
  form.value = {
    transaction_date: '',
    amount: '',
    type: 'expense',
    category: '',
    supplier: '',
    notes: ''
  }
  confidence.value = { date: 'high', amount: 'high', category: 'high', supplier: 'high' }
  store.clearRecognitionResult()
}

function onSubmitSuccess() {
  resetForm()
  emit('refresh')
}
</script>

<style scoped>
.receipt-uploader {
  padding: 0;
}

.upload-section {
  padding: 16px;
}

.upload-trigger {
  width: 100%;
  height: 120px;
  border: 2px dashed #dcdee0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #fafafa;
  font-size: 14px;
  color: #969799;
}

.recognize-btn {
  margin: 0 16px 16px;
}

.loading-area {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.result-section {
  background: #fff;
  margin: 0 12px 16px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.check-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #fff0f0;
  font-size: 13px;
  color: #ee0a24;
}

.field-row {
  border-bottom: 1px solid #f5f5f5;
  transition: background-color 0.2s;
}

.field-row:last-of-type {
  border-bottom: none;
}

.type-selector {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  gap: 16px;
}

.type-label {
  font-size: 14px;
  color: #646566;
  flex-shrink: 0;
}

.amount-prefix {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
}

.action-buttons {
  display: flex;
  gap: 12px;
  padding: 16px;
}
</style>
