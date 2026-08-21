<template>
  <div class="chat-view">
    <!-- 顶部标题栏 -->
    <header class="chat-header">
      <div class="chat-title">
        <van-icon :name="currentConfig?.icon || 'chat-o'" size="18" color="var(--brand)" />
        <span>{{ currentConfig?.label || 'AI对话' }}</span>
      </div>
      <van-button size="mini" plain icon="replay" @click="clearChat">清空对话</van-button>
    </header>

    <!-- 一键操作区：当前功能的预设按钮，点一下直接执行 -->
    <div v-if="actionBtns.length > 0" class="quick-bar">
      <div class="quick-bar-title">一键操作</div>
      <div class="quick-btns">
        <van-button
          v-for="act in actionBtns"
          :key="act.label"
          size="small"
          :type="act.type || 'default'"
          round
          class="quick-btn"
          :loading="actionLoading === act.label"
          @click="onActionClick(act)"
        >
          {{ act.label }}
        </van-button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div ref="msgListRef" class="msg-list">
      <template v-for="msg in messages" :key="msg.id">
        <!-- 用户消息 -->
        <div v-if="msg.role === 'user'" class="msg-row user">
          <div class="bubble user-bubble">
            <template v-if="msg.type === 'text'">{{ msg.content }}</template>
            <template v-else-if="msg.type === 'image'">
              <div class="user-image-wrap">
                <img :src="msg.content" class="user-image" alt="上传图片" />
                <span class="image-label">已上传图片，AI识别中...</span>
              </div>
            </template>
          </div>
        </div>

        <!-- AI消息 -->
        <div v-else class="msg-row ai">
          <div class="ai-avatar">
            <van-icon name="smile-o" size="16" color="#fff" />
          </div>
          <div class="bubble ai-bubble" :class="{ thinking: msg.thinking }">
            <!-- 文本 -->
            <template v-if="msg.type === 'text'">
              <template v-if="msg.thinking"><span class="think-dots"><i></i><i></i><i></i></span></template>
              <template v-else>{{ msg.content }}</template>
            </template>

            <!-- 核验卡片（记账） -->
            <template v-else-if="msg.type === 'bookkeeping-card'">
              <BookkeepingCard
                :data="msg.payload"
                :low-confidence-fields="msg.lowFields"
                @confirm="onBookkeepingConfirm"
              />
            </template>

            <!-- 查账结果列表 -->
            <template v-else-if="msg.type === 'transaction-list'">
              <div class="tx-list">
                <div class="tx-list-summary" v-if="msg.summary">
                  共 {{ msg.summary.total }} 笔 · 收入 ¥{{ fmt(msg.summary.income) }} · 支出 ¥{{ fmt(msg.summary.expense) }}
                </div>
                <div v-for="tx in msg.items" :key="tx.id" class="tx-item">
                  <div class="tx-main">
                    <span class="tx-date">{{ tx.transaction_date }}</span>
                    <span class="tx-cat">{{ tx.category || '未分类' }}</span>
                    <span class="tx-supplier">{{ tx.supplier || '-' }}</span>
                  </div>
                  <span class="tx-amount" :class="tx.type">
                    {{ tx.type === 'income' ? '+' : '-' }}¥{{ fmt(tx.amount) }}
                  </span>
                </div>
              </div>
            </template>

            <!-- 报表汇总卡片 -->
            <template v-else-if="msg.type === 'summary-card'">
              <div class="sum-card">
                <div class="sum-card-title">{{ msg.periodLabel }}收支汇总</div>
                <div class="sum-grid">
                  <div class="sum-cell">
                    <span class="sum-label">收入</span>
                    <span class="sum-value up">¥{{ fmt(msg.income) }}</span>
                  </div>
                  <div class="sum-cell">
                    <span class="sum-label">支出</span>
                    <span class="sum-value down">¥{{ fmt(msg.expense) }}</span>
                  </div>
                  <div class="sum-cell">
                    <span class="sum-label">利润</span>
                    <span class="sum-value" :class="msg.profit >= 0 ? 'up' : 'down'">¥{{ fmt(msg.profit) }}</span>
                  </div>
                </div>
              </div>
            </template>

            <!-- 报税底稿卡片 -->
            <template v-else-if="msg.type === 'tax-draft-card'">
              <div class="draft-card">
                <div class="draft-head">
                  <span>报税底稿</span>
                  <span class="draft-period">{{ msg.periodLabel }}</span>
                </div>
                <div class="draft-sub">{{ msg.period.start }} ~ {{ msg.period.end }} · 共 {{ msg.summary.tx_count }} 笔账</div>
                <div class="draft-rows">
                  <div class="draft-row">
                    <span>营业收入</span><span class="draft-val">¥{{ fmt(msg.summary.total_income) }}</span>
                  </div>
                  <div class="draft-row">
                    <span>营业成本</span><span class="draft-val">¥{{ fmt(msg.summary.total_cost) }}</span>
                  </div>
                  <div class="draft-row">
                    <span>期间费用</span><span class="draft-val">¥{{ fmt(msg.summary.total_expense) }}</span>
                  </div>
                  <div class="draft-row profit">
                    <span>利润</span><span class="draft-val">¥{{ fmt(msg.summary.total_profit) }}</span>
                  </div>
                </div>

                <div v-if="msg.costDetail.length > 0" class="draft-block">
                  <div class="draft-block-title">成本构成</div>
                  <div v-for="(item, i) in msg.costDetail" :key="i" class="draft-block-row">
                    <span>{{ item[0] }}</span><span>¥{{ fmt(item[1]) }}</span>
                  </div>
                </div>

                <div v-if="msg.expenseDetail.length > 0" class="draft-block">
                  <div class="draft-block-title">费用构成</div>
                  <div v-for="(item, i) in msg.expenseDetail" :key="i" class="draft-block-row">
                    <span>{{ item[0] }}</span><span>¥{{ fmt(item[1]) }}</span>
                  </div>
                </div>

                <div class="draft-tax">
                  <div class="draft-tax-title">税负估算参考</div>
                  <div class="draft-block-row">
                    <span>增值税</span>
                    <span v-if="msg.taxEstimate.vat_exempt" class="draft-exempt">免征（季度收入30万以内）</span>
                    <span v-else>¥{{ fmt(msg.taxEstimate.vat) }}（按1%估算）</span>
                  </div>
                  <div class="draft-block-row">
                    <span>附加税费</span>
                    <span>{{ msg.taxEstimate.vat_exempt ? '随增值税免征' : '¥' + fmt(msg.taxEstimate.surcharge) }}</span>
                  </div>
                  <div class="draft-block-row">
                    <span>经营所得个税</span>
                    <span class="draft-val">
                      ¥{{ fmt(msg.taxEstimate.income_tax) }}
                      <van-tag v-if="msg.taxEstimate.income_tax_halved" type="success" size="mini">已按减半估算</van-tag>
                    </span>
                  </div>
                  <div class="draft-block-row total">
                    <span>估算合计</span><span class="draft-val">¥{{ fmt(msg.taxEstimate.total_tax) }}</span>
                  </div>
                  <div class="draft-tax-note">{{ msg.taxEstimate.vat_rule }}</div>
                  <div class="draft-tax-note">{{ msg.taxEstimate.income_tax_note }}（本年累计利润 ¥{{ fmt(msg.taxEstimate.taxable_income_ytd) }}）</div>
                  <div class="draft-tax-note">{{ msg.taxEstimate.surcharge_note }}</div>
                  <div class="draft-tax-note">{{ msg.taxEstimate.note }}</div>
                </div>

                <!-- 待核实清单：未100%确认的规则，交给用户查证 -->
                <div v-if="msg.pendingVerification && msg.pendingVerification.length > 0" class="draft-verify">
                  <div class="draft-verify-title">
                    <van-icon name="info-o" size="13" color="var(--warn)" />
                    <span>以下规则尚未100%确认，标注为「待核实」，请以查证后的最新政策为准</span>
                  </div>
                  <div v-for="(v, i) in msg.pendingVerification" :key="i" class="draft-verify-item">
                    <span class="draft-verify-name">{{ v.item }}</span>
                    <span class="draft-verify-note">{{ v.note }}</span>
                  </div>
                </div>

                <div class="draft-disclaimer">⚠️ {{ msg.disclaimer }}</div>
              </div>
            </template>

            <!-- 报税日期提醒（真实规则 + 倒计时） -->
            <template v-else-if="msg.type === 'tax-reminder-card'">
              <div class="remind-card">
                <div class="remind-head">
                  <van-icon name="alarm-clock-o" size="16" color="var(--brand)" />
                  <span>报税日期提醒</span>
                  <span class="remind-today">{{ msg.today }}</span>
                </div>
                <div v-for="(item, i) in msg.items" :key="i" class="remind-item">
                  <div class="remind-item-main">
                    <span class="remind-label">{{ item.label }}</span>
                    <span class="remind-scope">{{ item.scope }} · 截止 {{ item.deadline }}</span>
                    <span class="remind-item-note">{{ item.note }}</span>
                  </div>
                  <span class="remind-badge" :class="item.status">{{ countdownText(item) }}</span>
                </div>
                <div v-if="msg.tips && msg.tips.length > 0" class="remind-tips">
                  <div v-for="(t, i) in msg.tips" :key="i" class="remind-tip">· {{ t }}</div>
                </div>
                <div class="remind-note">{{ msg.disclaimer }}</div>
              </div>
            </template>

            <!-- 客户台账列表 -->
            <template v-else-if="msg.type === 'customer-list'">
              <div class="customer-list">
                <div class="customer-list-head">
                  <span>客户台账（{{ (msg.items || []).length }} 位）</span>
                  <van-button size="mini" type="primary" plain icon="plus" @click="openCustomerForm()">新增客户</van-button>
                </div>
                <div v-if="!msg.items || msg.items.length === 0" class="customer-empty">
                  还没有客户。点右上角「新增客户」添加第一位吧。
                </div>
                <div v-for="c in msg.items" :key="c.id" class="customer-item" @click="openCustomerForm(c)">
                  <div class="customer-info">
                    <div class="customer-name-row">
                      <span class="customer-name">{{ c.name }}</span>
                      <span v-if="c.tag" class="customer-tag">{{ c.tag }}</span>
                    </div>
                    <span v-if="c.phone" class="customer-phone">{{ c.phone }}</span>
                    <span v-if="c.stats && c.stats.tx_count > 0" class="customer-stats">
                      累计 ¥{{ fmt(c.stats.total_amount) }} · {{ c.stats.tx_count }} 笔 · 最近 {{ c.stats.last_date }}
                    </span>
                    <span v-if="c.notes" class="customer-notes">{{ c.notes }}</span>
                  </div>
                  <div class="customer-item-btns">
                    <van-button size="mini" plain type="primary" icon="orders-o" @click.stop="onViewCustomerLedger(c)">账本</van-button>
                    <van-button size="mini" plain type="danger" icon="delete-o" @click.stop="onDeleteCustomer(c)">删除</van-button>
                  </div>
                </div>
                <div class="customer-list-foot">点客户可修改信息，点删除可移除。</div>
              </div>
            </template>

            <!-- 收支分类列表（可自由增删改） -->
            <template v-else-if="msg.type === 'category-list'">
              <div class="category-list">
                <div class="category-list-head">
                  <span>我的收支分类</span>
                  <van-button size="mini" type="primary" plain icon="plus" @click="openCategoryForm(null, 'expense')">新增</van-button>
                </div>
                <div class="category-group-title">支出分类</div>
                <div class="category-chips">
                  <span
                    v-for="c in msg.expense"
                    :key="c.id"
                    class="category-chip"
                    :class="{ custom: !c.is_default }"
                    @click="!c.is_default && openCategoryForm(c, 'expense')"
                  >
                    {{ c.name }}
                    <van-icon
                      v-if="!c.is_default"
                      name="cross"
                      class="category-chip-del"
                      @click.stop="onDeleteCategory(c, 'expense')"
                    />
                  </span>
                </div>
                <div class="category-group-title">收入分类</div>
                <div class="category-chips">
                  <span
                    v-for="c in msg.income"
                    :key="c.id"
                    class="category-chip"
                    :class="{ custom: !c.is_default }"
                    @click="!c.is_default && openCategoryForm(c, 'income')"
                  >
                    {{ c.name }}
                    <van-icon
                      v-if="!c.is_default"
                      name="cross"
                      class="category-chip-del"
                      @click.stop="onDeleteCategory(c, 'income')"
                    />
                  </span>
                </div>
                <div class="category-list-foot">带 ✕ 的是您自己加的，点它可改名，点 ✕ 可删除；系统分类不能删。记账时也能直接新建分类。</div>
              </div>
            </template>

            <!-- 按分类报表 -->
            <template v-else-if="msg.type === 'category-report'">
              <div class="cate-report">
                <div class="cate-report-title">{{ msg.periodLabel }} · 分类报表</div>
                <div class="cate-table">
                  <div class="cate-row cate-head-row">
                    <span class="cate-name">分类</span><span>收入</span><span>支出</span><span>结余</span>
                  </div>
                  <div v-for="(c, i) in msg.categories" :key="i" class="cate-row">
                    <span class="cate-name">{{ c.category }}</span>
                    <span class="cate-up">+{{ fmt(c.income) }}</span>
                    <span class="cate-down">-{{ fmt(c.expense) }}</span>
                    <span :class="c.net >= 0 ? 'cate-up' : 'cate-down'">{{ c.net >= 0 ? '' : '-' }}{{ fmt(Math.abs(c.net)) }}</span>
                  </div>
                  <div class="cate-row cate-total-row">
                    <span class="cate-name">合计</span>
                    <span class="cate-up">{{ fmt(msg.totals.income) }}</span>
                    <span class="cate-down">{{ fmt(msg.totals.expense) }}</span>
                    <span :class="msg.totals.profit >= 0 ? 'cate-up' : 'cate-down'">{{ fmt(msg.totals.profit) }}</span>
                  </div>
                </div>
              </div>
            </template>

            <!-- 按季度报表 -->
            <template v-else-if="msg.type === 'quarterly-report'">
              <div class="quarter-report">
                <div class="quarter-title">{{ msg.year }}年 · 按季度报表</div>
                <div class="quarter-table">
                  <div class="quarter-row quarter-head-row">
                    <span class="quarter-name">季度</span><span>收入</span><span>支出</span><span>利润</span>
                  </div>
                  <div
                    v-for="(q, i) in msg.quarters"
                    :key="i"
                    class="quarter-row"
                    :class="{ current: q.is_current }"
                  >
                    <span class="quarter-name">第{{ q.quarter }}季度（{{ q.months }}）</span>
                    <span class="cate-up">{{ fmt(q.income) }}</span>
                    <span class="cate-down">{{ fmt(q.expense) }}</span>
                    <span :class="q.profit >= 0 ? 'cate-up' : 'cate-down'">{{ fmt(q.profit) }}</span>
                  </div>
                  <div class="quarter-row quarter-total-row">
                    <span class="quarter-name">全年合计</span>
                    <span class="cate-up">{{ fmt(msg.totals.income) }}</span>
                    <span class="cate-down">{{ fmt(msg.totals.expense) }}</span>
                    <span :class="msg.totals.profit >= 0 ? 'cate-up' : 'cate-down'">{{ fmt(msg.totals.profit) }}</span>
                  </div>
                </div>
                <div class="quarter-note">
                  提示：现行政策季度收入30万以内增值税免征（阶段性优惠，以最新公告为准）。
                </div>
              </div>
            </template>

            <!-- 消息内快速按钮 -->
            <div v-if="msg.actions && msg.actions.length > 0" class="msg-actions">
              <van-button
                v-for="act in msg.actions"
                :key="act.label"
                size="small"
                :type="act.type || 'default'"
                round
                @click="act.handler"
              >{{ act.label }}</van-button>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="msg-empty">
        <van-icon name="chat-o" size="48" color="#c8c9cc" />
        <p>请从左侧选择一个功能开始</p>
      </div>
    </div>

    <!-- 统一输入区 -->
    <footer class="chat-input-area">
      <div class="chat-input-row">
        <!-- 图片上传 -->
        <van-uploader
          :after-read="onImageRead"
          accept="image/*"
          :max-count="1"
          :show-upload="!uploading"
          class="input-uploader"
        >
          <van-icon name="photograph" size="24" color="var(--brand)" />
        </van-uploader>

        <!-- 语音 -->
        <van-icon name="audio" size="24" color="var(--brand)" @click="onVoiceClick" />

        <!-- 文字输入 -->
        <van-field
          v-model="inputText"
          placeholder="输入您的记账内容或问题..."
          class="input-field"
          @keyup.enter="onSendText"
        />

        <!-- 发送 -->
        <van-button
          type="primary"
          size="small"
          round
          :disabled="!inputText.trim() && !uploading"
          :loading="uploading"
          @click="onSendText"
        >发送</van-button>
      </div>
      <div class="chat-input-hint">
        <span>也可以直接点上方按钮，一键完成常用操作</span>
      </div>
    </footer>

    <!-- 新增/编辑客户弹窗 -->
    <van-popup v-model:show="showCustomerForm" position="bottom" round class="customer-popup">
      <div class="customer-popup-head">
        <span>{{ customerForm.id ? '修改客户' : '新增客户' }}</span>
        <van-icon name="cross" size="18" @click="showCustomerForm = false" />
      </div>
      <div class="customer-popup-body">
        <van-field v-model="customerForm.name" label="称呼" placeholder="比如：张老板、王姐" maxlength="50" />
        <van-field v-model="customerForm.phone" label="电话" placeholder="手机号或座机" maxlength="20" type="tel" />
        <van-field label="标签">
          <template #input>
            <div class="tag-chips">
              <span
                v-for="t in tagOptions"
                :key="t"
                class="tag-chip"
                :class="{ active: customerForm.tag === t }"
                @click="customerForm.tag = customerForm.tag === t ? '' : t"
              >{{ t }}</span>
            </div>
          </template>
        </van-field>
        <van-field v-model="customerForm.notes" label="备注" placeholder="比如：爱吃辣、月结、欠款等" maxlength="200" />
        <van-button type="primary" block round :loading="customerSaving" class="customer-save-btn" @click="saveCustomer">
          保存客户
        </van-button>
      </div>
    </van-popup>

    <!-- 新增/编辑分类弹窗 -->
    <van-popup v-model:show="showCategoryForm" position="bottom" round class="customer-popup">
      <div class="customer-popup-head">
        <span>{{ categoryForm.id ? '修改分类' : '新增分类' }}</span>
        <van-icon name="cross" size="18" @click="showCategoryForm = false" />
      </div>
      <div class="customer-popup-body">
        <van-field v-model="categoryForm.name" label="分类名" placeholder="比如：进货、外卖平台、燃气" maxlength="50" />
        <van-field label="类型">
          <template #input>
            <div class="tag-chips">
              <span
                class="tag-chip"
                :class="{ active: categoryForm.type === 'expense' }"
                @click="categoryForm.type = 'expense'"
              >支出（花钱）</span>
              <span
                class="tag-chip"
                :class="{ active: categoryForm.type === 'income' }"
                @click="categoryForm.type = 'income'"
              >收入（进钱）</span>
            </div>
          </template>
        </van-field>
        <van-button type="primary" block round :loading="categorySaving" class="customer-save-btn" @click="saveCategory">
          保存分类
        </van-button>
      </div>
    </van-popup>

    <!-- 隐藏文件选择器：供"上传小票识别"按钮使用 -->
    <input
      ref="hiddenFileInput"
      type="file"
      accept="image/*"
      class="hidden-file-input"
      @change="onHiddenFileChange"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { useChatStore } from '@/stores/chat'
