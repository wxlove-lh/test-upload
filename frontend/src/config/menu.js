/**
 * 功能菜单配置 + 版本门控 + 会话注册表
 *
 * version 字段控制门控：
 *   free / basic / standard / pro
 *   用户可见 = 从 free 到 自己版本 的所有区块
 *
 * chat.greeting 是该功能项点击后 AI 的开场白
 * chat.module   对应会话处理模块
 *
 * actions 是一键操作按钮：点一下直接执行，用户无需打字。
 * 每个 action 的 command 决定 ChatView 怎么处理：
 *   - quick-text       直接把 text 当作一条用户消息发给现有流程
 *   - tax-draft        调用后端生成报税底稿（kind: this-month/last-month/this-quarter 等）
 *   - tax-reminder     调用后端报税日历（真实规则 + 倒计时）
 *   - tax-tips         申报注意事项
 *   - report-category  按分类报表
 *   - report-quarterly 按季度报表
 *   - export-excel     导出账目 Excel
 *   - customers-list   客户台账列表（真实接口）
 *   - customers-add    打开新增客户弹窗
 *   - categories-list  收支分类列表（真实接口）
 *   - categories-add   打开新增分类弹窗
 *
 * 菜单项可带 route 字段：点击后直接跳转页面（如报税流程教程），不走聊天会话。
 *
 * 「跟AI商量」(ai-chat) 与其他任意功能里直接打字的默认走向：调用后端 /ai/chat，
 * AI 结合真实账目数据自由回答。
 */

// 版本排序（用于门控判断）
export const VERSION_ORDER = ['free', 'basic', 'standard', 'pro']

// 版本名称映射
export const VERSION_NAMES = {
  free: '免费版',
  basic: '基础版',
  standard: '标准版',
  pro: '专业版',
}

