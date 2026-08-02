<template>
  <div class="login-page">
    <!-- Logo区域 -->
    <div class="logo-section">
      <div class="logo-icon">
        <van-icon name="balance-o" size="48" color="#fff" />
      </div>
      <h1 class="app-title">AI虚拟文员</h1>
      <p class="app-subtitle">智能记账，轻松管理</p>
    </div>

    <!-- 登录/注册表单卡片 -->
    <div class="form-card">
      <van-tabs v-model:active="activeTab" class="login-tabs" line-width="60" title-active-color="#4FC3F7">
        <van-tab title="登录">
          <van-form @submit="onLogin" class="login-form">
            <van-cell-group inset :border="false">
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
            </van-cell-group>
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
            <van-cell-group inset :border="false">
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
                placeholder="请输入密码"
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
                placeholder="请确认密码"
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
                placeholder="请选择行业"
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
            </van-cell-group>
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
    </div>

    <!-- 底部提示 -->
    <div class="footer-tip">
      <span>前5次免费体验，无需付费即可使用</span>
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

// 登录
async function onLogin() {
  loading.value = true
  try {
    await userStore.login(loginForm.phone, loginForm.password)
    await userStore.fetchUserInfo()
    router.push('/bookkeeping')
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
    router.push('/bookkeeping')
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
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #BBDEFB 30%, #F5F5F5 60%);
  padding-bottom: 40px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 80px;
  padding-bottom: 32px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, #4FC3F7, #29B6F6);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(79, 195, 247, 0.3);
  margin-bottom: 16px;
}

.app-title {
  font-size: 24px;
  font-weight: 600;
  color: #37474F;
  margin: 0 0 8px 0;
}

.app-subtitle {
  font-size: 14px;
  color: #78909C;
  margin: 0;
}

.form-card {
  margin: 0 20px;
  background: #fff;
  border-radius: 16px;
  padding: 8px 0 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.login-tabs :deep(.van-tabs__nav) {
  background: transparent;
}

.login-tabs :deep(.van-tab) {
  font-size: 16px;
}

.login-form {
  padding: 16px 12px 0;
}

.login-form :deep(.van-cell-group--inset) {
  margin: 0;
  background: #F8F9FA;
  border-radius: 12px;
}

.login-form :deep(.van-field) {
  padding: 14px 16px;
}

.login-form :deep(.van-field__left-icon) {
  color: #90A4AE;
  margin-right: 8px;
}

.login-form :deep(.van-field__control) {
  font-size: 15px;
}

.form-footer {
  padding: 24px 16px 0;
}

.submit-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #4FC3F7, #29B6F6) !important;
  border: none !important;
}

.footer-tip {
  text-align: center;
  margin-top: 32px;
  color: #90A4AE;
  font-size: 13px;
}
</style>