import { recognizeReceipt, getTaxDraft, getTaxCalendar, chatWithAi } from '@/api/ai'
import { getTransactions, getTransactionSummary, createTransaction, exportTransactions } from '@/api/transaction'
import { getCategorySummary, getQuarterly } from '@/api/analytics'
import { listCustomers, createCustomer, updateCustomer, deleteCustomer } from '@/api/customer'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/category'
import BookkeepingCard from '@/components/chat/BookkeepingCard.vue'

const route = useRoute()
const chatStore = useChatStore()

const featureId = computed(() => route.params.feature || 'ai-bookkeeping')
const currentConfig = computed(() => chatStore.getFeatureConfig(featureId.value))

const messages = ref([])
const inputText = ref('')
const uploading = ref(false)
const msgListRef = ref(null)
const hiddenFileInput = ref(null)

// 正在执行中的按钮（显示 loading）
const actionLoading = ref('')

// 客户台账弹窗
const showCustomerForm = ref(false)
const customerSaving = ref(false)
const customerForm = reactive({ id: null, name: '', phone: '', tag: '', notes: '' })
const tagOptions = ['老客户', '月结', '团购', '赊账', '散客']

// 收支分类弹窗（分类因人而异，可自由增删改）
const showCategoryForm = ref(false)
const categorySaving = ref(false)
const categoryForm = reactive({ id: null, name: '', type: 'expense' })