// 功能菜单区块（从上到下）
export const MENU_SECTIONS = [
  {
    key: 'free',
    version: 'free',
    title: '免费版功能',
    items: [
      {
        id: 'ai-chat',
        icon: 'smile-o',
        label: '跟AI商量',
        module: 'ai-chat',
        greeting: '我是您的AI文员。记账、查账、报税的事，都能直接打字跟我商量，我会结合您的账目回答。',
        actions: [
          { label: '这个月赚了多少？', command: 'quick-text', text: '这个月赚了多少？', type: 'primary' },
          { label: '我该交多少税？', command: 'quick-text', text: '我该交多少税？' },
          { label: '看看账，给店提个建议', command: 'quick-text', text: '看看我的账，给店提个建议' },
        ],
      },
      {
        id: 'ai-bookkeeping',
        icon: 'edit',
        label: 'AI识别记账',
        module: 'bookkeeping',
        greeting: '您好，我是您的AI记账文员。上传小票照片或直接告诉我收支，我帮您入账。',
        actions: [
          { label: '上传小票识别', command: 'bookkeeping-upload', type: 'primary' },
          { label: '记一笔支出', command: 'quick-text', text: '记一笔支出' },
          { label: '记一笔收入', command: 'quick-text', text: '记一笔收入' },
        ],
      },
      {
        id: 'categories',
        icon: 'apps-o',
        label: '收支分类',
        module: 'categories',
        greeting: '每个店的分类都不一样。分类可以自己加、自己改，记账的时候直接选，不用打字。',
        actions: [
          { label: '查看我的分类', command: 'categories-list', type: 'primary' },
          { label: '新增分类', command: 'categories-add' },
        ],
      },
      {
        id: 'inquiry',
        icon: 'search',
        label: '查账',
        module: 'inquiry',
        greeting: '我帮您查账，点下面的按钮就能直接看结果。',
        actions: [
          { label: '查本月收支', command: 'quick-text', text: '查这个月的账', type: 'primary' },
          { label: '查上月收支', command: 'quick-text', text: '查上个月的账' },
          { label: '查最近7天', command: 'quick-text', text: '查最近7天的账' },
        ],
      },
    ],
  },
  {
    key: 'basic',
    version: 'basic',
    title: '基础版功能',
    items: [
      {
        id: 'report',
        icon: 'chart-trending-o',
        label: '报表',
        module: 'report',
        greeting: '我帮您生成报表。选择时间段，立即生成收入支出汇总。',
        actions: [
          { label: '本月报表', command: 'quick-text', text: '生成这个月的报表', type: 'primary' },
          { label: '上月报表', command: 'quick-text', text: '生成上个月的报表' },
          { label: '按分类报表', command: 'report-category' },
          { label: '按季度报表', command: 'report-quarterly' },
          { label: '全年报表', command: 'quick-text', text: '生成今年的报表' },
        ],
      },
      {
        id: 'export',
        icon: 'down',
        label: '导出Excel',
        module: 'export',
        greeting: '把账目导出成 Excel 表格，方便保存和对账。',
        actions: [
          { label: '导出本月账目', command: 'export-excel', period: 'month', type: 'primary' },
          { label: '导出上月账目', command: 'export-excel', period: 'last-month' },
          { label: '导出全部账目', command: 'export-excel', period: 'all' },
        ],
      },
    ],
  },
  {
    key: 'standard',
    version: 'standard',
    title: '标准版功能',
    items: [
      {
        id: 'customers',
        icon: 'friends-o',
        label: '客户台账',
        module: 'customers',
        greeting: '客户台账帮您管理客户和往来账。',
        actions: [
          { label: '查看客户列表', command: 'customers-list', type: 'primary' },
          { label: '新增客户', command: 'customers-add' },
        ],
      },
      {
        id: 'ledger-detail',
        icon: 'bookmark-o',
        label: '收支详细账本',
        module: 'ledger-detail',
        greeting: '这里能看到每笔收支的明细。',
        actions: [
          { label: '本月明细', command: 'quick-text', text: '查看这个月的收支明细', type: 'primary' },
          { label: '上月明细', command: 'quick-text', text: '查看上个月的收支明细' },
        ],
      },
      {
        id: 'tax-reminder',
        icon: 'alarm-clock-o',
        label: '报税日期提醒',
        module: 'tax-reminder',
        greeting: '我帮您查一下最近的报税安排。',
        actions: [
          { label: '查申报时间表（倒计时）', command: 'tax-reminder', type: 'primary' },
          { label: '申报注意事项', command: 'tax-tips' },
        ],
      },
      {
        id: 'tax-draft',
        icon: 'description',
        label: '报税底稿',
        module: 'tax-draft',
        greeting: '点下面的按钮，我根据您的账目一键生成报税底稿。',
        actions: [
          { label: '生成本月报税底稿', command: 'tax-draft', kind: 'this-month', type: 'primary' },
          { label: '生成上月报税底稿', command: 'tax-draft', kind: 'last-month' },
          { label: '生成本季度报税底稿', command: 'tax-draft', kind: 'this-quarter' },
        ],
      },
      {
        id: 'tax-tutorial',
        icon: 'guide-o',
        label: '报税流程教程',
        module: 'tutorial',
        route: '/app/tutorial/tax',
      },
    ],
  },
  {
    key: 'pro',
    version: 'pro',
    title: '专业版功能',
    items: [
      {
        id: 'customers-unlimited',
        icon: 'friends',
        label: '客户台账（不限量）',
        module: 'customers-unlimited',
        greeting: '专业版客户台账，不限客户数量。',
        actions: [
          { label: '查看客户列表', command: 'customers-list', type: 'primary' },
          { label: '新增客户', command: 'customers-add' },
        ],
      },
    ],
  },
]

/**
 * 根据用户版本返回可见的功能项列表
 * @param {string} plan - 用户 subscription_plan
 * @returns {Array} [{ sectionTitle, items: [...] }]
 */
export function getVisibleMenu(plan) {
  const userLevel = VERSION_ORDER.indexOf(plan)
  if (userLevel === -1) return []

  const sections = []
  for (const section of MENU_SECTIONS) {
    if (VERSION_ORDER.indexOf(section.version) > userLevel) break
    sections.push(section)
  }
  return sections
}
