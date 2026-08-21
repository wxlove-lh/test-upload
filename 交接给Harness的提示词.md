# AI 虚拟文员项目交接提示词

> 把下面整个代码块的内容复制给 DeepSeek Harness(或任何 AI 编程助手),它就能接手这个项目。

```
【项目交接说明】请先完整读完下面内容,再开始工作。

# 项目:AI虚拟文员(记账 + 报税辅助 SaaS)

## 一句话定位
面向餐饮小店/个体户(小吃店、早餐店、烧烤店等)的记账 + 税务申报辅助工具。
核心不是记账,而是帮客户把零散数据整理成合规账本、生成报表、辅助报税(不代替报税)。
记账功能是引流入口,老板可截图小票存为凭证供日后核验/导出。

## 技术栈
- 后端:Python Flask + SQLAlchemy + JWT(flask-jwt-extended),SQLite(开发)/PostgreSQL(生产)
- 前端:Vue 3 + Vite + Vant 4 + Pinia + Vue Router + ECharts + Axios
- AI:DeepSeek(图片识别收据,需要 DEEPSEEK_API_KEY)
- 文档生成:python-docx / openpyxl

## 目录结构
- backend/          Flask 后端
  - app.py          应用入口,注册所有 blueprint
  - config.py       配置(dev/prod,SQLite默认)
  - extensions.py   db/migrate/jwt 实例
  - models/         User / Transaction / ModificationLog / Category / ReferralRecord / Coupon
  - routes/         auth(登录注册) / transaction(记账/查账/导出/凭证) / analytics(报表) / ai(识别/报税底稿) / category
  - services/       deepseek_service(AI识别) / comparison(双次识别比对) / export_service(Excel导出) / tax_service(报税底稿生成)
  - prompts/        receipt_prompt.txt(小票识别提示词)
  - requirements.txt
- frontend/         Vue 3 前端
  - src/views/      Login / Workbench(工作台) / ChatView(聊天操作区) / Bookkeeping / Ledger / Analytics / Profile / Pricing
  - src/components/ ReceiptUploader / TransactionList / ChartPanel / VoucherPanel / EditTransaction 等
  - src/config/menu.js      功能菜单 + 版本门控 + 一键操作按钮配置
  - src/stores/     user / chat / bookkeeping / analytics
  - src/api/        axios 封装,含 auth / transaction / analytics / ai / referral
  - src/styles/theme.css   全局设计令牌(深绿主色 #123F33,现代商务风)
- docbuild/         文档生成脚本 + 知识地基
- demo_server.py    一键演示服务器(同时提供前端静态文件 + 后端API)
- 启动演示.bat      Windows双击启动脚本(自动npm build + 启动后端 + 开浏览器)

## 运行方式(Windows)
双击「启动演示.bat」→ 自动 npm build 前端 → 启动 demo_server.py → 浏览器打开 http://localhost:5000
演示账号:13812345678 / 123456(已升级为专业版 pro / 999次,能看全部功能)
demo_server.py 每次启动会把演示账号保持为专业版。

## 当前已完成
1. 登录/注册(手机号+密码,JWT,免费5次)
2. 聊天式工作台:左侧版本门控菜单 + 右侧聊天操作区(ChatView)
3. 一键操作按钮:每个功能进聊天区顶部有一排按钮,点一下直接出结果,不用打字
   - AI记账:上传小票识别 / 记支出 / 记收入
   - 查账:本月/上月/最近7天
   - 报表:本月/上月/全年汇总卡片
   - 导出Excel:本月/上月/全部
   - 报税底稿:本月/上月(后端 tax_service 自动归集成本费用+税负估算)
   - 报税日期提醒:本月/季度
   - 客户台账:目前是"开发中"提示,后端无模型
4. 报税底稿:已接后端 /api/ai/tax-draft,按收入/成本/费用/利润归集,附增值税+个税估算参考
5. 凭证功能:交易可上传/查看小票图片,报税备查
6. 数据分析:日历视图/柱状图/折线图/饼图/同比环比
7. 全站视觉:现代简洁商务风,深绿主色,白底+大卡片+留白

## 待办/下一步(按优先级)
1. 【最重要】客户台账:建 Customer 模型 + 增删改查接口 + 前端列表/新增,替换现在的"开发中"提示
2. 报税底稿想更灵活:可选接 DeepSeek 生成(现在已内置本地规则版,可先用)
3. 报表/导出增强:按分类报表、季度报表
4. 税务提醒:接真实申报日期规则,按客户行业/地区差异
5. 后端 payment / referral 蓝图未实现(app.py 已预留,会自动跳过)
6. 报税知识库 docbuild/个体户报税知识地基.md 可继续扩充,做成前端教程页

## 关键注意点
- 不要动 frontend/postcss.config.cjs:曾用 px-to-viewport 导致电脑端放大5倍,已关闭,勿恢复
- 前端全局样式在 src/styles/theme.css,改视觉先看这里
- 用户不懂编程,要避免技术术语,所有交互面向餐饮老板
- AI识别需要 DeepSeek API Key 配在 backend/.env,没有Key时识别会失败但其他功能正常
- 报税底稿的税负估算是简化参考,产品文案要写"以税务机关核定为准"

## 税务业务知识(做报税功能必须懂,精简版)
### 个体户要交的税(四大块)
1. 增值税:小规模纳税人 月销≤10万/季≤30万 免征(2027-12-31前);超过按1%交
2. 个税(经营所得):5%~35% 五级累进;年应纳税所得额≤200万减半征收(2023-2027)
3. 附加税费:跟着增值税走,小规模减征50%
4. 其他:印花税、房产税等;个体户不交企业所得税
### 申报时间表(做提醒功能)
- 增值税+附加:月或季,期满15日内
- 个税经营所得预缴:季,季终15日内(1/4/7/10月)
- 个税经营所得年度汇算(B表):次年3月31日前
- 工商年报:每年1月1日~6月30日
- 关键:不管有没有收入都要申报,逾期加收滞纳金
### 征收方式与建账(决定账做多重)
- 核定征收:税务局定税额,简单,逐步收紧
- 查账征收:按真实收入-成本算税,需要规范记账,是主流趋势
- 建账标准:注册资金≥20万或月销≥4万→复式账;10万~20万或月销1.5万~4万→简易账;以下→收支凭证粘贴簿
- 简易账=经营收入账+经营费用账+购进账+盘点表+利润表 → 正好是现有记账功能覆盖的范围,记账功能天然就是简易账的数字化
- 账簿凭证保存10年;查账征收建议单独经营账户,公私分开
### 税表(产品要生成的交付物)
- A表:季度预缴,季终15日内
- B表:年度汇算,次年3月31日前
- C表:多处经营汇总,次年3月31日前
- 个税减半优惠系统自动认定,无需手动填
### 对产品设计的启示
- 记账功能 = 简易账数字化(收入/支出/分类/供应商/日期 正好构成简易账字段)
- 税表生成 = 把账本数字按规则映射到 A/B 表字段,是确定性计算,不是AI猜测
- 报税提醒 = 按时间表做倒计时,技术简单,价值直接
- 流程教学 = 把报税操作做成图文/视频,是差异化卖点
- 风险:税表算错→客户被罚→口碑崩塌,规则必须经懂税的人终审,产品内必须有免责声明
- 完整知识文档在 docbuild/个体户报税知识地基.md,做税务功能前先读它
```

## 怎么用(用户操作步骤)

### 方式一:让 Harness 读本地项目(推荐)
1. 打开 Harness,把工作区切换到项目文件夹:`C:\Users\19678\Documents\Qoder\2026-08-02\chat-1\ai-virtual-clerk`
2. 把上面代码块里的内容直接粘贴发给 Harness
3. 说一句你想让它做的事,比如:"继续做客户台账功能"

### 方式二:只给它提示词(不读本地代码)
1. 直接把上面代码块内容复制给 Harness
2. 它会基于描述重建代码,但可能和现有代码不完全一致(因为它没读你的文件)