// 当前功能的一键操作按钮
const actionBtns = computed(() => currentConfig.value?.actions || [])

// 当前功能配置（用于聊天流程）
const isBookkeeping = computed(() => featureId.value === 'ai-bookkeeping')
const isInquiry = computed(() => featureId.value === 'inquiry')

// 记账流程状态
const bookkeepingStep = ref('idle') // idle / waiting-input / recognizing / awaiting-confirm

// ── 消息管理 ──
async function initChat() {
  messages.value = chatStore.ensureSession(featureId.value)
  await scrollToBottom()
}

function pushUserText(text) {
  chatStore.addMessage(featureId.value, { role: 'user', type: 'text', content: text })
  syncMessages()
}

function pushUserImage(dataUrl) {
  chatStore.addMessage(featureId.value, { role: 'user', type: 'image', content: dataUrl })
  syncMessages()
}

function pushAiText(text, extra = {}) {
  chatStore.addMessage(featureId.value, { role: 'assistant', type: 'text', content: text, ...extra })
  syncMessages()
}

function syncMessages() {
  messages.value = chatStore.sessions[featureId.value] || []
  scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
}

// ── 时间段解析：根据文字判断查账/报表范围 ──
function resolvePeriod(text) {
  const today = new Date()
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  const todayStr = fmt(today)
  const thisMonthStart = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`

  if (text.includes('上个')) {
    const d = new Date()
    d.setDate(1)
    d.setDate(d.getDate() - 1)
    const end = fmt(d)
    const start = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
    return { start, end, label: '上月' }
  }
  if (text.includes('7天')) {
    const d = new Date()
    d.setDate(d.getDate() - 7)
    return { start: fmt(d), end: todayStr, label: '最近7天' }
  }
  if (text.includes('今年') || text.includes('全年')) {
    return { start: `${today.getFullYear()}-01-01`, end: todayStr, label: '今年' }
  }
  return { start: thisMonthStart, end: todayStr, label: '本月' }
}

// ── 一键按钮分发：所有预设按钮的执行入口 ──
async function onActionClick(act) {
  if (actionLoading.value) return
  actionLoading.value = act.label

  try {
    switch (act.command) {
      case 'bookkeeping-upload':
        handleUploadButton()
        break
      case 'quick-text':
        handleQuickText(act.text)
        break
      case 'export-excel':
        await handleExportExcel(act.period)
        break
      case 'tax-draft':
        await handleTaxDraft(act.kind)
        break
      case 'tax-reminder':
        await handleTaxReminder()
        break
      case 'tax-tips':
        await handleTaxTips()
        break
      case 'report-category':
        await handleCategoryReport()
        break
      case 'report-quarterly':
        await handleQuarterlyReport()
        break
      case 'customers-list':
        await handleCustomersList()
        break
      case 'customers-add':
        openCustomerForm()
        break
      case 'categories-list':
        await handleCategoriesList()
        break
      case 'categories-add':
        openCategoryForm()
        break
      default:
        showToast('该功能正在完善中')
    }
  } finally {
    actionLoading.value = ''
  }
}

// 上传小票：触发表单里隐藏的文件选择器
function handleUploadButton() {
  if (!isBookkeeping.value) {
    // 不在记账页，先提示
    showToast('请先在左侧选择「AI识别记账」')
    return
  }
  hiddenFileInput.value?.click()
}

async function onHiddenFileChange(e) {
  const file = e.target.files?.[0]
  e.target.value = '' // 允许重复选择同一文件
  if (!file) return
  // 生成 dataURL 用于预览
  const dataUrl = await readFileAsDataURL(file)
  await processImage({ content: dataUrl, file })
}

function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// 快捷文字：按当前功能路由到对应流程
async function handleQuickText(text) {
  pushUserText(text)
  // 跟AI商量：直接走自由对话
  if (featureId.value === 'ai-chat') {
    await handleAiChat(text)
    return
  }
  if (isBookkeeping.value) {
    bookkeepingStep.value = 'waiting-input'
    pushAiText('好的，请直接告诉我这笔账的金额和内容，比如「买菜花了235元」或「今天卖了1800元」。')
    return
  }
  // 查账 / 报表 / 收支明细
  if (text.includes('报表')) {
    await handleReport(text)
  } else {
    await handleInquiry(text)
  }
}

// ── 发送文字：任何界面底部输入框 = 直接跟AI商量 ──
// 只有"AI识别记账"里等老板报账时，打字才走记账核验流程；
// 其余所有界面，打字一律进AI对话，AI会结合当前界面的内容回答。
async function onSendText() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  pushUserText(text)

  // 记账流程：老板正在报账，把文字当作记账信息处理
  if (isBookkeeping.value && bookkeepingStep.value === 'waiting-input') {
    await handleTextBookkeeping(text)
    return
  }

  // 其他一切情况：直接跟AI商量
  await handleAiChat(text)
}

// ── AI 自由对话：结合当前界面内容 + 聊天记录回答，带"正在思考"动效 ──
async function handleAiChat(text) {
  // 先放一个"正在思考"气泡
  chatStore.addMessage(featureId.value, {
    role: 'assistant',
    type: 'text',
    content: '',
    thinking: true,
  })
  syncMessages()

  // 把本对话框最近的文字聊天记录带上，让AI有记忆、能接着商量（排除刚问的这句，后端单独传）
  const history = messages.value
    .filter(m => m.type === 'text' && !m.thinking && m.content && !(m.role === 'user' && m.content === text))
    .slice(-10)
    .map(m => ({
      role: m.role === 'user' ? '老板' : 'AI文员',
      content: String(m.content).slice(0, 200),
    }))

  try {
    const res = await chatWithAi(text, featureId.value, history)
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg && lastMsg.thinking) {
      lastMsg.thinking = false
      lastMsg.content = res.reply || '我一时没想好，您换个问法试试？'
    } else {
      pushAiText(res.reply)
    }
    syncMessages()
  } catch (e) {
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg && lastMsg.thinking) {
      lastMsg.thinking = false
      lastMsg.content = '刚才没连上，请稍后再试。'
    } else {
      pushAiText('刚才没连上，请稍后再试。')
    }
    syncMessages()
  }
}

// ── 图片上传（记账） ──
async function onImageRead(file) {
  if (!isBookkeeping.value) {
    showToast('当前功能暂不支持图片，请到"AI识别记账"使用')
    return
  }
  if (bookkeepingStep.value === 'awaiting-confirm') {
    showToast('请先确认上一笔账目，或点击"重新记账"')
    return
  }
  await processImage(file)
}

async function processImage(file) {
  // 显示用户上传的图片
  pushUserImage(file.content)
  bookkeepingStep.value = 'recognizing'
  uploading.value = true

  try {
    const result = await recognizeReceipt(file.file)
    // 识别成功 → 生成核验卡片
    bookkeepingStep.value = 'awaiting-confirm'
    pushAiText('识别完成，请核对以下信息：')
    buildBookkeepingCard(result)
  } catch (e) {
    // 识别失败：告诉老板真实原因 + 给一张手动记账卡片，当场就能把账记了
    const reason = e?.response?.data?.message || '网络或AI服务出问题了'
    const today = new Date()
    const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
    bookkeepingStep.value = 'awaiting-confirm'
    pushAiText(`自动识别没成功：${reason}。别急，下面这张卡片您手动填一下，一样能入账：`)
    buildBookkeepingCard({
      transaction_date: dateStr,
      amount: 0,
      type: 'expense',
      category: '',
      supplier: '',
      customer_name: '',
      notes: '',
      confidence: { date: 'low', amount: 'low', category: 'low', supplier: 'low' },
      match_status: 'needs_check',
    }, ['date', 'amount', 'category', 'supplier'])
  } finally {
    uploading.value = false
  }
}

// ── 文字记账 ──
// 把老板的白话拆成账：日期(昨天/前天/X月X日)、金额、收支方向、分类(猜)、客户(台账匹配)
function parseSmartDate(text) {
  const today = new Date()
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  const d = new Date(today)
  if (text.includes('前天')) d.setDate(d.getDate() - 2)
  else if (text.includes('昨天')) d.setDate(d.getDate() - 1)
  else if (text.includes('今天')) { /* 就是今天 */ }
  else {
    const m = text.match(/(\d{1,2})月(\d{1,2})[日号]/)
    if (m) {
      const mm = parseInt(m[1], 10)
      const dd = parseInt(m[2], 10)
      if (mm >= 1 && mm <= 12 && dd >= 1 && dd <= 31) {
        return `${today.getFullYear()}-${String(mm).padStart(2, '0')}-${String(dd).padStart(2, '0')}`
      }
    }
  }
  return fmt(d)
}

function guessCategory(text) {
  const rules = [
    ['房租', ['房租', '租金', '门面费']],
    ['食材', ['菜', '肉', '食材', '米', '面', '油', '进货', '海鲜', '鱼', '蛋']],
    ['水电燃气', ['水费', '电费', '燃气', '煤气', '气费']],
    ['工资', ['工资', '工钱', '发钱']],
    ['酒水饮料', ['酒', '饮料', '啤酒', '白酒']],
    ['耗材餐具', ['餐盒', '打包盒', '筷子', '碗', '耗材', '纸巾']],
    ['设备维修', ['修', '维修', '保养']],
    ['运输配送', ['运费', '配送', '快递', '打车']],
  ]
  for (const [cat, keywords] of rules) {
    if (keywords.some(k => text.includes(k))) return cat
  }
  return ''
}

function guessIncome(text) {
  return text.includes('收') || text.includes('卖') || text.includes('赚')
    || text.includes('进账') || text.includes('营业额') || text.includes('收到')
}

async function handleTextBookkeeping(text) {
  pushAiText('好的，我记下来了。请确认以下信息是否准确：')
  const dateStr = parseSmartDate(text)
  const amountMatch = text.match(/(\d+(\.\d+)?)/)
  const amount = amountMatch ? parseFloat(amountMatch[1]) : 0
  const type = guessIncome(text) ? 'income' : 'expense'
  const category = guessCategory(text)

  // 从客户台账里匹配客户名（比如"张老板赊了300"自动挂到张老板账上）
  let customerName = ''
  try {
    const res = await listCustomers()
    const names = (res.items || []).map(c => c.name).sort((a, b) => b.length - a.length)
    customerName = names.find(n => text.includes(n)) || ''
  } catch (e) {
    // 匹配失败不影响记账
  }

  buildBookkeepingCard({
    transaction_date: dateStr,
    amount,
    type,
    category,
    supplier: '',
    customer_name: customerName,
    notes: text,
    confidence: { date: 'high', amount: amount > 0 ? 'high' : 'low', category: category ? 'medium' : 'low', supplier: 'low' },
    match_status: 'needs_check',
  }, ['category'])
  bookkeepingStep.value = 'awaiting-confirm'
}

// ── 构建核验卡片 ──
function buildBookkeepingCard(result, forceLow = []) {
  const confidence = result.confidence || {}
  const lowFields = []
  const fieldConfidence = {
    date: confidence.date,
    amount: confidence.amount,
    category: confidence.category,
    supplier: confidence.supplier,
  }
  // 找出低可信字段
  for (const [field, level] of Object.entries(fieldConfidence)) {
    if (level === 'low' || level === 'medium' || forceLow.includes(field)) {
      lowFields.push({
        field,
        label: fieldLabel(field),
        value: result[fieldValueKey(field)] || '',
        level,
      })
    }
  }

  chatStore.addMessage(featureId.value, {
    role: 'assistant',
    type: 'bookkeeping-card',
    payload: {
      transaction_date: result.transaction_date,
      amount: result.amount,
      type: result.type === '收入' || result.type === 'income' ? 'income' : 'expense',
      category: result.category,
      supplier: result.supplier,
      customer_name: result.customer_name || '',
      notes: result.notes,
    },
    lowFields,
  })
  syncMessages()
}

function fieldLabel(field) {
  return { date: '交易日期', amount: '金额', category: '分类', supplier: '供应商' }[field] || field
}

function fieldValueKey(field) {
  return { date: 'transaction_date', amount: 'amount', category: 'category', supplier: 'supplier' }[field] || field
}

// ── 查账流程 ──
async function handleInquiry(text) {
  const { start, end, label } = resolvePeriod(text)
  try {
    const res = await getTransactions({ start_date: start, end_date: end, per_page: 50 })
    const summaryRes = await getTransactionSummary({ start_date: start, end_date: end })
    const items = res.items || []
    if (items.length === 0) {
      pushAiText(`${label}（${start} ~ ${end}）没有查到收支记录。`)
      return
    }
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'transaction-list',
      items,
      summary: {
        total: res.total,
        income: summaryRes.total_income,
        expense: summaryRes.total_expense,
      },
    })
    syncMessages()
  } catch (e) {
    pushAiText('查询失败了，请稍后再试。')
  }
}

// ── 报表流程：显示汇总卡片 ──
async function handleReport(text) {
  const { start, end, label } = resolvePeriod(text)
  try {
    const summaryRes = await getTransactionSummary({ start_date: start, end_date: end })
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'summary-card',
      periodLabel: label,
      period: { start, end },
      income: summaryRes.total_income || 0,
      expense: summaryRes.total_expense || 0,
      profit: summaryRes.total_profit || 0,
    })
    syncMessages()
  } catch (e) {
    pushAiText('生成报表失败了，请稍后再试。')
  }
}

// ── 导出 Excel ──
async function handleExportExcel(period) {
  const today = new Date()
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  let start, end, label

  if (period === 'last-month') {
    const d = new Date()
    d.setDate(1)
    d.setDate(d.getDate() - 1)
    start = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
    end = fmt(d)
    label = '上月'
  } else if (period === 'all') {
    start = ''
    end = ''
    label = '全部'
  } else {
    start = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`
    end = fmt(today)
    label = '本月'
  }

  try {
    const blob = await exportTransactions({ start_date: start, end_date: end })
    const filename = `账目导出_${label}_${today.getFullYear()}${String(today.getMonth() + 1).padStart(2, '0')}${String(today.getDate()).padStart(2, '0')}.xlsx`
    downloadBlob(blob, filename)
    pushAiText(`已导出 ${label} 账目 Excel，请查看浏览器下载。`)
  } catch (e) {
    pushAiText('导出失败，请稍后再试。')
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// ── 报税底稿：一键生成（支持本月/上月/本季度等，可AI解读） ──
const DRAFT_KIND_LABELS = {
  'this-month': '本月',
  'last-month': '上月',
  'this-quarter': '本季度',
  'last-quarter': '上季度',
  'this-year': '今年全年',
  'all': '全部账目',
}

async function handleTaxDraft(kind) {
  const k = kind || 'this-month'
  const label = DRAFT_KIND_LABELS[k] || '本月'
  pushAiText(`好的，正在生成${label}报税底稿...`)
  try {
    const draft = await getTaxDraft({ kind: k })
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'tax-draft-card',
      periodLabel: draft.period?.label || label,
      period: draft.period,
      summary: draft.summary,
      costDetail: draft.cost_detail,
      expenseDetail: draft.expense_detail,
      taxEstimate: draft.tax_estimate,
      pendingVerification: draft.pending_verification,
      disclaimer: draft.disclaimer,
      actions: [
        { label: 'AI帮我解读这份底稿', type: 'primary', handler: () => handleTaxDraftAi(k, label) },
      ],
    })
    syncMessages()
  } catch (e) {
    pushAiText('生成报税底稿失败了，请稍后再试。')
  }
}

