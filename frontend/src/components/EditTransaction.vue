<template>
  <van-popup
    v-model:show="visible"
    position="bottom"
    round
    :style="{ maxHeight: '85vh' }"
    @close="handleClose"
  >
    <div class="edit-transaction">
      <!-- 警告条 -->
      <div v-if="!editMode" class="warning-bar">
        <van-icon name="warning-o" size="18" color="#ee0a24" />
        <span class="warning-text">正在修改已入账的历史数据，此操作影响统计结果，确定要修改吗？</span>
      </div>

      <!-- 确认修改按钮（未进入编辑模式时显示） -->
      <div v-if="!editMode" class="confirm-action">
        <van-button type="danger" block round @click="editMode = true">
          确定修改
        </van-button>
      </div>

      <!-- 编辑表单 -->
      <div v-if="editMode" class="edit-form">
        <div class="form-header">
          <span>修改交易记录</span>
          <van-icon name="cross" @click="handleClose" />
        </div>

        <!-- 交易日期 -->
        <van-field
          v-model="form.transaction_date"
          is-link
          readonly
          label="交易日期"
          placeholder="请选择日期"
          @click="showDatePicker = true"
        />

        <!-- 金额 -->
        <van-field
          v-model="form.amount"
          label="金额"
          type="number"
          placeholder="请输入金额"
        />

        <!-- 类型 -->
        <van-field name="type" label="类型">
          <template #input>
            <van-radio-group v-model="form.type" direction="horizontal">
              <van-radio name="income">收入</van-radio>
              <van-radio name="expense">支出</van-radio>
            </van-radio-group>
          </template>
        </van-field>

        <!-- 分类 -->
        <van-field
          v-model="form.category"
          is-link
          readonly
          label="分类"
          placeholder="请选择分类"
          @click="showCategoryPicker = true"
        />

        <!-- 供应商 -->
        <van-field
          v-model="form.supplier"
          label="供应商"
          placeholder="请输入供应商名称"
        />

        <!-- 备注 -->
        <van-field
          v-model="form.notes"
          label="备注"
          type="textarea"
          rows="2"
          placeholder="请输入备注（选填）"
          autosize
        />

        <!-- 底部按钮 -->
        <div class="form-actions">
          <van-button plain round @click="handleClose">取消</van-button>
          <van-button type="primary" round :loading="saving" loading-text="保存中..." @click="handleSave">
            保存修改
          </van-button>
        </div>
      </div>

      <!-- 日期选择器 -->
      <van-popup v-model:show="showDatePicker" position="bottom" round>
        <van-date-picker
          v-model="datePickerValue"
          title="选择交易日期"
          :min-date="minDate"
          :max-date="maxDate"
          @confirm="onDateConfirm"
          @cancel="showDatePicker = false"
        />
      </van-popup>

      <!-- 分类选择器 -->
      <van-popup v-model:show="showCategoryPicker" position="bottom" round>
        <van-picker
          :columns="categoryColumns"
          @confirm="onCategoryConfirm"
          @cancel="showCategoryPicker = false"
        />
      </van-popup>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { showToast } from 'vant'
import { updateTransaction } from '@/api/transaction'

const props = defineProps({
  show: { type: Boolean, default: false },
  transaction: { type: Object, default: null },
})

const emit = defineEmits(['update:show', 'refresh'])

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val),
})

const editMode = ref(false)
const saving = ref(false)
const showDatePicker = ref(false)
const showCategoryPicker = ref(false)

const form = ref({
  transaction_date: '',
  amount: '',
  type: 'expense',
  category: '',
  supplier: '',
  notes: '',
})

// 日期选择器值（数组格式 ['2026','08','02']）
const datePickerValue = ref([])
const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

// 分类选项
const categoryColumns = [
  '餐饮', '交通', '购物', '娱乐', '医疗', '教育',
  '住房', '通讯', '工资', '奖金', '投资收益', '其他',
]

/** 当弹窗打开且有交易数据时，初始化表单 */
watch(
  () => props.show,
  (val) => {
    if (val && props.transaction) {
      editMode.value = false
      const t = props.transaction
      form.value = {
        transaction_date: t.transaction_date || '',
        amount: String(t.amount || ''),
        type: t.type || 'expense',
        category: t.category || '',
        supplier: t.supplier || '',
        notes: t.notes || '',
      }
      // 初始化日期选择器
      if (t.transaction_date) {
        const parts = t.transaction_date.split('-')
        datePickerValue.value = parts
      } else {
        const now = new Date()
        datePickerValue.value = [
          String(now.getFullYear()),
          String(now.getMonth() + 1).padStart(2, '0'),
          String(now.getDate()).padStart(2, '0'),
        ]
      }
    }
  }
)

/** 日期确认 */
function onDateConfirm({ selectedValues }) {
  form.value.transaction_date = selectedValues.join('-')
  showDatePicker.value = false
}

/** 分类确认 */
function onCategoryConfirm({ selectedValues }) {
  form.value.category = selectedValues[0] || ''
  showCategoryPicker.value = false
}

/** 保存修改 */
async function handleSave() {
  if (!form.value.transaction_date) {
    showToast('请选择交易日期')
    return
  }
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    showToast('请输入有效金额')
    return
  }

  saving.value = true
  try {
    await updateTransaction(props.transaction.id, {
      transaction_date: form.value.transaction_date,
      amount: parseFloat(form.value.amount),
      type: form.value.type,
      category: form.value.category,
      supplier: form.value.supplier,
      notes: form.value.notes,
    })
    showToast({ message: '修改成功', type: 'success' })
    visible.value = false
    emit('refresh')
  } catch (error) {
    // 错误已由api拦截器处理
  } finally {
    saving.value = false
  }
}

/** 关闭弹窗 */
function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.edit-transaction {
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.warning-bar {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fff8f0;
  border: 1px solid #ffdfdf;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.warning-text {
  font-size: 13px;
  color: #ee0a24;
  line-height: 1.5;
}

.confirm-action {
  padding: 16px 0;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f5f5f5;
}

.form-header .van-icon {
  cursor: pointer;
  color: #999;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f5f5f5;
}

.form-actions .van-button {
  flex: 1;
}
</style>
