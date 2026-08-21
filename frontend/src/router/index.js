import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/app',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requireAuth: false },
  },
  {
    path: '/app',
    name: 'Workbench',
    component: () => import('@/views/Workbench.vue'),
    meta: { requireAuth: true },
    children: [
      {
        path: '',
        redirect: '/app/chat/ai-bookkeeping',
      },
      {
        path: 'chat/:feature',
        name: 'Chat',
        component: () => import('@/views/ChatView.vue'),
        meta: { requireAuth: true },
      },
      {
        path: 'tutorial/tax',
        name: 'TaxTutorial',
        component: () => import('@/views/TaxTutorial.vue'),
        meta: { requireAuth: true },
      },
    ],
  },
  // 移动端旧页面保留，作为窄屏/过渡入口
  {
    path: '/bookkeeping',
    name: 'Bookkeeping',
    component: () => import('@/views/Bookkeeping.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/ledger',
    name: 'Ledger',
    component: () => import('@/views/Ledger.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/views/Analytics.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requireAuth: true },
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('@/views/Pricing.vue'),
    meta: { requireAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 页面标题映射
const titleMap = {
  Login: '登录 - AI虚拟文员',
  Workbench: 'AI虚拟文员',
  Chat: 'AI虚拟文员',
  Bookkeeping: '记账 - AI虚拟文员',
  Ledger: '台账 - AI虚拟文员',
  Analytics: '数据分析 - AI虚拟文员',
  Profile: '我的 - AI虚拟文员',
  Pricing: '定价 - AI虚拟文员',
  TaxTutorial: '报税流程教程 - AI虚拟文员',
}

// 路由守卫：检查登录状态 + 设置标题
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = titleMap[to.name] || 'AI虚拟文员'

  const token = localStorage.getItem('token')

  if (to.name === 'Login') {
    // 已登录用户访问登录页，直接跳转到工作台
    if (token) {
      next('/app')
    } else {
      next()
    }
  } else if (to.meta.requireAuth && !token) {
    // 需要认证但未登录，跳转登录页
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