// AI解读底稿：没配Key或调用失败时，自动回退到按规则生成的解读
async function handleTaxDraftAi(kind, label) {
  pushAiText(`好的，我来用大白话解读这份${label}底稿...`)
  try {
    const draft = await getTaxDraft({ kind, use_ai: 1 })
    const notes = draft.ai_notes || {}
    pushAiText(notes.used ? 'AI解读如下：' : '（未配置AI，先看按规则生成的解读）')
    const items = notes.items || []
    if (items.length > 0) {
      pushAiText(items.join('\n'))
    }
  } catch (e) {
    pushAiText('AI解读失败了，您也可以直接看底稿里的数字。')
  }
}

// ── 报税日期提醒：真实申报时间表 + 倒计时 ──
async function handleTaxReminder() {
  pushAiText('好的，正在帮您查最近的申报安排...')
  try {
    const cal = await getTaxCalendar()
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'tax-reminder-card',
      today: cal.today,
      items: cal.items || [],
      tips: cal.tips || [],
      disclaimer: cal.disclaimer,
    })
    syncMessages()
  } catch (e) {
    pushAiText('查询申报日历失败了，请稍后再试。')
  }
}

async function handleTaxTips() {
  pushAiText('好的，说一下申报注意事项...')
  try {
    const cal = await getTaxCalendar()
    const lines = (cal.tips || []).join('\n')
    pushAiText(lines)
    pushAiText(cal.disclaimer || '以税务机关通知为准。')
  } catch (e) {
    pushAiText('查询失败了，请稍后再试。')
  }
}

