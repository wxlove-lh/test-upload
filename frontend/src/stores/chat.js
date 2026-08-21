import { defineStore } from 'pinia'
import { ref } from 'vue'
import { MENU_SECTIONS } from '@/config/menu'

// 消息类型：
// text - 纯文本气泡
// image - 图片消息（用户上传的）
// voucher-card - 凭证卡片
// bookkeeping-card - 记账核验卡片
// list - 列表卡片（查账/客户列表）

const STORAGE_KEY = 'aiclerk-chat-sessions'

// 从本地读取会话（刷新/下次打开还在，AI的"记忆"不丢）
function loadStoredSessions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return {}
    const parsed = JSON.parse(raw)
    // 序列化时函数（消息里按钮的handler）会丢失，恢复时把没有handler的按钮清掉，避免点了没反应
    for (const key of Object.keys(parsed)) {
      if (!Array.isArray(parsed[key])) continue
      parsed[key] = parsed[key].map(m => ({
        ...m,
        actions: (m.actions || []).filter(a => typeof a.handler === 'function'),
      }))
    }
    return parsed
  } catch (e) {
    return {}
  }
}

export const useChatStore = defineStore('chat', () => {
  // 每个功能项的会话消息（带本地持久化记忆）
  const sessions = ref(loadStoredSessions())

  let saveTimer = null
  function persist() {
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      try {
        const json = JSON.stringify(sessions.value, (k, v) => (k === 'handler' ? undefined : v))
        localStorage.setItem(STORAGE_KEY, json)
      } catch (e) {
        // 存储失败（空间不足等）不影响使用
      }
    }, 300)
  }

  // 查找功能项的 greeting
  function getFeatureConfig(featureId) {
    for (const section of MENU_SECTIONS) {
      const item = section.items.find(i => i.id === featureId)
      if (item) return item
    }
    return null
  }

  // 初始化会话（首次进入该功能时，插入 AI 开场白）
  function ensureSession(featureId) {
    if (!sessions.value[featureId] || sessions.value[featureId].length === 0) {
      const config = getFeatureConfig(featureId)
      const greeting = config?.greeting || '您好，有什么可以帮您？'
      sessions.value[featureId] = [
        { id: `g-${featureId}-${Date.now()}`, role: 'assistant', type: 'text', content: greeting, time: Date.now() },
      ]
      persist()
    }
    return sessions.value[featureId]
  }

  // 追加一条消息
  function addMessage(featureId, message) {
    if (!sessions.value[featureId]) ensureSession(featureId)
    sessions.value[featureId].push({
      id: `${featureId}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      time: Date.now(),
      ...message,
    })
    persist()
    return sessions.value[featureId]
  }

  // 清空会话
  function clearSession(featureId) {
    sessions.value[featureId] = []
    persist()
  }

  return { sessions, ensureSession, addMessage, clearSession, getFeatureConfig }
})
