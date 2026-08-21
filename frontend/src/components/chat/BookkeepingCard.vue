<template>
  <div class="bookkeeping-card">
    <!-- 风险提示 -->
    <div class="card-warning">
      <van-icon name="warning-o" size="14" color="#ee0a24" />
      <span>数据将影响报表与报税，请仔细核对后确认</span>
    </div>

    <!-- 高可信数据区 -->
    <div class="data-section">
      <div class="section-label high">✔ 已识别</div>
      <div class="field-grid">
        <div class="field-item">
          <span class="field-name">交易日期</span>
          <span class="field-value">{{ data.transaction_date || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-name">金额</span>
          <span class="field-value amount">¥{{ fmtAmount(data.amount) }}</span>
        </div>
        <div class="field-item">
          <span class="field-name">类型</span>
          <span class="field-value" :class="data.type === 'income' ? 'green' : 'red'">
            {{ data.type === 'income' ? '收入' : '支出' }}
          </span>
        </div>
      </div>

      <!-- 分类选择：随时可换，还能新建自己的分类 -->
      <div class="category-pick-row">
        <span class="field-name">分类</span>
        <span class="category-pick-current">{{ selectedCategory || data.category || '未选择' }}</span>
        <van-button size="mini" type="primary" plain @click="openPicker">选分类</van-button>
      </div>

      <!-- 客户选择：这笔账挂到哪位客户名下（往来账/赊账） -->
      <div class="category-pick-row">
        <span class="field-name">客户</span>
        <span class="category-pick-current">{{ selectedCustomer || data.customer_name || '散客/不挂客户' }}</span>
        <van-button size="mini" type="primary" plain @click="openCustomerPicker">选客户</van-button>
      </div>
    </div>

    <!-- 低可信数据区 -->
    <div v-if="lowConfidenceFields.length > 0" class="data-section low-section">
      <div class="section-label low">需要您确认</div>
      <div v-for="lf in lowConfidenceFields" :key="lf.field" class="low-field-item">
        <div class="low-field-info">
          <span class="field-name">{{ lf.label }}</span>
          <van-tag :type="lf.level === 'low' ? 'danger' : 'warning'" size="mini">
            {{ lf.level === 'low' ? '不确定' : '需核对' }}
          </van-tag>
        </div>
        <div class="low-field-value">
          <van-field
            v-model="editable[lf.field]"
            size="small"
            :placeholder="'请输入' + lf.label"
            class="low-input"
          />
          <van-button size="small" type="primary" plain @click="confirmField(lf.field)">确认</van-button>
        </div>
      </div>
    </div>

    <!-- 全部低可信字段处理完，才出现入库按钮 -->
    <van-button
      v-if="allConfirmed"
      type="primary"
      block
      round
      :loading="submitting"
      loading-text="入库中..."
      class="submit-btn"
      @click="submit"
    >
      全部确认，入库
    </van-button>
    <div v-else class="submit-placeholder">
      <span v-if="lowConfidenceFields.length > 0">请先确认所有"需要您确认"的项目</span>
      <span v-else>点击下方按钮完成入库</span>
    </div>

    <!-- 分类选择弹窗 -->
    <van-popup v-model:show="showPicker" position="bottom" round class="cate-picker-popup">
      <div class="cate-picker-head">
        <span>选择分类</span>
        <van-icon name="cross" size="18" @click="showPicker = false" />
      </div>
      <div class="cate-picker-body">
        <div class="cate-picker-tip">每个店分类不一样，选不准就自己建一个</div>
        <div class="cate-picker-chips">
          <span
            v-for="c in pickerOptions"
            :key="c.id"
            class="cate-picker-chip"
            :class="{ active: (selectedCategory || data.category) === c.name }"
            @click="pickCategory(c.name)"
          >{{ c.name }}</span>
        </div>
        <div class="cate-picker-new">
          <template v-if="!showNewInput">
            <van-button size="small" type="primary" plain icon="plus" @click="showNewInput = true">
              新建自己的分类
            </van-button>
          </template>
          <template v-else>
            <div class="cate-new-row">
              <van-field
                v-model="newCatName"
                placeholder="分类名，比如：进货"
                maxlength="50"
                class="cate-new-input"
                @keyup.enter="createNewCategory"
              />
              <van-button size="small" type="primary" :loading="catSaving" @click="createNewCategory">
                保存
              </van-button>
            </div>
          </template>
        </div>
      </div>
    </van-popup>
    <!-- 客户选择弹窗 -->
    <van-popup v-model:show="showCustomerPicker" position="bottom" round class="cate-picker-popup">
      <div class="cate-picker-head">
        <span>选择客户（这笔账记在谁名下）</span>
        <van-icon name="cross" size="18" @click="showCustomerPicker = false" />
      </div>
      <div class="cate-picker-body">
        <div class="cate-picker-tip">挂上客户，TA 的往来账、赊账都记在一起，随时能查</div>
        <div class="cate-picker-chips">
          <span
            class="cate-picker-chip"
            :class="{ active: !selectedCustomer && !data.customer_name }"
            @click="pickCustomer('')"
          >散客/不挂客户</span>
          <span
            v-for="c in customerOptions"
            :key="c.id"
            class="cate-picker-chip"
            :class="{ active: (selectedCustomer || data.customer_name) === c.name }"
            @click="pickCustomer(c.name)"
          >{{ c.name }}</span>
        </div>
        <div class="cate-picker-new">
          <template v-if="!showNewCustomerInput">
            <van-button size="small" type="primary" plain icon="plus" @click="showNewCustomerInput = true">
              新建客户
            </van-button>
          </template>
          <template v-else>
            <div class="cate-new-row">
              <van-field
                v-model="newCustomerName"
                placeholder="客户称呼，比如：张老板"
                maxlength="50"
                class="cate-new-input"
                @keyup.enter="createNewCustomer"
              />
              <van-button size="small" type="primary" :loading="customerSaving" @click="createNewCustomer">
                保存
              </van-button>
            </div>
          </template>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { showToast } from 'vant'
import { getCategories, createCategory } from '@/api/category'
import { listCustomers, createCustomer } from '@/api/customer'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
  lowFields: { type: Array, default: () => [] },
})