function countdownText(item) {
  if (item.status === 'overdue') return `已逾期 ${-item.days_left} 天`
  if (item.status === 'open') return '办理期内'
  if (item.days_left === 0) return '今天到期'
  return `剩 ${item.days_left} 天`
}

// ── 报表增强：按分类 / 按季度 ──
async function handleCategoryReport() {
  const { start, end } = resolvePeriod('这个月')
  pushAiText('好的，正在生成按分类的报表...')
  try {
    const res = await getCategorySummary({ start_date: start, end_date: end })
    if (!res.categories || res.categories.length === 0) {
      pushAiText(`${start} ~ ${end} 还没有记账数据，先记几笔账再来生成报表吧。`)
      return
    }
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'category-report',
      periodLabel: `${start} ~ ${end}`,
      categories: res.categories,
      totals: res.totals,
    })
    syncMessages()
  } catch (e) {
    pushAiText('生成分类报表失败了，请稍后再试。')
  }
}

async function handleQuarterlyReport() {
  const year = new Date().getFullYear()
  pushAiText(`好的，正在生成${year}年按季度报表...`)
  try {
    const res = await getQuarterly({ year })
    const now = new Date()
    const currentQ = Math.floor(now.getMonth() / 3) + 1
    const quarters = (res.quarters || []).map(q => ({ ...q, is_current: q.quarter === currentQ }))
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'quarterly-report',
      year: res.year || year,
      quarters,
      totals: res.totals,
    })
    syncMessages()
  } catch (e) {
    pushAiText('生成季度报表失败了，请稍后再试。')
  }
}

