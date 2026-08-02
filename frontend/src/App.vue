<template>
  <div id="app">
    <router-view />
    <van-tabbar
      v-if="showTabbar"
      v-model="activeTab"
      :fixed="true"
      :safe-area-inset-bottom="true"
      @change="onTabChange"
    >
      <van-tabbar-item icon="edit" to="/bookkeeping">记账</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/ledger">台账</van-tabbar-item>
      <van-tabbar-item icon="chart-trending-o" to="/analytics">数据分析</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const activeTab = ref(0)

// 登录页不显示底部导航栏
const showTabbar = computed(() => {
  return route.path !== '/login'
})

// tab路由映射
const tabRoutes = ['/bookkeeping', '/ledger', '/analytics', '/profile']

// 监听路由变化，同步activeTab
watch(
  () => route.path,
  (path) => {
    const index = tabRoutes.indexOf(path)
    if (index !== -1) {
      activeTab.value = index
    }
  },
  { immediate: true }
)

function onTabChange(index) {
  router.push(tabRoutes[index])
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