const emit = defineEmits(['confirm'])

const submitting = ref(false)
const editable = reactive({})

// 初始化可编辑字段
props.lowFields.forEach(lf => {
  editable[lf.field] = lf.value || ''
})

// 已确认的低可信字段
const confirmedFields = ref([])

// ── 分类选择（因人而异，可自由调整） ──
const categories = ref({ expense: [], income: [] })
const selectedCategory = ref('')
const showPicker = ref(false)
const showNewInput = ref(false)
const newCatName = ref('')
const catSaving = ref(false)

// ── 客户选择（这笔账挂到哪位客户名下） ──
const customerOptions = ref([])
const selectedCustomer = ref('')
const showCustomerPicker = ref(false)
const showNewCustomerInput = ref(false)
const newCustomerName = ref('')
const customerSaving = ref(false)

const pickerType = computed(() => (props.data.type === 'income' ? 'income' : 'expense'))
const pickerOptions = computed(() => categories.value[pickerType.value] || [])

async function loadCategories() {
  try {
    categories.value = await getCategories()
  } catch (e) {
    // 失败保持空，不影响记账
  }
}

function openPicker() {
  showNewInput.value = false
  newCatName.value = ''
  showPicker.value = true
  loadCategories()
}

function pickCategory(name) {
  selectedCategory.value = name
  // 若分类在待确认列表里，直接帮老板填好并确认
  const lf = lowConfidenceFields.value.find(f => f.field === 'category')
  if (lf) {
    editable.category = name
    confirmField('category')
  }
  showPicker.value = false
}

async function createNewCategory() {
  const name = newCatName.value.trim()
  if (!name) {
    showToast('请填分类名')
    return
  }
  catSaving.value = true
  try {
    await createCategory({ name, type: pickerType.value })
    newCatName.value = ''
    showNewInput.value = false
    await loadCategories()
    pickCategory(name)
    showToast('分类已建好')
  } catch (e) {
    // 错误已由拦截器提示
  } finally {
    catSaving.value = false
  }
}

// ── 客户选择逻辑 ──
async function loadCustomers() {
  try {
    const res = await listCustomers()
    customerOptions.value = res.items || []
  } catch (e) {
    // 失败保持空，不影响记账
  }
}

function openCustomerPicker() {
  showNewCustomerInput.value = false
  newCustomerName.value = ''
  showCustomerPicker.value = true
  loadCustomers()
}

function pickCustomer(name) {
  selectedCustomer.value = name
  showCustomerPicker.value = false
}