// ── 客户台账：列表 / 新增 / 修改 / 删除 ──
async function handleCustomersList() {
  pushAiText('好的，正在读取您的客户台账...')
  try {
    const res = await listCustomers()
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'customer-list',
      items: res.items || [],
    })
    syncMessages()
  } catch (e) {
    pushAiText('读取客户列表失败了，请稍后再试。')
  }
}

function openCustomerForm(customer = null) {
  if (customer) {
    customerForm.id = customer.id
    customerForm.name = customer.name || ''
    customerForm.phone = customer.phone || ''
    customerForm.tag = customer.tag || ''
    customerForm.notes = customer.notes || ''
  } else {
    customerForm.id = null
    customerForm.name = ''
    customerForm.phone = ''
    customerForm.tag = ''
    customerForm.notes = ''
  }
  showCustomerForm.value = true
}

async function saveCustomer() {
  if (!customerForm.name.trim()) {
    showToast('请填一下客户称呼')
    return
  }
  customerSaving.value = true
  try {
    if (customerForm.id) {
      await updateCustomer(customerForm.id, { ...customerForm })
      pushAiText(`已更新客户「${customerForm.name}」。`)
    } else {
      await createCustomer({ ...customerForm })
      pushAiText(`已添加客户「${customerForm.name}」。`)
    }
    showCustomerForm.value = false
    await refreshCustomerListMessage()
  } catch (e) {
    // 错误已由拦截器提示
  } finally {
    customerSaving.value = false
  }
}

async function refreshCustomerListMessage() {
  try {
    const res = await listCustomers()
    const msgs = chatStore.sessions[featureId.value] || []
    let target = null
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].type === 'customer-list') {
        target = msgs[i]
        break
      }
    }
    if (target) {
      target.items = res.items || []
    } else {
      chatStore.addMessage(featureId.value, {
        role: 'assistant',
        type: 'customer-list',
        items: res.items || [],
      })
    }
    syncMessages()
  } catch (e) {
    // 静默失败，不打扰老板
  }
}

async function onDeleteCustomer(c) {
  try {
    await showConfirmDialog({
      title: '删除客户',
      message: `确定删除「${c.name}」吗？删除后无法恢复。`,
    })
  } catch (e) {
    return // 用户取消
  }
  try {
    await deleteCustomer(c.id)
    showToast('已删除')
    await refreshCustomerListMessage()
  } catch (e) {
    // 错误已由拦截器提示
  }
}

// ── 查看某个客户的往来账本 ──
async function onViewCustomerLedger(c) {
  try {
    const res = await getTransactions({ customer_name: c.name, per_page: 50 })
    const items = res.items || []
    if (items.length === 0) {
      pushAiText(`「${c.name}」还没有记账记录。记账时选上这位客户，往来账就会记到 TA 名下。`)
      return
    }
    let income = 0
    let expense = 0
    items.forEach(t => {
      const v = parseFloat(t.amount || 0)
      if (t.type === 'income') income += v
      else expense += v
    })
    pushAiText(`这是「${c.name}」的往来账本：`)
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'transaction-list',
      items,
      summary: { total: items.length, income, expense },
    })
    syncMessages()
  } catch (e) {
    pushAiText('读取客户账本失败了，请稍后再试。')
  }
}

// ── 收支分类：查看 / 新增 / 改名 / 删除（因人而异，自由调整） ──
async function handleCategoriesList() {
  pushAiText('好的，正在读取您的收支分类...')
  try {
    const res = await getCategories()
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'category-list',
      expense: res.expense || [],
      income: res.income || [],
    })
    syncMessages()
  } catch (e) {
    pushAiText('读取分类失败了，请稍后再试。')
  }
}

function openCategoryForm(cat = null, type = 'expense') {
  if (cat) {
    categoryForm.id = cat.id
    categoryForm.name = cat.name || ''
    categoryForm.type = type
  } else {
    categoryForm.id = null
    categoryForm.name = ''
    categoryForm.type = type
  }
  showCategoryForm.value = true
}

