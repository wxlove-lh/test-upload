<template>
  <div class="page-container">
    <van-nav-bar title="选择套餐" left-arrow @click-left="$router.push('/profile')" />
    <div class="page-content">
      <!-- 顶部提示条 -->
      <van-notice-bar
        left-icon="volume-o"
        text="前5次免费体验，功能全开，满意再付费"
        background="#e8f4ff"
        color="#1989fa"
      />

      <!-- 套餐卡片列表 -->
      <div class="plans-wrapper">
        <!-- 基础版 -->
        <div class="plan-card plan-card--active">
          <div class="plan-badge">推荐</div>
          <h3 class="plan-name">基础版</h3>
          <div class="price-table">
            <div class="price-row">
              <div class="price-cell">
                <span class="price-label">日付</span>
                <span class="price-value">¥1<span class="price-unit">/天</span></span>
              </div>
              <div class="price-cell">
                <span class="price-label">月付</span>
                <span class="price-value">¥28<span class="price-unit">/月</span></span>
              </div>
              <div class="price-cell price-cell--highlight">
                <span class="price-label">
                  年付
                  <van-tag type="danger" size="small" class="save-tag">省166元</van-tag>
                </span>
                <span class="price-value">¥199<span class="price-unit">/年</span></span>
              </div>
            </div>
          </div>
          <van-button type="primary" block round @click="onSelectPlan('basic')">
            选择
          </van-button>
        </div>

        <!-- 进阶版 -->
        <div class="plan-card plan-card--disabled">
          <h3 class="plan-name">进阶版</h3>
          <div class="price-table">
            <div class="price-row">
              <div class="price-cell">
                <span class="price-label">日付</span>
                <span class="price-value">¥2<span class="price-unit">/天</span></span>
              </div>
              <div class="price-cell">
                <span class="price-label">月付</span>
                <span class="price-value">¥56<span class="price-unit">/月</span></span>
              </div>
              <div class="price-cell">
                <span class="price-label">年付</span>
                <span class="price-value">¥388<span class="price-unit">/年</span></span>
              </div>
            </div>
          </div>
          <van-button disabled block round>敬请期待</van-button>
        </div>

        <!-- 文员版 -->
        <div class="plan-card plan-card--disabled">
          <h3 class="plan-name">文员版</h3>
          <div class="price-table">
            <div class="price-row">
              <div class="price-cell">
                <span class="price-label">日付</span>
                <span class="price-value">¥4<span class="price-unit">/天</span></span>
              </div>
              <div class="price-cell">
                <span class="price-label">月付</span>
                <span class="price-value">¥112<span class="price-unit">/月</span></span>
              </div>
              <div class="price-cell">
                <span class="price-label">年付</span>
                <span class="price-value">¥688<span class="price-unit">/年</span></span>
              </div>
            </div>
          </div>
          <van-button disabled block round>敬请期待</van-button>
        </div>
      </div>

      <!-- 创始会员提示 -->
      <div class="founder-section">
        <van-notice-bar
          left-icon="star"
          text="创始会员特权：前200名注册用户，基础版年付仅需99元终身价！"
          background="#fff7e6"
          color="#ed6a0c"
          wrapable
        />
      </div>
    </div>

    <!-- 付费方式选择 -->
    <van-action-sheet
      v-model:show="showActionSheet"
      :actions="payActions"
      cancel-text="取消"
      description="选择付费方式"
      @select="onPaySelect"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'

const showActionSheet = ref(false)

const payActions = [
  { name: '日付 - ¥1/天', value: 'daily' },
  { name: '月付 - ¥28/月', value: 'monthly' },
  { name: '年付 - ¥199/年（推荐）', value: 'yearly' },
]

function onSelectPlan(plan) {
  if (plan === 'basic') {
    showActionSheet.value = true
  }
}

function onPaySelect(action) {
  showActionSheet.value = false
  showToast('支付功能开发中，请联系客服开通')
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f7f8fa;
}
.page-content {
  padding-bottom: 40px;
}
.plans-wrapper {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.plan-card {
  position: relative;
  background: #fff;
  border-radius: 12px;
  padding: 20px 16px;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.plan-card--active {
  border-color: #1989fa;
  background: linear-gradient(135deg, #f0f7ff 0%, #fff 100%);
}
.plan-card--disabled {
  opacity: 0.6;
  background: #f5f5f5;
}
.plan-badge {
  position: absolute;
  top: -1px;
  right: 16px;
  background: #1989fa;
  color: #fff;
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 0 0 8px 8px;
  font-weight: 500;
}
.plan-name {
  font-size: 18px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 16px;
}
.price-table {
  margin-bottom: 16px;
}
.price-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}
.price-cell {
  flex: 1;
  text-align: center;
  padding: 10px 4px;
  background: #fafafa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.price-cell--highlight {
  background: #e8f4ff;
}
.price-label {
  font-size: 12px;
  color: #969799;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.price-value {
  font-size: 18px;
  font-weight: bold;
  color: #323233;
}
.price-unit {
  font-size: 12px;
  font-weight: normal;
  color: #969799;
}
.save-tag {
  margin-left: 2px;
}
.founder-section {
  padding: 0 16px;
  margin-top: 8px;
}
:deep(.van-notice-bar) {
  border-radius: 8px;
}
</style>