async function createNewCustomer() {
  const name = newCustomerName.value.trim()
  if (!name) {
    showToast('请填客户称呼')
    return
  }
  customerSaving.value = true
  try {
    await createCustomer({ name })
    newCustomerName.value = ''
    showNewCustomerInput.value = false
    await loadCustomers()
    pickCustomer(name)
    showToast('客户已建好')
  } catch (e) {
    // 错误已由拦截器提示
  } finally {
    customerSaving.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadCustomers()
})

const lowConfidenceFields = computed(() => props.lowFields || [])

const allConfirmed = computed(() => {
  if (lowConfidenceFields.value.length === 0) return true
  return confirmedFields.value.length >= lowConfidenceFields.value.length
})

function confirmField(field) {
  const lf = lowConfidenceFields.value.find(f => f.field === field)
  if (lf && (lf.field === 'amount' || lf.field === 'date')) {
    if (!editable[field]) {
      showToast('请先填写' + lf.label)
      return
    }
  }
  if (!confirmedFields.value.includes(field)) {
    confirmedFields.value.push(field)
  }
  showToast('已确认')
}

function fmtAmount(val) {
  const n = parseFloat(val || 0)
  return n.toFixed(2)
}

async function submit() {
  submitting.value = true
  try {
    // 合并确认后的字段
    const finalData = { ...props.data }
    lowConfidenceFields.value.forEach(lf => {
      const key = lf.field
      if (key === 'amount') {
        finalData.amount = parseFloat(editable[key] || finalData.amount)
      } else if (key === 'date') {
        finalData.transaction_date = editable[key] || finalData.transaction_date
      } else if (key === 'category') {
        finalData.category = editable[key] || finalData.category
      } else if (key === 'supplier') {
        finalData.supplier = editable[key] || finalData.supplier
      }
    })
    // 点选过分类则优先用点选的
    if (selectedCategory.value) {
      finalData.category = selectedCategory.value
    }
    // 点选过客户则挂到该客户名下
    if (selectedCustomer.value) {
      finalData.customer_name = selectedCustomer.value
    }
    emit('confirm', finalData)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.bookkeeping-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #ebedf0;
  overflow: hidden;
  width: 100%;
  min-width: 300px;
}

.card-warning {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fff0f0;
  padding: 8px 12px;
  font-size: 12px;
  color: #ee0a24;
}

.data-section {
  padding: 12px;
}

.low-section {
  background: #fffbef;
  border-top: 1px dashed #f0e3c8;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 10px;
}

.section-label.high { color: #07c160; }
.section-label.low { color: #b7791f; }

.field-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.field-item {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-name {
  font-size: 12px;
  color: #969799;
}

.field-value {
  font-size: 14px;
  font-weight: 600;
  color: #323233;
}

.field-value.amount { color: #1F6FB2; font-size: 16px; }
.field-value.green { color: #07c160; }
.field-value.red { color: #ee0a24; }

/* 分类选择行 */
.category-pick-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 8px 10px;
}

.category-pick-current {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #323233;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 分类弹窗 */
.cate-picker-popup {
  width: 100%;
  max-width: 560px;
  padding-bottom: env(safe-area-inset-bottom);
}

.cate-picker-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 8px;
  font-size: 15px;
  font-weight: 600;
  color: #323233;
}

.cate-picker-body {
  padding: 4px 16px 18px;
}

.cate-picker-tip {
  font-size: 11.5px;
  color: #969799;
  margin-bottom: 10px;
}

.cate-picker-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cate-picker-chip {
  font-size: 13px;
  color: #4a5560;
  background: #f7f8fa;
  border: 1px solid #ebedf0;
  border-radius: 999px;
  padding: 5px 14px;
  cursor: pointer;
  user-select: none;
}

.cate-picker-chip.active {
  background: var(--brand-soft, #eaf3ef);
  border-color: var(--brand, #123f33);
  color: var(--brand, #123f33);
  font-weight: 600;
}

.cate-picker-new {
  margin-top: 14px;
}

.cate-new-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cate-new-input {
  flex: 1;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 0 10px;
}

.low-field-item {
  background: #fff;
  border: 1px solid #f0e3c8;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 8px;
}

.low-field-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.low-field-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.low-input {
  flex: 1;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 0 10px;
}

.submit-btn {
  margin: 12px;
}

.submit-placeholder {
  text-align: center;
  padding: 10px;
  font-size: 12px;
  color: #c8c9cc;
  border-top: 1px solid #f5f5f5;
}
</style>
