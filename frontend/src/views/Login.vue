<template>
  <div class="login-page">
    <!-- 左：品牌区（桌面展示，手机端收成紧凑头部） -->
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-top">
          <div class="seal-logo">账</div>
          <span class="brand-wordmark">AI虚拟文员</span>
        </div>

        <h1 class="brand-headline">开店的每一笔，<br>都记得清清楚楚。</h1>
        <p class="brand-sub">AI 记账 · 自动归类 · 报税提醒<br />把散乱的小票，变成一本整整齐齐的账。</p>

        <div class="brand-feats">
          <span class="feat-pill">小票拍照即记</span>
          <span class="feat-pill">收支自动归类</span>
          <span class="feat-pill">报税日期提醒</span>
        </div>

        <div class="brand-stamp">专业账本 · 报税好帮手</div>
      </div>
    </div>

    <!-- 右：登录/注册表单区 -->
    <div class="form-panel">
      <div class="form-card">
        <div class="card-head">
          <h2 class="card-title">{{ activeTab === 0 ? '欢迎回来' : '创建账号' }}</h2>
          <p class="card-sub">{{ activeTab === 0 ? '用手机号登录您的账本' : '注册后即可开始免费体验' }}</p>
        </div>

        <van-tabs v-model:active="activeTab" class="login-tabs" :line-width="26" title-active-color="#123F33">
          <van-tab title="登录">
            <van-form @submit="onLogin" class="login-form">
              <van-field
                v-model="loginForm.phone"
                name="phone"
                label=""
                type="tel"
                placeholder="请输入手机号"
                maxlength="11"
                left-icon="phone-o"
                :rules="[
                  { required: true, message: '请输入手机号' },
                  { pattern: /^1\d{10}$/, message: '请输入正确的手机号' }
                ]"
              />
              <van-field
                v-model="loginForm.password"
                name="password"
                label=""
                type="password"
                placeholder="请输入密码"
                left-icon="lock"
                :rules="[{ required: true, message: '请输入密码' }]"
              />
              <div class="form-footer">
                <van-button
                  round
                  block
                  type="primary"
                  native-type="submit"
                  :loading="loading"
                  loading-text="登录中..."
                  class="submit-btn"
                >
                  登录
                </van-button>
              </div>
            </van-form>
          </van-tab>

          <van-tab title="注册">
            <van-form @submit="onRegister" class="login-form">
              <van-field
                v-model="registerForm.phone"
                name="phone"
                label=""
                type="tel"
                placeholder="请输入手机号"
                maxlength="11"
                left-icon="phone-o"
                :rules="[
                  { required: true, message: '请输入手机号' },
                  { pattern: /^1\d{10}$/, message: '请输入正确的手机号' }
                ]"
              />
              <van-field
                v-model="registerForm.password"
                name="password"
                label=""
                type="password"
                placeholder="设置密码"
                left-icon="lock"
                :rules="[
                  { required: true, message: '请输入密码' },
                  { validator: checkPasswordLength, message: '密码至少6位' }
                ]"
              />
              <van-field
                v-model="registerForm.confirmPassword"
                name="confirmPassword"
                label=""
                type="password"
                placeholder="再输一次密码"
                left-icon="lock"
                :rules="[
                  { required: true, message: '请确认密码' },
                  { validator: checkPasswordMatch, message: '两次密码不一致' }
                ]"
              />
              <van-field
                v-model="registerForm.industryText"
                name="industry"
                label=""
                placeholder="您的店属于哪种？"
                readonly
                is-link
                left-icon="shop-o"
                @click="showIndustryPicker = true"
                :rules="[{ required: true, message: '请选择行业' }]"
              />
              <van-field
                v-model="registerForm.referralCode"
                name="referral_code"
                label=""
                placeholder="推荐码（选填）"
                left-icon="gift-o"
              />
              <div class="form-footer">
                <van-button
                  round
                  block
                  type="primary"
                  native-type="submit"
                  :loading="loading"
                  loading-text="注册中..."
                  class="submit-btn"
                >
                  注册
                </van-button>
              </div>
            </van-form>
          </van-tab>
        </van-tabs>

        <!-- 演示账号提示 -->
        <div v-if="activeTab === 0" class="demo-hint" @click="fillDemo">
          <van-icon name="smile-o" size="15" />
          <span>演示账号：13812345678 / 123456</span>
          <span class="demo-fill">点此填入</span>
        </div>
      </div>

      <div class="footer-tip">前 5 次免费体验，无需付费即可使用</div>
      <div class="version-tag">工作台版 v0.2</div>
    </div>

    <!-- 行业选择弹出层 -->
    <van-popup v-model:show="showIndustryPicker" round position="bottom">
      <van-picker
        :columns="industryColumns"
        @confirm="onIndustryConfirm"
        @cancel="showIndustryPicker = false"
        title="选择行业"
        confirm-button-text="确定"
        cancel-button-text="取消"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref(0)