async function saveCategory() {
  if (!categoryForm.name.trim()) {
    showToast('请填一下分类名称')
    return
  }
  categorySaving.value = true
  try {
    if (categoryForm.id) {
      await updateCategory(categoryForm.id, { name: categoryForm.name, type: categoryForm.type })
      pushAiText(`已把分类改名为「${categoryForm.name}」。`)
    } else {
      await createCategory({ name: categoryForm.name, type: categoryForm.type })
      pushAiText(`已新增分类「${categoryForm.name}」。`)
    }
    showCategoryForm.value = false
    await refreshCategoryListMessage()
  } catch (e) {
    // 错误已由拦截器提示
  } finally {
    categorySaving.value = false
  }
}

async function refreshCategoryListMessage() {
  try {
    const res = await getCategories()
    const msgs = chatStore.sessions[featureId.value] || []
    let target = null
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].type === 'category-list') {
        target = msgs[i]
        break
      }
    }
    if (target) {
      target.expense = res.expense || []
      target.income = res.income || []
    } else {
      chatStore.addMessage(featureId.value, {
        role: 'assistant',
        type: 'category-list',
        expense: res.expense || [],
        income: res.income || [],
      })
    }
    syncMessages()
  } catch (e) {
    // 静默失败
  }
}

async function onDeleteCategory(cat, type) {
  try {
    await showConfirmDialog({
      title: '删除分类',
      message: `确定删除分类「${cat.name}」吗？`,
    })
  } catch (e) {
    return // 用户取消
  }
  try {
    await deleteCategory(cat.id)
    showToast('已删除')
    await refreshCategoryListMessage()
  } catch (e) {
    // 错误已由拦截器提示（如分类下有账目不能删）
  }
}

// ── 核验卡片确认 ──
async function onBookkeepingConfirm(data) {
  try {
    await createTransaction(data)
    bookkeepingStep.value = 'idle'
    pushAiText('✅ 已入账：' + (data.type === 'income' ? '收入' : '支出') + ' ¥' + fmt(data.amount) +
      (data.category ? '，分类：' + data.category : '') + '。还需要记其他账吗？')
    pushAiText('您可以继续上传小票、打字，或者点击"重新记账"。', {
      actions: [{ label: '重新记账', type: 'primary', handler: resetBookkeeping }],
    })
  } catch (e) {
    pushAiText('入库失败了，请重试。')
  }
}

function resetBookkeeping() {
  bookkeepingStep.value = 'waiting-input'
  pushAiText('好的，我们重新开始记账。您可以直接打字，也可以上传小票图片。')
}

// ── 语音（预留） ──
function onVoiceClick() {
  if (!isBookkeeping.value) {
    showToast('语音记账请在"AI识别记账"中使用')
    return
  }
  showToast('语音记账正在完善中，您也可以直接打字。')
}

// ── 清空对话 ──
function clearChat() {
  chatStore.clearSession(featureId.value)
  initChat()
  bookkeepingStep.value = 'waiting-input'
}

// 金额格式化
function fmt(val) {
  const n = parseFloat(val || 0)
  return n.toFixed(2)
}

// 切换功能时
watch(featureId, () => {
  initChat()
  bookkeepingStep.value = isBookkeeping.value ? 'waiting-input' : 'idle'
})

onMounted(() => {
  initChat()
  bookkeepingStep.value = isBookkeeping.value ? 'waiting-input' : 'idle'
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
  min-width: 0;
  background: var(--bg);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: var(--card);
  border-bottom: 1px solid var(--line);
  flex-shrink: 0;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--ink);
}

/* ── 一键操作区 ── */
.quick-bar {
  background: var(--card);
  border-bottom: 1px solid var(--line);
  padding: 10px 20px;
  flex-shrink: 0;
}

.quick-bar-title {
  font-size: 11px;
  color: var(--ink-3);
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  min-width: 96px;
}

/* ── 消息列表 ── */
.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.msg-row.user {
  justify-content: flex-end;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--brand-strong));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.bubble {
  max-width: 78%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.ai-bubble {
  background: var(--card);
  border: 1px solid var(--line);
  border-top-left-radius: 4px;
  box-shadow: var(--shadow-1);
}

/* AI正在思考动效 */
.ai-bubble.thinking {
  padding: 16px 18px;
}

.think-dots {
  display: inline-flex;
  gap: 5px;
  align-items: center;
}

.think-dots i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand);
  opacity: 0.35;
  animation: think-bounce 1.2s infinite ease-in-out;
}

.think-dots i:nth-child(2) { animation-delay: 0.15s; }
.think-dots i:nth-child(3) { animation-delay: 0.3s; }

@keyframes think-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
  30% { transform: translateY(-5px); opacity: 1; }
}

.user-bubble {
  background: var(--brand);
  color: #fff;
  border-top-right-radius: 4px;
}

.msg-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

/* 用户上传图片 */
.user-image-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.user-image {
  max-width: 200px;
  max-height: 180px;
  border-radius: 8px;
  object-fit: cover;
}

.image-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
}

/* 查账结果 */
.tx-list {
  display: flex;
  flex-direction: column;
}

.tx-list-summary {
  font-size: 13px;
  color: var(--brand);
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 8px;
}

.tx-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.tx-item:last-child { border-bottom: none; }

.tx-main {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 13px;
}

.tx-date { color: var(--ink-2); }
.tx-cat {
  background: var(--brand-soft);
  color: var(--brand);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 12px;
}
.tx-supplier { color: var(--ink-3); font-size: 12px; }

.tx-amount { font-size: 14px; font-weight: 600; }
.tx-amount.income { color: var(--up); }
.tx-amount.expense { color: var(--down); }

/* 报表汇总卡片 */
.sum-card {
  min-width: 240px;
}

.sum-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 10px;
}

.sum-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.sum-cell {
  background: var(--brand-tint);
  border-radius: 8px;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.sum-label {
  font-size: 11px;
  color: var(--ink-3);
}

.sum-value {
  font-size: 16px;
  font-weight: 700;
}
.sum-value.up { color: var(--up); }
.sum-value.down { color: var(--down); }

/* 报税底稿卡片 */
.draft-card {
  min-width: 320px;
}

.draft-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  padding-bottom: 8px;
  border-bottom: 2px solid var(--brand);
  margin-bottom: 8px;
}

.draft-period {
  font-size: 11px;
  font-weight: 400;
  color: var(--ink-3);
}

.draft-sub {
  font-size: 11px;
  color: var(--ink-3);
  margin-bottom: 10px;
}

.draft-rows {
  margin-bottom: 8px;
}

.draft-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13.5px;
  color: var(--ink-2);
}

.draft-row.profit {
  font-weight: 700;
  color: var(--ink);
  border-top: 1px dashed var(--line);
  margin-top: 4px;
  padding-top: 10px;
}

.draft-val {
  font-variant-numeric: tabular-nums;
}

.draft-row.profit .draft-val { color: var(--brand); }

.draft-block {
  background: var(--brand-tint);
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 8px;
}

.draft-block-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--brand);
  margin-bottom: 6px;
}

.draft-block-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
  color: var(--ink-2);
  padding: 3px 0;
}

.draft-block-row.total {
  font-weight: 700;
  color: var(--ink);
  border-top: 1px dashed var(--line);
  margin-top: 4px;
  padding-top: 8px;
}

