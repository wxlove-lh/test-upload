<template>
  <div class="page-container">
    <van-nav-bar title="个人中心" />
    <div class="page-content">
      <!-- 套餐信息区 -->
      <div class="section subscription-section">
        <div class="subscription-info">
          <p class="subscription-label">您当前是：</p>
          <p
            class="subscription-name"
            :class="{ 'text-danger': isExpired || userStore.isExpiringSoon }"
          >
            {{ displaySubscription }}
          </p>
          <p v-if="userStore.userInfo?.subscription_expiry" class="expiry-date">
            到期日：{{ formatDate(userStore.userInfo.subscription_expiry) }}
          </p>
          <p v-if="isExpired" class="expiry-warning">
            您的套餐已过期，请续费
          </p>
          <p v-else-if="userStore.isExpiringSoon" class="expiry-warning">
            您的套餐还有{{ userStore.daysUntilExpiry }}天到期，请尽快续费
          </p>
        </div>
        <div class="subscription-actions">
          <van-button type="primary" size="small" @click="goRenew">续费</van-button>
          <van-button plain size="small" @click="onEndService">结束服务</van-button>
        </div>
      </div>

      <!-- 推荐码区 -->
      <div class="section">
        <van-cell-group inset>
          <van-cell title="推荐码" :value="referralCode">
            <template #right-icon>
              <van-button size="mini" type="primary" plain @click="copyReferralCode">
                复制
              </van-button>
            </template>
          </van-cell>
          <van-cell title="已邀请" :value="referralData?.invited_count + '人' || '0人'" />
          <van-cell title="优惠券" :value="coupons.length + '张'" />
        </van-cell-group>
      </div>

      <!-- 裂变记录 -->
      <div class="section">
        <van-cell-group inset title="裂变记录">
          <template v-if="referralRecords.length > 0">
            <van-cell
              v-for="(record, index) in referralRecords"
              :key="index"
              :title="maskPhone(record.phone)"
              :label="formatDate(record.date)"
              :value="record.status"
            />
          </template>
          <van-empty v-else description="暂无裂变记录" image="search" />
        </van-cell-group>
      </div>

      <!-- 优惠券列表 -->
      <div class="section">
        <van-cell-group inset title="我的优惠券">
          <template v-if="coupons.length > 0">
            <van-cell
              v-for="(coupon, index) in coupons"
              :key="index"
              :title="'¥' + formatMoney(coupon.amount)"
              :label="coupon.source + ' ' + formatDate(coupon.expire_date)"
              :value="couponStatusText(coupon.status)"
              :value-class="'coupon-status-' + coupon.status"
            />
          </template>
          <van-empty v-else description="暂无优惠券" image="coupon" />
        </van-cell-group>
      </div>

      <!-- 退出登录 -->
      <div class="section logout-section">
        <van-button type="danger" plain block @click="onLogout">退出登录</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import { useUserStore } from '@/stores/user'
import { getReferralInfo } from '@/api/referral'

const router = useRouter()
const userStore = useUserStore()

// 推荐/裂变数据
const referralData = ref(null)
const referralRecords = ref([])
const coupons = ref([])

// 推荐码
const referralCode = computed(() => {
  return userStore.userInfo?.referral_code || '暂无'
})

// 是否已过期
const isExpired = computed(() => {
  if (!userStore.userInfo?.subscription_expiry) return false
  return userStore.daysUntilExpiry !== null && userStore.daysUntilExpiry <= 0
})

// 显示订阅文本
const displaySubscription = computed(() => {
  if (!userStore.userInfo) return '加载中...'
  const plan = userStore.userInfo.subscription_plan
  if (!plan || plan === 'free') {
    const remaining = userStore.userInfo.remaining_free_uses
    return remaining != null ? `免费体验（剩余${remaining}次）` : '免费体验'
  }
  return userStore.subscriptionText
})

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 金额千分位
function formatMoney(amount) {
  if (amount == null) return '0'
  return Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 手机号脱敏
function maskPhone(phone) {
  if (!phone || phone.length < 7) return phone
  return phone.slice(0, 3) + '****' + phone.slice(-4)
}

// 优惠券状态文本
function couponStatusText(status) {
  const map = { unused: '未使用', used: '已使用', expired: '已过期' }
  return map[status] || status
}

// 复制推荐码
async function copyReferralCode() {
  const code = userStore.userInfo?.referral_code
  if (!code) {
    showToast('暂无推荐码')
    return
  }
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(code)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = code
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    showToast('已复制')
  } catch {
    showToast('复制失败，请手动复制')
  }
}

// 续费
function goRenew() {
  router.push('/pricing')
}

// 结束服务
function onEndService() {
  showDialog({
    title: '结束服务',
    message: '结束服务后数据保留90天，之后会自动删除所有数据，确定要结束吗？',
    confirmButtonText: '确定结束',
    cancelButtonText: '再想想',
    showCancelButton: true,
  }).then(() => {
    showToast('功能开发中')
  }).catch(() => {})
}

// 退出登录
function onLogout() {
  showDialog({
    title: '退出登录',
    message: '确定要退出登录吗？',
    showCancelButton: true,
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {})
}

// 加载推荐/裂变数据
async function loadReferralData() {
  try {
    const res = await getReferralInfo()
    referralData.value = res
    referralRecords.value = res?.records || []
    coupons.value = res?.coupons || []
  } catch {
    // API不存在时静默处理
    referralRecords.value = []
    coupons.value = []
  }
}

onMounted(() => {
  if (!userStore.userInfo) {
    userStore.fetchUserInfo()
  }
  loadReferralData()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f7f8fa;
}
.page-content {
  padding-bottom: 80px;
}
.section {
  margin: 12px 0;
}
.subscription-section {
  background: #fff;
  padding: 20px 16px;
  margin: 0;
}
.subscription-info {
  margin-bottom: 12px;
}
.subscription-label {
  font-size: 13px;
  color: #969799;
  margin-bottom: 4px;
}
.subscription-name {
  font-size: 18px;
  font-weight: bold;
  color: #1a3a5c;
  margin-bottom: 4px;
}
.subscription-name.text-danger {
  color: #ee0a24;
}
.expiry-date {
  font-size: 13px;
  color: #969799;
  margin-bottom: 2px;
}
.expiry-warning {
  font-size: 13px;
  color: #ee0a24;
  margin-top: 4px;
  font-weight: 500;
}
.subscription-actions {
  display: flex;
  gap: 12px;
}
.logout-section {
  padding: 16px;
}
:deep(.coupon-status-unused) {
  color: #07c160;
}
:deep(.coupon-status-used) {
  color: #969799;
}
:deep(.coupon-status-expired) {
  color: #ee0a24;
}
</style>