const loading = ref(false)
const showIndustryPicker = ref(false)

// 登录表单
const loginForm = reactive({
  phone: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  phone: '',
  password: '',
  confirmPassword: '',
  industry: '',
  industryText: '',
  referralCode: ''
})

// 行业选项
const industryColumns = [
  { text: '奶茶店', value: '奶茶店' },
  { text: '咖啡店', value: '咖啡店' },
  { text: '面包店', value: '面包店' },
  { text: '早餐店', value: '早餐店' },
  { text: '快餐店', value: '快餐店' },
  { text: '小吃店', value: '小吃店' },
  { text: '烧烤店', value: '烧烤店' },
  { text: '中餐馆', value: '中餐馆' },
  { text: '西餐厅', value: '西餐厅' }
]

// 密码长度校验
function checkPasswordLength(val) {
  return val.length >= 6
}

// 密码一致性校验
function checkPasswordMatch(val) {
  return val === registerForm.password
}

// 行业选择确认
function onIndustryConfirm({ selectedOptions }) {
  registerForm.industry = selectedOptions[0].value
  registerForm.industryText = selectedOptions[0].text
  showIndustryPicker.value = false
}

// 演示账号一键填入
function fillDemo() {
  loginForm.phone = '13812345678'
  loginForm.password = '123456'
  showToast('已填入演示账号，点登录即可')
}

// 登录
async function onLogin() {
  loading.value = true
  try {
    await userStore.login(loginForm.phone, loginForm.password)
    await userStore.fetchUserInfo()
    router.push('/app')
  } catch (e) {
    const msg = e.response?.data?.message || '登录失败，请重试'
    showToast(msg)
  } finally {
    loading.value = false
  }
}

// 注册
async function onRegister() {
  loading.value = true
  try {
    await userStore.register(
      registerForm.phone,
      registerForm.password,
      registerForm.industry,
      registerForm.referralCode || undefined
    )
    await userStore.fetchUserInfo()
    router.push('/app')
  } catch (e) {
    const msg = e.response?.data?.message || '注册失败，请重试'
    showToast(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  /* 设计令牌（商务风） */
  --ink: #1F2421;
  --green-deep: #123F33;
  --green: #227B5B;
  --green-soft: #EAF3EF;
  --bg-soft: #F6F8F7;
  --line: #E6EAE7;
  --warn: #C9932E;

  display: flex;
  min-height: 100vh;
  background: var(--bg-soft);
  color: var(--ink);
}

/* ───────────── 左：品牌区 ───────────── */
.brand-panel {
  flex: 1.15;
  background: linear-gradient(150deg, #0D2E26 0%, #123F33 55%, #1B5E46 100%);
  color: #F4F8F6;
  display: flex;
  position: relative;
  overflow: hidden;
}

/* 细腻光斑，代替原来的账本横格 */
.brand-panel::before {
  content: '';
  position: absolute;
  top: -120px;
  right: -80px;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.07) 0%, transparent 70%);
  pointer-events: none;
}

.brand-panel::after {
  content: '';
  position: absolute;
  left: -100px;
  bottom: -140px;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.brand-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 9vh 8% 48px;
  max-width: 560px;
  margin: 0 auto;
  width: 100%;
}

.brand-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 72px;
}

/* Logo：深绿圆角方块，白"账"字 */
.seal-logo {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: #fff;
  color: var(--green-deep);
  font-family: "Songti SC", "STSong", "SimSun", serif;
  font-size: 23px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.brand-wordmark {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 2px;
}

.brand-headline {
  font-size: 38px;
  font-weight: 700;
  line-height: 1.4;
  margin: 0 0 20px;
  letter-spacing: 1px;
}

.brand-sub {
  font-size: 15px;
  line-height: 1.9;
  color: rgba(244, 248, 246, 0.82);
  margin: 0;
}

.brand-feats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 44px;
}