.draft-block-row.total .draft-val { color: var(--brand); }

.draft-exempt {
  color: var(--up);
  font-weight: 600;
}

.draft-tax {
  background: #FFF8EC;
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 8px;
}

.draft-tax-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--warn);
  margin-bottom: 6px;
}

.draft-tax-note {
  font-size: 11px;
  color: var(--ink-3);
  margin-top: 6px;
  line-height: 1.5;
}

/* 待核实清单 */
.draft-verify {
  background: #FDF6EC;
  border: 1px dashed #E8D5AE;
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 8px;
}

.draft-verify-title {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--warn);
  margin-bottom: 6px;
  line-height: 1.4;
}

.draft-verify-item {
  padding: 5px 0;
  border-top: 1px dashed rgba(201, 147, 46, 0.25);
}

.draft-verify-item:first-of-type { border-top: none; }

.draft-verify-name {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-2);
  margin-bottom: 2px;
}

.draft-verify-note {
  display: block;
  font-size: 11px;
  color: var(--ink-3);
  line-height: 1.5;
}

.draft-disclaimer {
  font-size: 11px;
  color: var(--ink-3);
  margin-top: 8px;
  line-height: 1.5;
}

/* 报税提醒卡片 */
.remind-card {
  min-width: 300px;
}

.remind-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 10px;
}

.remind-today {
  margin-left: auto;
  font-size: 11px;
  font-weight: 400;
  color: var(--ink-3);
}

.remind-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--line);
}

.remind-item:last-of-type { border-bottom: none; }

.remind-item-main {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.remind-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
}

.remind-scope {
  font-size: 12px;
  color: var(--brand);
}

.remind-item-note {
  font-size: 11px;
  color: var(--ink-3);
  line-height: 1.4;
}

.remind-badge {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.remind-badge.normal { background: var(--brand-soft); color: var(--up); }
.remind-badge.soon { background: #FFF4DE; color: var(--warn); }
.remind-badge.urgent { background: #FDECEC; color: var(--down); }
.remind-badge.overdue { background: #FDECEC; color: var(--down); }
.remind-badge.open { background: var(--brand-soft); color: var(--brand); }

.remind-tips {
  background: var(--brand-tint);
  border-radius: 8px;
  padding: 8px 10px;
  margin-top: 8px;
}

.remind-tip {
  font-size: 11px;
  color: var(--ink-2);
  line-height: 1.6;
}

.remind-note {
  font-size: 11px;
  color: var(--ink-3);
  margin-top: 8px;
}

/* 客户台账卡片 */
.customer-list {
  min-width: 300px;
}

.customer-list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 6px;
}

.customer-empty {
  padding: 18px 0;
  text-align: center;
  font-size: 12.5px;
  color: var(--ink-3);
}

.customer-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.customer-item:last-of-type { border-bottom: none; }

.customer-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.customer-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.customer-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
}

.customer-tag {
  font-size: 10.5px;
  color: var(--brand);
  background: var(--brand-soft);
  padding: 1px 7px;
  border-radius: 999px;
}

.customer-phone {
  font-size: 12px;
  color: var(--ink-2);
}

.customer-stats {
  font-size: 11.5px;
  color: var(--brand);
  font-weight: 600;
}

.customer-item-btns {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.customer-notes {
  font-size: 11.5px;
  color: var(--ink-3);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.customer-list-foot {
  margin-top: 6px;
  font-size: 11px;
  color: var(--ink-3);
}

/* 收支分类卡片 */
.category-list {
  min-width: 300px;
}

.category-list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 8px;
}

.category-group-title {
  font-size: 11.5px;
  color: var(--ink-3);
  margin: 8px 0 6px;
}

.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.category-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--ink-2);
  background: var(--brand-tint);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 3px 10px;
}

.category-chip.custom {
  color: var(--brand);
  border-color: rgba(18, 63, 51, 0.35);
  cursor: pointer;
}

.category-chip-del {
  color: var(--ink-3);
  font-size: 11px;
}

.category-chip.custom:hover { background: var(--brand-soft); }

.category-list-foot {
  margin-top: 10px;
  font-size: 11px;
  color: var(--ink-3);
  line-height: 1.5;
}

/* 客户弹窗 */
.customer-popup {
  width: 100%;
  max-width: 560px;
  padding: 0 0 env(safe-area-inset-bottom);
}

.customer-popup-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
}

.customer-popup-body {
  padding: 0 8px 16px;
}

.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--ink-2);
  cursor: pointer;
  user-select: none;
}

.tag-chip.active {
  border-color: var(--brand);
  background: var(--brand-soft);
  color: var(--brand);
  font-weight: 600;
}

.customer-save-btn {
  margin-top: 16px;
}

/* 按分类报表 */
.cate-report {
  min-width: 320px;
}

.cate-report-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--ink);
  padding-bottom: 8px;
  border-bottom: 2px solid var(--brand);
  margin-bottom: 6px;
}

.cate-table {
  display: flex;
  flex-direction: column;
}

.cate-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 6px;
  padding: 7px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 12.5px;
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.cate-row > span:first-child { text-align: left; }

.cate-head-row {
  font-size: 11.5px;
  color: var(--ink-3);
  border-bottom: 1px solid var(--line);
}

.cate-name {
  font-weight: 600;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cate-total-row {
  font-weight: 700;
  border-bottom: none;
  border-top: 1px dashed var(--line);
  margin-top: 4px;
  padding-top: 9px;
}

.cate-up { color: var(--up); }
.cate-down { color: var(--down); }

/* 按季度报表 */
.quarter-report {
  min-width: 320px;
}

.quarter-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--ink);
  padding-bottom: 8px;
  border-bottom: 2px solid var(--brand);
  margin-bottom: 6px;
}

.quarter-table {
  display: flex;
  flex-direction: column;
}

.quarter-row {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 1fr;
  gap: 6px;
  padding: 7px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 12.5px;
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.quarter-row > span:first-child { text-align: left; }

.quarter-row.current {
  background: var(--brand-tint);
  margin: 0 -6px;
  padding-left: 6px;
  padding-right: 6px;
  border-radius: 6px;
}

.quarter-head-row {
  font-size: 11.5px;
  color: var(--ink-3);
  border-bottom: 1px solid var(--line);
}

.quarter-name {
  font-weight: 600;
  color: var(--ink);
}

.quarter-total-row {
  font-weight: 700;
  border-bottom: none;
  border-top: 1px dashed var(--line);
  margin-top: 4px;
  padding-top: 9px;
}

.quarter-note {
  margin-top: 8px;
  font-size: 11px;
  color: var(--ink-3);
  line-height: 1.5;
}

/* 空状态 */
.msg-empty {
  text-align: center;
  padding: 60px 0;
  color: #c8c9cc;
}

.msg-empty p { font-size: 13px; margin-top: 12px; }

/* 输入区 */
.chat-input-area {
  background: var(--card);
  border-top: 1px solid var(--line);
  padding: 10px 16px 12px;
  flex-shrink: 0;
}

.chat-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-uploader {
  flex-shrink: 0;
}

.input-field {
  flex: 1;
  background: var(--bg);
  border-radius: 20px;
  padding: 0 14px;
}

.chat-input-hint {
  text-align: center;
  font-size: 11px;
  color: var(--ink-3);
  margin-top: 6px;
}

.hidden-file-input {
  display: none;
}
</style>
