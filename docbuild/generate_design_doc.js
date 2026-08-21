/* AI虚拟文员 — 模块一 & 模块二 优化设计文档生成脚本 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, PageBreak, Footer, TabStopType, TabStopPosition,
} = require('docx');

// ─────────── 通用样式常量 ───────────
const FONT = '微软雅黑';
const PRIMARY = '1F6FB2';    // 主蓝
const DARK = '2D3748';       // 正文深灰
const GRAY = '6B7280';      // 次要灰
const LIGHT = 'E8F1FA';     // 浅蓝底
const GREEN = '2F855A';
const AMBER = 'B7791F';
const RED = 'C53030';
const PURPLE = '6B46C1';

function p(text, opts = {}) {
  const runs = Array.isArray(text) ? text : [{ text, color: opts.color || DARK, bold: opts.bold || false }];
  return new Paragraph({
    children: runs.map(r => new TextRun({
      text: r.text, bold: r.bold, italics: r.italics, color: r.color || opts.color || DARK,
      size: (r.size || opts.size || 21), font: r.font || FONT,
      highlight: r.highlight, break: r.break,
    })),
    spacing: { before: opts.before ?? 60, after: opts.after ?? 60, line: opts.line ?? 300 },
    alignment: opts.alignment || AlignmentType.LEFT,
    indent: opts.indent,
    bullet: opts.bullet,
    numbering: opts.numbering,
    style: opts.style,
    border: opts.border,
    keepNext: opts.keepNext,
  });
}

function h1(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, size: 30, font: FONT, color: PRIMARY })],
    spacing: { before: 360, after: 160 },
    heading: HeadingLevel.HEADING_1,
    border: { bottom: { color: PRIMARY, size: 6, style: BorderStyle.SINGLE, space: 4 } },
  });
}
function h2(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, size: 25, font: FONT, color: DARK })],
    spacing: { before: 240, after: 120 },
    heading: HeadingLevel.HEADING_2,
  });
}
function h3(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, size: 22, font: FONT, color: PRIMARY })],
    spacing: { before: 180, after: 80 },
    heading: HeadingLevel.HEADING_3,
  });
}

function bullet(text, opts = {}) {
  return p(text, { bullet: { level: 0 }, before: 30, after: 30, ...opts });
}

function note(text) {
  return new Paragraph({
    children: [new TextRun({ text: '【优化要点】', bold: true, color: PRIMARY, font: FONT, size: 21 }),
      new TextRun({ text, font: FONT, size: 21, color: DARK })],
    spacing: { before: 60, after: 80, line: 300 },
    shading: { type: ShadingType.CLEAR, fill: LIGHT },
    indent: { left: 120, right: 120 },
  });
}

// ─────────── 表格工具 ───────────
function table(headers, rows, opts = {}) {
  const widths = opts.widths || headers.map(() => 2400);
  const colCount = headers.length;
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((hd, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: opts.headerFill || '1F6FB2' },
      margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: hd, bold: true, size: 20, font: FONT, color: 'FFFFFF' })], alignment: AlignmentType.CENTER, spacing: { after: 0 } })],
    })),
  });
  const bodyRows = rows.map((r, ri) => new TableRow({
    children: r.map((cell, ci) => new TableCell({
      width: { size: widths[ci], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: ri % 2 === 1 ? 'F7F9FC' : 'FFFFFF' },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: Array.isArray(cell)
        ? cell.map((t) => new Paragraph({ children: [new TextRun({ text: t, size: 19, font: FONT, color: DARK })], spacing: { after: 20 } }))
        : [new Paragraph({ children: [new TextRun({ text: cell, size: 19, font: FONT, color: DARK })], spacing: { after: 0 } })],
    })),
  }));
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: [headerRow, ...bodyRows], alignment: AlignmentType.CENTER });
}

function spacer() { return new Paragraph({ children: [], spacing: { after: 60 } }); }

// ─────────── 文档内容 ───────────
const children = [];

// 封面
children.push(
  new Paragraph({ children: [new TextRun({ text: '', size: 10, font: FONT })], spacing: { before: 2000, after: 0 } }),
  new Paragraph({ children: [new TextRun({ text: 'AI虚拟文员', bold: true, size: 56, font: FONT, color: PRIMARY })], alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
  new Paragraph({ children: [new TextRun({ text: '产品设计规格文档', bold: true, size: 36, font: FONT, color: DARK })], alignment: AlignmentType.CENTER, spacing: { after: 400 } }),
  new Paragraph({ children: [new TextRun({ text: '模块一 · 左侧导航栏', size: 24, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
  new Paragraph({ children: [new TextRun({ text: '模块二 · AI识别记账', size: 24, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
  new Paragraph({ children: [new TextRun({ text: '含整体框架设计（桌面端布局 · 版本门控 · 会话体系）', size: 20, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER, spacing: { after: 600 } }),
  new Paragraph({ children: [new TextRun({ text: '版本 v0.1（优化稿）', size: 18, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: '2026-08-07', size: 18, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER }),
  new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { after: 0 }, pageBreakBefore: true }),
);

// 目录占位
children.push(h1('目录'));
children.push(p('一、设计优化说明', { after: 40 }));
children.push(p('二、整体框架（新增）', { after: 40 }));
children.push(p('三、模块一 · 左侧导航栏', { after: 40 }));
children.push(p('四、模块二 · AI识别记账', { after: 40 }));
children.push(p('五、与现有代码的差异映射', { after: 40 }));
children.push(p('六、开发顺序建议', { after: 40 }));
children.push(new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { after: 0 }, pageBreakBefore: true }));

// ═══════════ 一、设计优化说明 ═══════════
children.push(h1('一、设计优化说明'));
children.push(p('本设计在原始设计思路（左侧导航 + 聊天驱动记账）基础上，对照现有代码进行了系统性优化与补全。以下为本次优化的总体原则与核心决策。'));

children.push(h2('1.1 优化原则'));
children.push(bullet('聊天驱动：所有功能在右侧聊天区内完成，不跳出当前界面。'));
children.push(bullet('版本门控：功能可见性由用户订阅版本决定，低版本不可见高版本功能。'));
children.push(bullet('数据可核验：所有入账数据必须经过用户核对确认，保留完整审计轨迹。'));
children.push(bullet('风险可视化：低可信度数据以视觉方式明确标注，让用户知情确认。'));
children.push(bullet('渐进式呈现：识别结果逐步呈现，增强透明度和信任感。'));

children.push(h2('1.2 关键决策摘要'));
children.push(table(
  ['决策项', '原始设计', '优化后方案', '理由'],
  [
    ['版本命名', '免费/基础/标准/专业', 'free / basic / standard / pro（代码常量）', '与现有 free/basic/advanced/clerk 对齐并演进，避免歧义'],
    ['专业版菜单', '客户台账（不限量）', '客户台账并入专业版区块，带“不限量”标注；标准版不再单列', '同一功能在标准版与专业版同时出现会造成导航重复，视觉与逻辑均冲突'],
    ['95%阈值', '模型输出数值置信度', '以“双次识别 + 字段置信度”组合判定，可操作化（见 4.4）', '现有模型无法直接输出 95% 数值；需转化为可判定的规则'],
    ['整体框架', '仅两个模块描述', '补全桌面端整体框架：路由、会话、版本门控、数据模型', '两个模块依赖的导航/聊天底座目前不存在，需一并设计'],
    ['客户数据', '未定义', '新增 Customer 数据模型与 CRUD', '客户台账依赖，现有代码没有客户实体'],
    ['报税提醒', '未定义', '新增 TaxReminder 数据模型与配置', '申报倒计时需要可配置的申报日期与提醒规则'],
  ],
  { widths: [1400, 2200, 3200, 2200] }
));

children.push(note('文档定位：本设计为“规格 + 评审”性质，直接面向开发落地。每个模块均给出布局、交互、状态、异常与代码映射。'));
children.push(new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { after: 0 }, pageBreakBefore: true }));

// ═══════════ 二、整体框架 ═══════════
children.push(h1('二、整体框架（新增）'));
children.push(p('模块一与模块二共同依赖一个“桌面端外壳”：左侧导航栏 + 右侧聊天区。现有代码是移动端（Vant + 底部 Tab），本设计将应用升级为桌面端优先的聊天式工作台。'));

children.push(h2('2.1 产品形态变化'));
children.push(table(
  ['维度', '现有实现', '目标形态'],
  [
    ['使用场景', '手机移动端（Vant）', '桌面浏览器为主，兼顾窄屏响应式'],
    ['主交互', '页面 + 表单 + 弹窗', '左侧导航 + 右侧聊天区'],
    ['布局', '底部 4-Tab 导航', '左侧固定导航栏 + 右侧聊天工作台'],
    ['导航结构', '记账/台账/数据分析/我的', '按版本分区的功能菜单（模块一）'],
    ['路由', '/bookkeeping、/ledger 等页面级', '工作台外壳 + 聊天会话承载全部功能'],
  ],
  { widths: [1500, 3300, 3200] }
));

children.push(h2('2.2 布局结构'));
children.push(bullet('整体分左右两栏：左侧导航栏（固定宽度 220px，版本底色）；右侧聊天工作台（自适应剩余宽度，白底）。'));
children.push(bullet('右侧聊天区采用“消息流”模式：上方为历史消息列表，底部为统一输入区。'));
children.push(bullet('输入区包含三个操作入口：文字输入框、图片上传按钮、语音按钮，三者平级。'));
children.push(bullet('窄屏（< 768px）时导航栏可收起为图标条，聊天区占满剩余空间（响应式降级，不阻塞首版）。'));

children.push(h2('2.3 路由与状态设计'));
children.push(h3('2.3.1 路由结构'));
children.push(p('新增工作台外壳路由，功能项不再各自占一个页面：', { after: 40 }));
children.push(p('/login → /app（工作台外壳，requireAuth）→ /app/chat/:feature', { color: PRIMARY, bold: true, after: 40 }));
children.push(table(
  ['路径', '组件', '说明'],
  [
    ['/login', 'Login.vue', '登录注册（沿用现有）'],
    ['/app', 'Workbench.vue（新增）', '左侧导航 + 右侧聊天区外壳'],
    ['/app/chat/:feature', 'ChatView.vue（新增）', '会话视图，按 feature 加载对应对话'],
    ['/pricing', 'Pricing.vue', '套餐页（沿用现有，改为从工作台内嵌打开）'],
  ],
  { widths: [2000, 3200, 2800] }
));
children.push(p('现有 /bookkeeping、/ledger、/analytics、/profile 页面保留，作为窄屏/过渡期入口，不阻塞首版迁移。', { color: GRAY, size: 20 }));

children.push(h3('2.3.2 会话持久化'));
children.push(bullet('每个功能项对应一条独立会话（chat session），互不混淆。'));
children.push(bullet('会话消息存库（新增 Message 表），刷新不丢失；支持会话内继续操作。'));
children.push(bullet('消息包含 role（user/assistant/system）、type（text/image/card/form）、payload（JSON）、关联实体（transaction/customer/attachment）。'));
children.push(bullet('当前代码 token 仅存 localStorage，多标签页不同步；建议改为 Pinia 持久化 + 跨标签同步（storage 事件）。'));

children.push(h2('2.4 版本门控机制'));
children.push(h3('2.4.1 版本常量与菜单配置'));
children.push(p('在代码中集中定义功能菜单与版本门控，而非散落在各页面。建议新增 frontend/src/config/menu.js：', { after: 40 }));
children.push(table(
  ['版本', '代码常量', '可见区块'],
  [
    ['免费版', 'free', '免费版功能'],
    ['基础版', 'basic', '免费版 + 基础版'],
    ['标准版', 'standard', '免费版 + 基础版 + 标准版'],
    ['专业版', 'pro', '免费版 + 基础版 + 标准版 + 专业版'],
  ],
  { widths: [1400, 2000, 3600] }
));
children.push(p('菜单数据结构建议：{ id, label, icon, version, chat: { greeting, module } }，version 字段控制门控，chat 字段声明点击后的对话行为。'));
children.push(note('现有代码 subscription_plan 取值为 free/basic/advanced/clerk。上线时需在用户模型中补充 standard/pro 取值，并对存量 advanced 用户做迁移映射（advanced→standard，clerk→pro），避免老用户功能消失。'));

children.push(h3('2.4.2 门控判定位置'));
children.push(bullet('前端：按用户 subscription_plan 过滤菜单，低版本不渲染高版本区块（模块一规则）。'));
children.push(bullet('后端：每个受控 API 增加版本校验装饰器/中间件，防止直接调接口越权（如 export 接口仅 basic 及以上可调）。'));
children.push(bullet('入口拦截：免费额度用尽时，在导航入口/开场白处直接提示升级，不进入识别流程。'));

children.push(h2('2.5 数据模型影响'));
children.push(table(
  ['新增模型', '用途', '关键字段'],
  [
    ['Customer（客户台账）', '记录经营客户/供应商往来', 'user_id、name、phone、type(客户/供应商)、total_amount、created_at'],
    ['TaxReminder（报税提醒）', '申报倒计时与配置', 'user_id、tax_type、due_date、remind_days、status'],
    ['ChatSession / Message', '会话持久化', 'user_id、feature、messages(payload JSON)、created_at'],
    ['Attachment（附件）', '报税底稿/凭证图片', 'user_id、message_id、type、url、created_at'],
  ],
  { widths: [2400, 2200, 3400] }
));
children.push(p('现有 Transaction 模型已具备 ai_confidence、ai_match_status、source_image_url、ModificationLog，可直接支撑核验卡片与审计需求，无需大改。', { color: GRAY, size: 20 }));
children.push(new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { after: 0 }, pageBreakBefore: true }));

// ═══════════ 三、模块一 · 左侧导航栏 ═══════════
children.push(h1('三、模块一 · 左侧导航栏'));
children.push(p('本节在原始设计确认稿基础上优化，标注“【优化要点】”处为本次修订，其余沿用确认稿。'));

children.push(h2('3.1 整体定位'));
children.push(p('屏幕最左侧的竖长区域，固定不动，是软件的总入口。宽度建议 220px；窄屏可收起为 64px 图标条。'));

children.push(h2('3.2 布局结构'));
children.push(bullet('第一块 · 用户身份区：圆形头像（40px）+ 等级标签（版本名），头像在上、标签紧贴头像下方，便于横排阅读。'));
children.push(bullet('第二块 · 功能菜单区：按版本分四个区块，从上到下：免费版功能、基础版功能、标准版功能、专业版功能。'));
children.push(bullet('第三块 · 底部设置入口：单独置于最底部（个人中心 / 套餐 / 设置）。'));
children.push(bullet('区块之间只用文字标题 + 上下间距分隔，不画框线、不加色块背景、不加分割线。'));

children.push(h2('3.3 功能菜单内容'));
children.push(table(
  ['区块', '功能项', '点击后的AI对话行为'],
  [
    ['免费版功能', 'AI识别记账', 'AI引导用户开始记账，列出三种输入方式（模块二）'],
    ['免费版功能', '查账', 'AI询问想查询哪个时间段的收支，展示结果'],
    ['基础版功能', '报表', 'AI生成报表展示（收支/利润趋势）'],
    ['基础版功能', '导出Excel', 'AI引导用户选择报表类型，确认后导出'],
    ['标准版功能', '客户台账', 'AI展示客户列表并询问操作（新增/查看/搜索）'],
    ['标准版功能', '收支详细账本', 'AI引导选择时间范围并展示明细'],
    ['标准版功能', '报税日期提醒', 'AI显示各税种申报倒计时'],
    ['标准版功能', '报税底稿', 'AI引导选择报表类型并生成底稿'],
    ['专业版功能', '客户台账（不限量）', 'AI展示客户列表，不受数量限制'],
  ],
  { widths: [1500, 1900, 4600] }
));

children.push(note('冲突处理：原设计中“客户台账”同时出现在标准版与专业版区块。同一功能在两个区块重复出现会造成导航歧义。优化为：客户台账仅出现在专业版区块（标注“不限量”），标准版不再重复列示。若产品坚持两个版本都显示，则建议标准版显示“客户台账（限量）”并用角标标注数量上限，避免视觉重复。'));

children.push(h2('3.4 区块可见规则'));
children.push(bullet('用户当前版本，可见从“免费版”到“当前版本”的所有区块。'));
children.push(bullet('免费版 → 只见免费版区块；基础版 → 免费版+基础版；标准版 → 免费版+基础版+标准版；专业版 → 全部四个区块。'));
children.push(bullet('【优化要点】区块标题即分隔元素。低版本用户看不到更高版本区块时，区块顺序固定，标题位置恒定，避免界面跳动。'));
children.push(bullet('【优化要点】版本升级/降级后，前端根据用户信息实时重新渲染菜单，无需刷新页面。'));

children.push(h2('3.5 背景颜色'));
children.push(p('左侧导航栏统一底色随当前用户版本变化，颜色淡到不刺眼、与白底不冲突：', { after: 40 }));
children.push(table(
  ['版本', '底色（示意）', '设计值建议'],
  [
    ['免费版', '极淡灰色', '#F7F8FA'],
    ['基础版', '极淡蓝色', '#F0F6FC'],
    ['标准版', '极淡橙色', '#FDF6EE'],
    ['专业版', '极淡紫色', '#F6F3FC'],
  ],
  { widths: [1600, 2000, 2600] }
));
children.push(note('建议底色用 CSS 变量统一管理（如 --nav-bg-free / --nav-bg-basic …），由用户版本动态切换。同色系的选中态在底色基础上加深 6%–10%，保证可辨识度。'));

children.push(h2('3.6 选中状态'));
children.push(bullet('被点击的功能项，叠加一层同色系浅色圆角背景（参考 iOS 18 圆润质感）。'));
children.push(bullet('建议：圆角 8–10px，左右留 8px 内边距，图标 + 文字整行高亮。'));
children.push(bullet('选中态示例：基础版（浅蓝底）时，选中项背景为 #D8E8F8，文字加深为 #1F6FB2。'));

children.push(h2('3.7 功能项点击行为'));
children.push(bullet('点击任意功能项，右侧聊天区立即出现对应 AI 对话（开场白）。'));
children.push(bullet('同一功能项重复点击：不重复插入开场白，滚动定位到该功能对应会话。'));
children.push(bullet('具体对话内容由各功能模块单独设计（本设计覆盖 AI识别记账；其余模块预留会话注册表）。'));
children.push(bullet('【优化要点】新增“会话注册表”设计：每个功能项声明一个 module 处理器，统一管理开场白、输入策略、消息渲染组件，避免聊天区逻辑堆成巨石。'));

children.push(h2('3.8 折叠状态与分隔方式'));
children.push(bullet('所有区块默认完全展开，无折叠功能。用户进入页面即看到所有可见区块与功能项。'));
children.push(bullet('区块之间不画框线、不加色块、不加分割线，仅靠文字标题与上下间距自然隔开。'));
children.push(bullet('【优化要点】为保证“无框线”时区块仍清晰可辨，区块标题统一字号（13px）、统一上下间距（16–20px），功能项缩进对齐。'));
children.push(new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { after: 0 }, pageBreakBefore: true }));

// ═══════════ 四、模块二 · AI识别记账 ═══════════
children.push(h1('四、模块二 · AI识别记账'));

children.push(h2('4.1 模块定位与入口'));
children.push(p('用户进入记账功能后的核心交互区，所有记账操作在右侧聊天区内完成，不跳出当前界面。入口为左侧导航栏「AI识别记账」。'));

children.push(h2('4.2 三种输入方式'));
children.push(p('同一界面内自由切换，用户任意选择。统一输入区设计：', { after: 40 }));
children.push(table(
  ['输入方式', '交互', '数据流'],
  [
    ['文字输入', '输入框直接输入自然语言，如“今天买菜花了235元”', 'AI 解析关键字段 → 信息补全 → 核验卡片'],
    ['图片上传', '上传小票/进货单/微信截图照片', 'AI 视觉识别（现有 /api/ai/recognize 双次识别）→ 逐条呈现 → 核验卡片'],
    ['语音输入', '按住录音，松开发送', '语音转文字（现有 /api/ai/voice 占位，需接入）→ 同文字流程'],
  ],
  { widths: [1400, 3200, 3400] }
));
children.push(note('现有 VoiceRecorder 已实现录音与回放，但后端 /api/ai/voice 为 501 占位。首版可先用浏览器 Web Speech API 做语音转文字，或接入第三方 ASR，文本进入与文字输入相同的信息补全流程。'));

children.push(h2('4.3 AI开场白'));
children.push(p('用户点击「AI识别记账」后，AI 主动发起第一轮对话，以气泡形式出现在右侧聊天区。内容含三项：', { after: 40 }));
children.push(bullet('告知当前处于记账状态。'));
children.push(bullet('列出三种可用操作方式：文字输入、图片上传、语音输入（平级展示，不设优先级）。'));
children.push(bullet('结束等待用户输入，不解释技术细节、不说明限额规则、不包含品牌宣传。'));
children.push(p('开场白文案建议（简洁、自然、口语化）：', { after: 40 }));
children.push(new Paragraph({
  children: [new TextRun({ text: '“您好，我是您的AI记账文员，现在可以开始记账了。您可以直接打字告诉我，或上传小票照片，也可以用语音说。”', italics: true, color: GRAY, font: FONT, size: 21 })],
  indent: { left: 240 }, spacing: { after: 120 },
}));

children.push(h2('4.4 信息补全原则'));
children.push(bullet('系统自动识别信息是否完整；缺少必要字段时主动追问缺失内容，直到完整才进入下一步。'));
children.push(bullet('只补缺项，不问多余问题。'));
children.push(bullet('必要字段：交易日期、金额、类型（收入/支出）、分类。供应商、备注为可选项。'));
children.push(bullet('分类缺失时追问顺序（优先级）：餐饮 → 采购 → 租金 → 工资 → 交通 → 其他。'));
children.push(note('原始设计分类顺序为“餐饮、采购、租金、工资、交通、其他”，与现有代码 12 个默认分类（食材、酒水饮料、房租、工资、水电燃气、耗材餐具、设备维修、运输配送、税费管理、其他支出、营业收入、其他收入）不完全一致。建议统一为“餐饮（食材/酒水）→ 房租 → 工资 → 水电/耗材 → 交通配送 → 其他”，由后端分类接口动态下发，前端不写死。'));

children.push(h2('4.5 数据可信度阈值原则（核心）'));
children.push(p('原设计以“95% 确认度”为阈值。由于现有模型输出的是 high/medium/low 三档置信度而非数值百分比，优化为可判定规则：', { after: 40 }));
children.push(table(
  ['确认度判定', '判定规则（可执行）', '处理方式'],
  [
    ['≥ 95%（高可信）', '双次识别结果一致，且字段置信度为 high', '直接填入核验卡片高可信区，不提问'],
    ['< 95%（低可信）', '字段置信度为 medium/low，或双次识别结果不一致', '填入核验卡片低可信区，逐条列出 + 位置提示 + 确认按钮'],
    ['完全识别不了', '字段无结果 / 空值', 'AI 明确告知是哪一项识别不了、标注位置，请用户补充或重拍'],
  ],
  { widths: [1800, 3200, 3000] }
));
children.push(note('映射关系：现有 DeepSeek 提示词输出 confidence_date/amount/category/supplier 四档 high/medium/low；双次识别（温度 0.3/0.7）金额差 ≤2% 判 high。因此“≥95%”落地为：字段置信度=high 且双次一致；否则进低可信区。无需改动识别服务核心逻辑，只需扩展前端核验卡片的呈现。'));

children.push(h2('4.6 逐步呈现原则'));
children.push(bullet('图片识别结果不一次性全部弹出，逐条缓慢出现（如每条间隔 300–500ms），让用户看到数据提取过程。'));
children.push(bullet('每条数据附带可信度状态徽标（高=绿/中=黄/低=红）。'));
children.push(bullet('呈现顺序建议：日期 → 类型 → 金额 → 分类 → 供应商 → 备注（与现有 prompt 提取字段顺序一致）。'));

children.push(h2('4.7 风险提示原则'));
children.push(table(
  ['风险等级', '场景', '呈现方式'],
  [
    ['高', '图片模糊/遮挡/折痕导致识别不清', '顶部风险横幅（浅红底）+ 对应字段标红'],
    ['中', '手写单据、部分字段不确定', '字段背景浅黄 + 确认按钮'],
    ['低', '字段缺失需补充', '字段高亮 + 引导补充提示'],
  ],
  { widths: [1400, 3200, 3400] }
));

children.push(h2('4.8 核验确认卡片（核心交付物）'));
children.push(p('所有数据入库前必须经用户核对，以卡片形式集中展示。卡片分为两个区域：', { after: 40 }));
children.push(h3('4.8.1 高可信度数据区'));
children.push(bullet('≥95% 确认度字段直接填入，不加疑问标记。'));
children.push(bullet('展示：字段名 + 值，绿色对勾角标。'));
children.push(h3('4.8.2 低可信度数据区'));
children.push(bullet('低于 95% 确认度字段统一整合，集中列出。'));
children.push(bullet('每条附位置提示（所在行/列、旁边字段，如“金额右侧手写数字”“供应商栏潦草”），方便定位。'));
children.push(bullet('每条后面跟一个确认按钮；点击后弹出修正输入框，或“确认无误”直接采纳。'));
children.push(bullet('所有低可信度字段处理完毕，卡片底部出现“全部确认，入库”按钮。'));
children.push(bullet('未处理完的低可信度字段，入库按钮置灰不可点。'));
children.push(p('卡片结构示意：', { after: 40 }));
children.push(new Paragraph({
  children: [new TextRun({ text: '【高可信区】日期 2026-08-02 ✓ · 金额 ¥235.50 ✓ · 类型 支出 ✓\n【低可信区】分类：食材？[位置：清单第一行] [修正] [确认]\n  供应商：张三？[位置：右下角签名] [修正] [确认]\n[ 全部确认，入库 ]（低可信字段全部处理后点亮）', font: FONT, size: 19, color: DARK })],
  indent: { left: 240 }, shading: { type: ShadingType.CLEAR, fill: 'F7F9FC' }, spacing: { after: 160 },
}));
children.push(p('每张卡片附带风险提示：“数据将影响报表与报税，请核对确认”。用户必须主动点击确认才能入库。', { color: AMBER, bold: true }));

children.push(h2('4.9 完成反馈与衔接'));
children.push(bullet('入库成功：明确反馈（如“已入账：支出 ¥235.50，分类 食材”），并主动询问是否继续操作。'));
children.push(bullet('入库成功后同步刷新该会话内的“今日快览”摘要。'));
children.push(bullet('失败反馈：简洁明了，引导重试或更换输入方式，不出现技术性错误信息。'));

children.push(h2('4.10 限额处理'));
children.push(bullet('免费用户剩余次数为 0 时，在入口处直接拦截并提示升级（不进入记账流程）。'));
children.push(bullet('免费用户每次识别成功扣减一次（现有逻辑已实现）。'));
children.push(bullet('基础版及以上不限制识别次数。'));

children.push(h2('4.11 异常处理'));
children.push(table(
  ['异常场景', '反馈文案（示例）', '引导'],
  [
    ['图片识别超时', '“识别超时，请检查网络后重试”', '重试或改文字/语音'],
    ['图片无法识别', '“这张图片没有识别到有效内容，请换一张清晰的”', '重拍或手动输入'],
    ['语音无权限', '“请允许麦克风权限后再试”', '引导开启权限'],
    ['网络错误', '“网络似乎不太稳定，请稍后再试”', '重试'],
  ],
  { widths: [2000, 3600, 2400] }
));

children.push(h2('4.12 提示词设计方向'));
children.push(bullet('结构化指导 + 自然语言兼容：引导按规范输入，同时允许自然语言，AI 提取关键字段。'));
children.push(bullet('信息完整性驱动：识别到缺失字段时，提示词自动转向补充询问。'));
children.push(bullet('入库前核验：必须包含核验引导，未经核验不入库。'));
children.push(bullet('识别结果透明度：让用户知道哪些字段已识别、哪些待确认。'));
children.push(bullet('报错口语化：避免技术术语。'));
children.push(note('现有 backend/prompts/receipt_prompt.txt 已很完善（97 行，含 12 分类规则、置信度规则、严格 JSON 格式）。建议在此基础上增加：低可信度字段的“位置提示”输出（如行/列、相邻字段）、缺失字段列表输出，供前端渲染核验卡片。'));
children.push(new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { after: 0 }, pageBreakBefore: true }));

// ═══════════ 五、与现有代码的差异映射 ═══════════
children.push(h1('五、与现有代码的差异映射'));
children.push(p('新设计落地所需改动的现有代码清单：', { after: 40 }));
children.push(h2('5.1 前端'));
children.push(table(
  ['文件', '改动'],
  [
    ['src/App.vue', '底部 Tab 替换为桌面工作台外壳（或保留移动端、新增桌面布局）'],
    ['src/router/index.js', '新增 /app、/app/chat/:feature 路由'],
    ['src/config/menu.js（新增）', '菜单配置 + 版本门控 + 会话注册表'],
    ['src/views/Workbench.vue（新增）', '左侧导航 + 右侧聊天区外壳'],
    ['src/views/ChatView.vue（新增）', '聊天消息流 + 统一输入区'],
    ['src/components/ReceiptUploader.vue', '识别结果改为聊天气泡 + 核验卡片呈现'],
    ['src/components/ConfirmDialog.vue', '升级为“高/低可信度分区核验卡片”'],
    ['src/components/EditTransaction.vue', '分类选项改为动态接口，修正硬编码分类'],
    ['src/stores/user.js', '版本常量映射更新（standard/pro）'],
    ['src/api/ai.js', '语音端点从占位改为真实调用'],
    ['src/stores/bookkeeping.js', '改为会话维度存储'],
  ],
  { widths: [3400, 4600] }
));
children.push(h2('5.2 后端'));
children.push(table(
  ['文件', '改动'],
  [
    ['models/user.py', 'subscription_plan 补充 standard/pro；存量 advanced/clerk 迁移映射'],
    ['models/customer.py（新增）', '客户台账数据模型'],
    ['models/tax_reminder.py（新增）', '报税提醒数据模型'],
    ['models/message.py（新增）', '会话消息持久化'],
    ['routes/referral.py（实现）', '现为占位（app.py 注册但文件缺失），Profile 页依赖'],
    ['routes/payment.py（实现）', '现为占位，套餐购买需要'],
    ['routes/ai.py', 'voice 端点实现；recognize 返回低可信字段位置提示'],
    ['services/deepseek_service.py', 'prompt 增加位置提示/缺失字段输出'],
    ['services/export_service.py', '支持报表类型选择（明细/汇总/按分类）'],
    ['routes/transaction.py', '增加版本门控校验装饰器'],
  ],
  { widths: [3400, 4600] }
));
children.push(h2('5.3 已知问题清单（建议一并修复）'));
children.push(bullet('前后端分类不一致：后端 12 默认分类 vs 前端 EditTransaction/Ledger 硬编码“餐饮/交通/购物”一套。'));
children.push(bullet('/api/referrals、/api/payments 后端注册但文件缺失，被静默跳过。'));
children.push(bullet('Analytics 页 fetchComparison 解析字段与后端 /comparison 返回结构不匹配（数字卡片显示 0）。'));
children.push(bullet('ChartPanel 柱/折线图读 d.date，后端 /trend 返回 period，X 轴可能为空。'));
children.push(bullet('生产环境 CORS 全开、JWT_SECRET_KEY 默认值兜底，部署需加固。'));
children.push(bullet('存在 backend/routes/transaction.py.bak 备份文件，建议清理。'));

// ═══════════ 六、开发顺序建议 ═══════════
children.push(h1('六、开发顺序建议'));
children.push(table(
  ['阶段', '内容', '说明'],
  [
    ['1 · 底座', '工作台外壳 + 路由 + 版本门控 + 会话骨架', '先跑通“点导航→出对话”'],
    ['2 · 模块一', '左侧导航栏完整实现（底色/选中态/区块规则）', '不依赖后端新模型'],
    ['3 · 模块二', 'AI识别记账聊天流程 + 核验卡片', '复用现有 recognize 接口，增强 prompt'],
    ['4 · 基础版功能', '报表、导出Excel 接入聊天', '复用现有 analytics/export 接口'],
    ['5 · 标准版功能', '客户台账、详细账本、报税提醒、报税底稿', '需新增 Customer/TaxReminder 模型'],
    ['6 · 专业版', '客户台账不限量 + 套餐购买闭环', '依赖 payment 路由实现'],
  ],
  { widths: [1800, 4200, 3000] }
));

children.push(spacer());
children.push(new Paragraph({ children: [new TextRun({ text: '—— 文档结束 ——', color: GRAY, size: 18, font: FONT })], alignment: AlignmentType.CENTER, spacing: { before: 400 } }));

// ─────────── 组装文档 ───────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 21, color: DARK } } },
  },
  sections: [{
    properties: {},
    children,
  }],
});

const outDir = path.resolve(__dirname, '..');
const outPath = path.join(outDir, 'AI虚拟文员_模块一模块二设计文档.docx');
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log('OK → ' + outPath);
}).catch(err => { console.error('FAIL', err); process.exit(1); });