.feat-pill {
  font-size: 12.5px;
  color: #F4F8F6;
  border: 1px solid rgba(244, 248, 246, 0.3);
  border-radius: 999px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(2px);
}

.brand-stamp {
  margin-top: auto;
  padding-top: 48px;
  font-size: 12px;
  letter-spacing: 3px;
  color: rgba(244, 248, 246, 0.5);
}

/* ───────────── 右：表单区 ───────────── */
.form-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: var(--bg-soft);
}

.form-card {
  width: min(410px, 100%);
  background: #fff;
  border-radius: 16px;
  padding: 34px 32px 24px;
  box-shadow: 0 20px 48px rgba(18, 63, 51, 0.1), 0 2px 8px rgba(18, 63, 51, 0.05);
  border: 1px solid var(--line);
  animation: card-in 0.5s ease both;
}

.card-head {
  margin-bottom: 6px;
}

.card-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 6px;
  letter-spacing: 1px;
}

.card-sub {
  font-size: 13.5px;
  color: var(--ink-3, #8A938D);
  margin: 0 0 14px;
}

/* Tabs */
.login-tabs :deep(.van-tabs__nav) {
  background: transparent;
  margin-bottom: 8px;
}

.login-tabs :deep(.van-tab) {
  font-size: 16px;
  color: #7A807B;
}

.login-tabs :deep(.van-tab--active) {
  color: var(--green-deep);
  font-weight: 600;
}

.login-tabs :deep(.van-tabs__line) {
  background: var(--green);
  height: 3px;
  border-radius: 3px;
}

/* 表单 */
.login-form :deep(.van-cell-group--inset) {
  margin: 0;
  background: transparent;
  border-radius: 0;
}

.login-form :deep(.van-cell) {
  background: transparent;
}

.login-form :deep(.van-field) {
  background: transparent;
  padding: 17px 2px;
  border-bottom: 1px solid var(--line);
  transition: border-color 0.2s;
}

.login-form :deep(.van-field:focus-within) {
  border-bottom-color: var(--green);
}

.login-form :deep(.van-field__left-icon) {
  color: var(--green-deep);
  margin-right: 10px;
}

.login-form :deep(.van-field__control) {
  font-size: 15.5px;
}

.login-form :deep(.van-field__control::placeholder) {
  color: #B6BBB4;
}

/* 按钮 */
.form-footer {
  padding: 26px 0 4px;
}

.submit-btn {
  height: 50px;
  border-radius: 10px;
  background: var(--green-deep) !important;
  border: none !important;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  box-shadow: 0 8px 20px rgba(18, 63, 51, 0.25);
}

.submit-btn:active {
  background: var(--green) !important;
  transform: translateY(1px);
}

/* 演示账号提示 */
.demo-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 18px;
  padding: 11px 14px;
  background: var(--green-soft);
  border: 1px dashed rgba(18, 63, 51, 0.4);
  border-radius: 10px;
  font-size: 12.5px;
  color: var(--green-deep);
  cursor: pointer;
  transition: background 0.2s;
}

.demo-hint:active {
  background: #DFEFE7;
}

.demo-fill {
  margin-left: auto;
  color: var(--green);
  font-weight: 600;
}

/* 底部 */
.footer-tip {
  margin-top: 28px;
  font-size: 13px;
  color: #8A938D;
}

.version-tag {
  margin-top: 10px;
  font-size: 12px;
  color: var(--green);
  letter-spacing: 1px;
}

@keyframes card-in {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ───────────── 手机端：上下堆叠 ───────────── */
@media (max-width: 820px) {
  .login-page {
    flex-direction: column;
  }

  .brand-panel {
    flex: none;
  }

  .brand-inner {
    padding: 40px 24px 28px;
  }

  .brand-top {
    margin-bottom: 32px;
  }

  .brand-headline {
    font-size: 28px;
  }

  .brand-feats {
    margin-top: 22px;
    display: none;
  }

  .brand-stamp {
    display: none;
  }

  .form-panel {
    padding: 28px 18px 40px;
  }

  .form-card {
    padding: 26px 24px 20px;
  }
}

/* 尊重减少动效设置 */
@media (prefers-reduced-motion: reduce) {
  .form-card {
    animation: none;
  }
}
</style>
