# AI虚拟文员

面向饭店、吃食类店铺（夜宵摊、夫妻餐馆、早餐店、快餐店等）的AI记账+数据分析工具。

## 技术栈

### 后端
- Python Flask + SQLAlchemy
- DeepSeek V4-Pro（图片识别 + JSON提取）
- JWT认证
- PostgreSQL（生产）/ SQLite（开发）

### 前端
- Vue 3 + Vite
- Vant 4（移动端UI组件库）
- ECharts（图表）
- Pinia（状态管理）
- Axios（HTTP请求）

## 快速启动

### 后端
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY
python app.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

前端开发服务器默认运行在 http://localhost:3000，自动代理API到后端 http://localhost:5000。

## 项目结构
```
ai-virtual-clerk/
├── frontend/     # Vue 3 前端
├── backend/      # Python Flask 后端
└── README.md
```

## 核心功能
- 📸 拍照记账：AI识别收据/进货单/手写白条
- 🎤 语音记账：语音转文字提取记账信息
- 📋 台账管理：分页查询/筛选/修改/导出Excel
- 📊 数据分析：日历视图/柱状图/折线图/饼图/同比环比
- 👤 个人中心：套餐管理/推荐码/裂变记录
