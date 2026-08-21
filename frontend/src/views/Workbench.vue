<template>
  <div class="workbench">
    <!-- 左侧导航栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <!-- 品牌区 -->
      <div class="brand-area">
        <div class="brand-mark" @click="goProfile">
          <span class="brand-char">账</span>
        </div>
        <span class="brand-name">AI虚拟文员</span>
      </div>

      <!-- 用户身份区 -->
      <div class="user-area">
        <div class="avatar" @click="goProfile">
          <van-icon name="user-o" size="20" color="#fff" />
        </div>
        <div class="user-info">
          <span class="user-name">{{ displayName }}</span>
          <span class="user-plan">{{ planName }}</span>
        </div>
      </div>

      <!-- 功能菜单区 -->
      <nav class="menu-area">
        <div v-for="section in visibleMenu" :key="section.key" class="menu-section">
          <div class="section-title">{{ section.title }}</div>
          <div
            v-for="item in section.items"
            :key="item.id"
            class="menu-item"
            :class="{ active: currentFeature === item.id }"
            @click="selectFeature(item.id)"
          >
            <van-icon :name="item.icon" size="17" class="menu-icon" />
            <span class="menu-label">{{ item.label }}</span>
          </div>
        </div>
      </nav>

      <!-- 底部设置入口 -->
      <div class="sidebar-footer">
        <div class="menu-item" @click="goProfile">
          <van-icon name="setting-o" size="17" class="menu-icon" />
          <span class="menu-label">设置</span>
        </div>
      </div>
    </aside>

    <!-- 右侧聊天工作台 -->
    <main class="main-area">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getVisibleMenu, VERSION_NAMES } from '@/config/menu'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapsed = ref(false)

// 当前激活的功能项（教程页等独立页面按 route.name 匹配）
const currentFeature = computed(() => {
  if (route.name === 'TaxTutorial') return 'tax-tutorial'
  return route.params.feature || 'ai-bookkeeping'
})

// 当前用户版本
const plan = computed(() => userStore.userInfo?.subscription_plan || 'free')

// 可见菜单（按版本过滤）
const visibleMenu = computed(() => getVisibleMenu(plan.value))

// 版本名称
const planName = computed(() => VERSION_NAMES[plan.value] || '免费版')

// 用户显示名（脱敏手机号）
const displayName = computed(() => {
  const phone = userStore.userInfo?.phone
  if (!phone) return '未登录'
  if (phone.includes('****')) return phone
  return phone.length >= 7 ? phone.slice(0, 3) + '****' + phone.slice(7) : phone
})

// 点击功能项 → 有独立页面的直接跳页面，否则进入聊天会话
function selectFeature(featureId) {
  const item = visibleMenu.value.flatMap(s => s.items).find(i => i.id === featureId)
  if (item && item.route) {
    router.push(item.route)
    return
  }
  router.push(`/app/chat/${featureId}`)
}

function goProfile() {
  router.push('/profile')
}

// 进入工作台时拉取用户信息
// 原逻辑：watch plan 在 plan 为空时不触发，导致刷新页面后用户信息丢失、菜单退回免费版
// 现改为：userInfo 为空时（首次进入/刷新后）就主动拉取
watch(
  () => userStore.userInfo,
  (val) => {
    if (!val) userStore.fetchUserInfo()
  },
  { immediate: true }
)

// 窄屏响应式
function handleResize() {
  isCollapsed.value = window.innerWidth < 768
}
handleResize()
if (typeof window !== 'undefined') {
  window.addEventListener('resize', handleResize)
}
</script>

<style scoped>
.workbench {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg);
}

/* ── 左侧导航栏 ── */
.sidebar {
  width: 236px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--card);
  border-right: 1px solid var(--line);
  transition: width 0.2s;
}

.sidebar.collapsed {
  width: 64px;
}

/* 品牌区 */
.brand-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px 12px;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--brand);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-family: "Songti SC", "STSong", "SimSun", serif;
  box-shadow: 0 2px 8px rgba(18, 63, 51, 0.25);
}

.brand-char {
  font-size: 17px;
  font-weight: 700;
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--ink);
}

/* 用户身份区 */
.user-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px 14px;
  border-bottom: 1px solid var(--line);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--brand-strong));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow: hidden;
}

.user-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-plan {
  font-size: 11px;
  color: var(--ink-3);
  background: var(--brand-tint);
  padding: 2px 8px;
  border-radius: 999px;
  width: fit-content;
}

/* 菜单区 */
.menu-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px 10px;
}

.menu-section {
  margin-bottom: 18px;
}

.section-title {
  font-size: 11px;
  color: var(--ink-3);
  padding: 6px 10px 8px;
  letter-spacing: 0.5px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 9px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  color: var(--ink-2);
  font-size: 13.5px;
}

.menu-item:hover {
  background: var(--brand-tint);
}

.menu-item.active {
  background: var(--brand-soft);
  color: var(--brand);
  font-weight: 600;
}

.menu-icon {
  flex-shrink: 0;
}

.menu-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar.collapsed .menu-label,
.sidebar.collapsed .section-title,
.sidebar.collapsed .user-info,
.sidebar.collapsed .brand-name {
  display: none;
}

/* 底部设置入口 */
.sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid var(--line);
}

/* ── 右侧聊天工作台 ── */
.main-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg);
}
</style>
