# AI虚拟文员 · 完整代码交接包

> 本文件 = 【交接提示词】 + 【全部源码】,自包含,直接整体复制给 DeepSeek Harness 或其他 AI 编程助手即可。

---

# 第一部分:交接提示词

把下面这个代码块原样发给 AI,它就能理解项目并开始工作。

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

---

# 第二部分:完整源码清单

以下按目录结构列出项目全部源代码。文件路径即为相对项目根目录的位置。
说明:
- 不含 node_modules(依赖)、dist(构建产物)、venv(虚拟环境)、instance(数据库)、.git
- 后端识别小票需要 DeepSeek Key,配在 backend/.env(参考 backend/.env.example)


---

# 后端 (backend)

### 📄 backend/app.py
```
import os
from flask import Flask
from flask_cors import CORS
from config import config
from extensions import db, migrate, jwt


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)  # 开发阶段允许所有来源

    # 导入所有模型（确保SQLAlchemy能发现它们）
    from models import User, Transaction, ModificationLog, Category, ReferralRecord, Coupon  # noqa: F401

    # 注册Blueprint（route文件后续创建，用try/except优雅处理）
    _register_blueprints(app)

    # 在app context中创建所有表并初始化默认分类
    with app.app_context():
        db.create_all()
        from models.category import init_default_categories
        init_default_categories()

    return app


def _register_blueprints(app):
    """注册所有Blueprint，如果route文件尚未创建则跳过"""
    blueprints = [
        ('routes.auth', 'auth_bp', '/api/auth'),
        ('routes.transaction', 'transaction_bp', '/api/transactions'),
        ('routes.analytics', 'analytics_bp', '/api/analytics'),
        ('routes.ai', 'ai_bp', '/api/ai'),
        ('routes.payment', 'payment_bp', '/api/payments'),
        ('routes.referral', 'referral_bp', '/api/referrals'),
        ('routes.category', 'category_bp', '/api/categories'),
    ]

    for module_path, bp_name, url_prefix in blueprints:
        try:
            module = __import__(module_path, fromlist=[bp_name])
            bp = getattr(module, bp_name)
            app.register_blueprint(bp, url_prefix=url_prefix)
            app.logger.info(f"已注册Blueprint: {bp_name} -> {url_prefix}")
        except (ImportError, AttributeError) as e:
            app.logger.warning(f"跳过Blueprint {bp_name}: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
```

### 📄 backend/config.py
```
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 604800  # 7天

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 📄 backend/extensions.py
```
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
```

### 📄 backend/requirements.txt
```
Flask==3.1.1
Flask-CORS==5.0.1
Flask-JWT-Extended==4.7.1
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.1.0
openai==1.82.0
Pillow==11.2.1
python-dotenv==1.1.0
gunicorn==23.0.0
openpyxl==3.1.5
Werkzeug==3.1.3
psycopg2-binary==2.9.10
marshmallow==3.26.1
```

### 📄 backend/.env.example
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///dev.db
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

### 📄 backend/Dockerfile
```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```


## 📁 backend/models/

### 📄 backend/models/__init__.py
```
from models.user import User
from models.transaction import Transaction, ModificationLog
from models.category import Category
from models.referral import ReferralRecord
from models.coupon import Coupon
```

### 📄 backend/models/category.py
```
from extensions import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # NULL表示系统默认
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10))  # 'income' 或 'expense'
    is_default = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'


def init_default_categories():
    """创建12个默认分类（幂等操作：仅在不存在时插入）"""
    defaults = [
        # 支出(10个)
        {'name': '食材', 'type': 'expense', 'sort_order': 1},
        {'name': '酒水饮料', 'type': 'expense', 'sort_order': 2},
        {'name': '房租', 'type': 'expense', 'sort_order': 3},
        {'name': '工资', 'type': 'expense', 'sort_order': 4},
        {'name': '水电燃气', 'type': 'expense', 'sort_order': 5},
        {'name': '耗材餐具', 'type': 'expense', 'sort_order': 6},
        {'name': '设备维修', 'type': 'expense', 'sort_order': 7},
        {'name': '运输配送', 'type': 'expense', 'sort_order': 8},
        {'name': '税费管理', 'type': 'expense', 'sort_order': 9},
        {'name': '其他支出', 'type': 'expense', 'sort_order': 10},
        # 收入(2个)
        {'name': '营业收入', 'type': 'income', 'sort_order': 1},
        {'name': '其他收入', 'type': 'income', 'sort_order': 2},
    ]

    for item in defaults:
        existing = Category.query.filter_by(
            name=item['name'],
            type=item['type'],
            user_id=None
        ).first()
        if not existing:
            category = Category(
                user_id=None,
                name=item['name'],
                type=item['type'],
                is_default=True,
                sort_order=item['sort_order']
            )
            db.session.add(category)

    db.session.commit()
```

### 📄 backend/models/coupon.py
```
from extensions import db
from datetime import datetime


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2))
    source = db.Column(db.String(50), default='referral_reward')
    expiry_date = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='coupons')

    def __repr__(self):
        return f'<Coupon {self.id} user={self.user_id} amount={self.amount}>'
```

### 📄 backend/models/referral.py
```
from extensions import db
from datetime import datetime


class ReferralRecord(db.Model):
    __tablename__ = 'referral_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_amount = db.Column(db.Numeric(10, 2))
    reward_expiry = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='issued')  # issued/used/expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    inviter = db.relationship('User', foreign_keys=[inviter_id], backref='invited_records')
    invitee = db.relationship('User', foreign_keys=[invitee_id], backref='invited_by_records')

    def __repr__(self):
        return f'<ReferralRecord inviter={self.inviter_id} invitee={self.invitee_id}>'
```

### 📄 backend/models/transaction.py
```
from extensions import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(10))  # 'income' 或 'expense'
    category = db.Column(db.String(50))
    supplier = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending/confirmed/modified
    source_image_url = db.Column(db.String(500), nullable=True)
    voucher_urls = db.Column(db.Text, nullable=True)  # 凭证图片文件名，逗号分隔
    ai_confidence = db.Column(db.String(10))  # high/medium/low
    ai_match_status = db.Column(db.String(20))  # matched/needs_check
    confirmed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    modification_logs = db.relationship('ModificationLog', backref='transaction', lazy='dynamic')

    # 索引
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'transaction_date'),
        db.Index('idx_user_category', 'user_id', 'category'),
        db.Index('idx_user_supplier', 'user_id', 'supplier'),
    )

    def __repr__(self):
        return f'<Transaction {self.id} user={self.user_id} {self.type} {self.amount}>'


class ModificationLog(db.Model):
    __tablename__ = 'modification_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    field_name = db.Column(db.String(50))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ModificationLog {self.transaction_id} {self.field_name}>'
```

### 📄 backend/models/user.py
```
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(50))  # 夜宵摊/夫妻餐馆/早餐店/快餐店/小吃店
    subscription_plan = db.Column(db.String(20), default='free')  # free/basic/advanced/clerk
    subscription_type = db.Column(db.String(20), nullable=True)  # daily/monthly/yearly
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    referral_code = db.Column(db.String(10), unique=True)  # 6位随机字母数字
    referred_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    free_uses_remaining = db.Column(db.Integer, default=5)
    is_founding_member = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    referrer = db.relationship('User', remote_side=[id], backref='referrals')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    categories = db.relationship('Category', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_referral_code():
        """生成6位随机字母数字码（大写）"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=6))

    def __repr__(self):
        return f'<User {self.phone}>'
```


## 📁 backend/routes/

### 📄 backend/routes/__init__.py
```
```

### 📄 backend/routes/ai.py
```
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.comparison import ComparisonService
from services.tax_service import generate_tax_draft
from models.user import User
from extensions import db

logger = logging.getLogger(__name__)

# 注意：url_prefix在app.py中注册时已指定为'/api/ai'，这里不再重复设置
ai_bp = Blueprint('ai', __name__)

# 允许的图片类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
# 最大图片大小：10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024


def _allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@ai_bp.route('/recognize', methods=['POST'])
@jwt_required()
def recognize_receipt():
    """
    识别收据图片

    请求：multipart/form-data，字段名 'image'
    响应：识别结果JSON（包含confidence和match_status）
    """
    # 1. 检查图片文件
    if 'image' not in request.files:
        return jsonify({"message": "请上传收据图片"}), 400

    image_file = request.files['image']

    # 2. 检查文件名
    if not image_file.filename:
        return jsonify({"message": "未选择文件"}), 400

    # 3. 检查文件类型
    if not _allowed_file(image_file.filename):
        return jsonify({"message": "不支持的图片格式，请上传JPG/PNG/GIF/WebP图片"}), 400

    # 4. 读取图片并检查大小
    image_bytes = image_file.read()
    if len(image_bytes) == 0:
        return jsonify({"message": "图片文件为空"}), 400
    if len(image_bytes) > MAX_IMAGE_SIZE:
        return jsonify({"message": "图片过大（超过10MB），请压缩后重试"}), 400

    # 5. 检查用户权限与免费次数
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

    if user.subscription_plan == 'free' and user.free_uses_remaining <= 0:
        return jsonify({"message": "免费体验次数已用完，请订阅后继续使用"}), 403

    # 6. 双次识别
    try:
        comparison = ComparisonService()
        result = comparison.dual_recognize(image_bytes)
    except TimeoutError:
        logger.error("AI识别超时，用户ID: %s", user_id)
        return jsonify({"message": "识别超时，请检查网络后重试"}), 504
    except RuntimeError as e:
        logger.error("AI识别服务异常，用户ID: %s, 错误: %s", user_id, str(e))
        return jsonify({"message": f"识别失败：{str(e)}，请稍后重试"}), 503
    except Exception as e:
        logger.error("AI识别未知异常，用户ID: %s, 错误: %s", user_id, str(e), exc_info=True)
        return jsonify({"message": "识别服务异常，请稍后重试"}), 500

    # 7. 扣减免费次数（仅免费用户）
    if user.subscription_plan == 'free':
        user.free_uses_remaining = max(0, user.free_uses_remaining - 1)
        try:
            db.session.commit()
        except Exception as e:
            logger.error("扣减免费次数失败，用户ID: %s, 错误: %s", user_id, str(e))
            db.session.rollback()

    # 8. 返回结果
    return jsonify(result), 200


@ai_bp.route('/voice', methods=['POST'])
@jwt_required()
def voice_to_text():
    """语音转文字记账（预留端点，后续实现）"""
    return jsonify({"message": "语音记账功能开发中"}), 501


@ai_bp.route('/tax-draft', methods=['GET'])
@jwt_required()
def get_tax_draft():
    """一键生成报税底稿。

    Query 参数：
      - start_date / end_date：指定时间段（YYYY-MM-DD）
      - kind：this-month / last-month / all（未给日期时使用）
    """
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    kind = request.args.get('kind', 'this-month')

    try:
        draft = generate_tax_draft(user_id, start_date=start_date, end_date=end_date, kind=kind)
        return jsonify(draft), 200
    except Exception as e:
        logger.error("生成报税底稿失败，用户ID: %s, 错误: %s", user_id, str(e), exc_info=True)
        return jsonify({"message": "生成报税底稿失败，请稍后重试"}), 500
```

### 📄 backend/routes/analytics.py
```
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from extensions import db
from sqlalchemy import func, extract, case

analytics_bp = Blueprint('analytics', __name__)


def _parse_date(date_str, default=None):
    """解析日期字符串，支持 YYYY-MM-DD 格式"""
    if not date_str:
        return default
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return default


def _base_query(user_id, start_date, end_date):
    """构建基础查询：过滤用户、时间范围、有效状态"""
    return Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
        Transaction.status.in_(['confirmed', 'modified'])
    )


def _aggregate_by_date(query):
    """按 transaction_date 聚合 income/expense"""
    rows = query.with_entities(
        Transaction.transaction_date,
        func.sum(case(
            (Transaction.type == 'income', Transaction.amount),
            else_=0
        )).label('income'),
        func.sum(case(
            (Transaction.type == 'expense', Transaction.amount),
            else_=0
        )).label('expense'),
    ).group_by(Transaction.transaction_date).order_by(Transaction.transaction_date).all()
    return rows


@analytics_bp.route('/daily', methods=['GET'])
@jwt_required()
def daily():
    """每日数据（日历视图用）"""
    user_id = get_jwt_identity()

    today = date.today()
    # 默认本周（周一到周日）
    default_start = today - timedelta(days=today.weekday())
    default_end = default_start + timedelta(days=6)

    start_date = _parse_date(request.args.get('start_date'), default_start)
    end_date = _parse_date(request.args.get('end_date'), default_end)

    query = _base_query(user_id, start_date, end_date)
    rows = _aggregate_by_date(query)

    data = []
    for row in rows:
        income = float(row.income or 0)
        expense = float(row.expense or 0)
        data.append({
            'date': row.transaction_date.isoformat(),
            'income': income,
            'expense': expense,
            'profit': round(income - expense, 2),
        })

    return jsonify({
        'data': data,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    })


@analytics_bp.route('/trend', methods=['GET'])
@jwt_required()
def trend():
    """趋势数据（图表用），支持 day/week/month/year 维度"""
    user_id = get_jwt_identity()
    dimension = request.args.get('dimension', 'day')

    today = date.today()
    default_start = today - timedelta(days=today.weekday())
    default_end = default_start + timedelta(days=6)

    start_date = _parse_date(request.args.get('start_date'), default_start)
    end_date = _parse_date(request.args.get('end_date'), default_end)

    query = _base_query(user_id, start_date, end_date)

    if dimension == 'day':
        rows = _aggregate_by_date(query)
        data = [
            {
                'period': row.transaction_date.isoformat(),
                'income': float(row.income or 0),
                'expense': float(row.expense or 0),
                'profit': round(float(row.income or 0) - float(row.expense or 0), 2),
            }
            for row in rows
        ]

    elif dimension == 'week':
        # ISO周：使用 YEAR-WEEK 作为分组键（周一为一周开始）
        rows = query.with_entities(
            func.strftime('%Y-%W', Transaction.transaction_date).label('week_key'),
            func.min(Transaction.transaction_date).label('min_date'),
            func.sum(case(
                (Transaction.type == 'income', Transaction.amount),
                else_=0
            )).label('income'),
            func.sum(case(
                (Transaction.type == 'expense', Transaction.amount),
                else_=0
            )).label('expense'),
        ).group_by('week_key').order_by('week_key').all()

        data = []
        for row in rows:
            income = float(row.income or 0)
            expense = float(row.expense or 0)
            data.append({
                'period': row.min_date.isoformat(),
                'income': income,
                'expense': expense,
                'profit': round(income - expense, 2),
            })

    elif dimension == 'month':
        rows = query.with_entities(
            func.strftime('%Y-%m', Transaction.transaction_date).label('month_key'),
            func.sum(case(
                (Transaction.type == 'income', Transaction.amount),
                else_=0
            )).label('income'),
            func.sum(case(
                (Transaction.type == 'expense', Transaction.amount),
                else_=0
            )).label('expense'),
        ).group_by('month_key').order_by('month_key').all()

        data = []
        for row in rows:
            income = float(row.income or 0)
            expense = float(row.expense or 0)
            data.append({
                'period': row.month_key,
                'income': income,
                'expense': expense,
                'profit': round(income - expense, 2),
            })

    elif dimension == 'year':
        rows = query.with_entities(
            func.strftime('%Y', Transaction.transaction_date).label('year_key'),
            func.sum(case(
                (Transaction.type == 'income', Transaction.amount),
                else_=0
            )).label('income'),
            func.sum(case(
                (Transaction.type == 'expense', Transaction.amount),
                else_=0
            )).label('expense'),
        ).group_by('year_key').order_by('year_key').all()

        data = []
        for row in rows:
            income = float(row.income or 0)
            expense = float(row.expense or 0)
            data.append({
                'period': row.year_key,
                'income': income,
                'expense': expense,
                'profit': round(income - expense, 2),
            })
    else:
        return jsonify({'error': 'dimension 必须是 day/week/month/year'}), 400

    return jsonify({
        'dimension': dimension,
        'data': data,
    })


@analytics_bp.route('/category-ratio', methods=['GET'])
@jwt_required()
def category_ratio():
    """分类占比（饼图用）"""
    user_id = get_jwt_identity()

    today = date.today()
    default_start = today.replace(day=1)
    default_end = today

    start_date = _parse_date(request.args.get('start_date'), default_start)
    end_date = _parse_date(request.args.get('end_date'), default_end)
    tx_type = request.args.get('type', 'expense')

    if tx_type not in ('income', 'expense'):
        return jsonify({'error': 'type 必须是 income 或 expense'}), 400

    query = _base_query(user_id, start_date, end_date).filter(
        Transaction.type == tx_type
    )

    rows = query.with_entities(
        Transaction.category,
        func.sum(Transaction.amount).label('amount'),
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()

    total = sum(float(row.amount or 0) for row in rows)

    data = []
    for row in rows:
        amount = float(row.amount or 0)
        percentage = round(amount / total * 100, 1) if total > 0 else 0.0
        data.append({
            'category': row.category,
            'amount': amount,
            'percentage': percentage,
        })

    return jsonify({
        'type': tx_type,
        'data': data,
        'total': total,
    })


def _calc_period_summary(user_id, start_date, end_date):
    """计算某个时间段内的 income/expense/profit 汇总"""
    query = _base_query(user_id, start_date, end_date)
    row = query.with_entities(
        func.sum(case(
            (Transaction.type == 'income', Transaction.amount),
            else_=0
        )).label('income'),
        func.sum(case(
            (Transaction.type == 'expense', Transaction.amount),
            else_=0
        )).label('expense'),
    ).first()

    income = float(row.income or 0)
    expense = float(row.expense or 0)
    return {
        'income': income,
        'expense': expense,
        'profit': round(income - expense, 2),
    }


def _calc_change(current_val, previous_val):
    """计算变化百分比"""
    if previous_val == 0:
        return 100.0 if current_val > 0 else 0.0
    return round((current_val - previous_val) / abs(previous_val) * 100, 1)


@analytics_bp.route('/comparison', methods=['GET'])
@jwt_required()
def comparison():
    """同比/环比分析"""
    user_id = get_jwt_identity()

    today = date.today()
    default_start = today.replace(day=1)
    default_end = today

    start_date = _parse_date(request.args.get('start_date'), default_start)
    end_date = _parse_date(request.args.get('end_date'), default_end)

    # 当前时间段汇总
    current = _calc_period_summary(user_id, start_date, end_date)

    # 环比：上一个同等长度的时间段
    delta_days = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=delta_days - 1)
    prev_mom = _calc_period_summary(user_id, prev_start, prev_end)

    mom = {
        'income_change': _calc_change(current['income'], prev_mom['income']),
        'expense_change': _calc_change(current['expense'], prev_mom['expense']),
        'profit_change': _calc_change(current['profit'], prev_mom['profit']),
        'previous': prev_mom,
    }

    # 同比：去年同期
    try:
        yoy_start = start_date.replace(year=start_date.year - 1)
        yoy_end = end_date.replace(year=end_date.year - 1)
    except ValueError:
        # 处理闰年2月29日等特殊情况
        yoy_start = start_date.replace(year=start_date.year - 1, day=28)
        yoy_end = end_date.replace(year=end_date.year - 1, day=28)

    # 检查去年同期是否有数据
    yoy_query = _base_query(user_id, yoy_start, yoy_end)
    has_yoy_data = yoy_query.first() is not None

    if has_yoy_data:
        prev_yoy = _calc_period_summary(user_id, yoy_start, yoy_end)
        yoy = {
            'income_change': _calc_change(current['income'], prev_yoy['income']),
            'expense_change': _calc_change(current['expense'], prev_yoy['expense']),
            'profit_change': _calc_change(current['profit'], prev_yoy['profit']),
            'previous': prev_yoy,
        }
    else:
        yoy = None

    return jsonify({
        'current': current,
        'mom': mom,
        'yoy': yoy,
    })
```

### 📄 backend/routes/auth.py
```
import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from models.category import init_default_categories
from extensions import db

auth_bp = Blueprint('auth', __name__)


def serialize_user(user, mask_phone=True):
    """将User模型序列化为字典"""
    phone = user.phone
    if mask_phone and phone and len(phone) >= 7:
        phone = phone[:3] + '****' + phone[7:]

    return {
        'id': user.id,
        'phone': phone,
        'industry': user.industry,
        'subscription_plan': user.subscription_plan,
        'subscription_type': user.subscription_type,
        'subscription_expiry': user.subscription_expiry.isoformat() if user.subscription_expiry else None,
        'free_uses_remaining': user.free_uses_remaining,
        'referral_code': user.referral_code,
        'is_founding_member': user.is_founding_member,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': '请求体不能为空'}), 400

    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    industry = data.get('industry', '').strip()
    referral_code = data.get('referral_code', '').strip() if data.get('referral_code') else None

    # 校验必填字段
    if not phone:
        return jsonify({'message': '手机号不能为空'}), 400
    if not password:
        return jsonify({'message': '密码不能为空'}), 400
    if not industry:
        return jsonify({'message': '行业不能为空'}), 400

    # 校验手机号格式（11位数字）
    if not re.match(r'^\d{11}$', phone):
        return jsonify({'message': '手机号格式错误，需为11位数字'}), 400

    # 检查手机号是否已注册
    if User.query.filter_by(phone=phone).first():
        return jsonify({'message': '该手机号已注册'}), 409

    # 创建用户
    user = User(phone=phone, industry=industry)
    user.set_password(password)
    user.referral_code = User.generate_referral_code()

    # 处理推荐码
    if referral_code:
        referrer = User.query.filter_by(referral_code=referral_code.upper()).first()
        if referrer:
            user.referred_by = referrer.id
        else:
            return jsonify({'message': '推荐码无效'}), 400

    db.session.add(user)
    db.session.commit()

    # 初始化默认分类
    init_default_categories()

    # 生成token（注册后自动登录）
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': '注册成功',
        'token': access_token,
        'user': serialize_user(user),
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': '请求体不能为空'}), 400

    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()

    if not phone or not password:
        return jsonify({'message': '手机号和密码不能为空'}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user or not user.check_password(password):
        return jsonify({'message': '手机号或密码错误'}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': '登录成功',
        'token': access_token,
        'user': serialize_user(user),
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """获取当前登录用户信息"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': '用户不存在'}), 404

    return jsonify(serialize_user(user, mask_phone=False)), 200
```

### 📄 backend/routes/category.py
```
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from models.transaction import Transaction
from extensions import db

category_bp = Blueprint('category', __name__)


@category_bp.route('', methods=['GET'])
@jwt_required()
def list_categories():
    """获取分类列表：系统默认 + 当前用户自定义"""
    user_id = get_jwt_identity()

    categories = Category.query.filter(
        db.or_(
            Category.user_id.is_(None),
            Category.user_id == user_id
        )
    ).order_by(Category.type, Category.sort_order, Category.id).all()

    result = {'expense': [], 'income': []}

    for cat in categories:
        item = {
            'id': cat.id,
            'name': cat.name,
            'is_default': cat.is_default,
            'sort_order': cat.sort_order,
        }
        if cat.type in result:
            result[cat.type].append(item)

    return jsonify(result)


@category_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    """新增自定义分类"""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': '请提供请求体'}), 400

    name = data.get('name', '').strip()
    cat_type = data.get('type', '').strip()

    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400

    if cat_type not in ('income', 'expense'):
        return jsonify({'error': 'type 必须是 income 或 expense'}), 400

    # 检查同名分类是否已存在（同一用户，包括系统默认）
    existing = Category.query.filter(
        Category.name == name,
        Category.type == cat_type,
        db.or_(
            Category.user_id.is_(None),
            Category.user_id == user_id
        )
    ).first()

    if existing:
        return jsonify({'error': f'分类「{name}」已存在'}), 400

    # 获取当前最大 sort_order
    max_order = db.session.query(db.func.max(Category.sort_order)).filter(
        Category.type == cat_type,
        db.or_(
            Category.user_id.is_(None),
            Category.user_id == user_id
        )
    ).scalar() or 0

    category = Category(
        user_id=user_id,
        name=name,
        type=cat_type,
        is_default=False,
        sort_order=max_order + 1,
    )
    db.session.add(category)
    db.session.commit()

    return jsonify({
        'id': category.id,
        'name': category.name,
        'type': category.type,
        'is_default': category.is_default,
        'sort_order': category.sort_order,
    }), 201


@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """修改分类名称"""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': '请提供请求体'}), 400

    new_name = data.get('name', '').strip()
    if not new_name:
        return jsonify({'error': '分类名称不能为空'}), 400

    category = Category.query.get_or_404(category_id)

    # 权限校验：必须是系统默认或当前用户的分类
    if category.user_id is not None and category.user_id != user_id:
        return jsonify({'error': '无权修改该分类'}), 403

    # 检查新名称是否已被占用
    name_conflict = Category.query.filter(
        Category.name == new_name,
        Category.type == category.type,
        Category.id != category_id,
        db.or_(
            Category.user_id.is_(None),
            Category.user_id == user_id
        )
    ).first()

    if name_conflict:
        return jsonify({'error': f'分类名称「{new_name}」已被使用'}), 400

    if category.is_default and category.user_id is None:
        # 系统默认分类：不直接修改，创建一个新的用户自定义分类
        new_category = Category(
            user_id=user_id,
            name=new_name,
            type=category.type,
            is_default=False,
            sort_order=category.sort_order,
        )
        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            'id': new_category.id,
            'name': new_category.name,
            'type': new_category.type,
            'is_default': new_category.is_default,
            'sort_order': new_category.sort_order,
            'message': '基于系统默认分类创建了自定义分类',
        })
    else:
        # 用户自定义分类：直接修改
        category.name = new_name
        db.session.commit()

        return jsonify({
            'id': category.id,
            'name': category.name,
            'type': category.type,
            'is_default': category.is_default,
            'sort_order': category.sort_order,
        })


@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """删除分类"""
    user_id = get_jwt_identity()

    category = Category.query.get_or_404(category_id)

    # 只能删除自己的自定义分类
    if category.user_id != user_id:
        return jsonify({'error': '无权删除该分类'}), 403

    # 检查是否有关联的 Transaction 记录
    tx_count = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.category == category.name,
        Transaction.status.in_(['confirmed', 'modified'])
    ).count()

    if tx_count > 0:
        return jsonify({'error': '该分类下有账目记录，无法删除'}), 400

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': '分类已删除'})
```

### 📄 backend/routes/transaction.py
```
import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from decimal import Decimal

from extensions import db
from models.transaction import Transaction, ModificationLog
from services.export_service import generate_excel

from sqlalchemy import func

transaction_bp = Blueprint('transaction', __name__)

# 凭证图片允许的类型与大小
ALLOWED_VOUCHER_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_VOUCHER_SIZE = 10 * 1024 * 1024  # 10MB


def _voucher_allowed(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VOUCHER_EXTENSIONS


def voucher_names_to_urls(voucher_urls: str) -> list:
    """把数据库里逗号分隔的凭证文件名转成可访问的URL列表"""
    if not voucher_urls:
        return []
    names = [n for n in voucher_urls.split(',') if n]
    return [f'/api/transactions/vouchers/{n}' for n in names]


def serialize_transaction(t):
    """将Transaction对象序列化为字典"""
    return {
        'id': t.id,
        'user_id': t.user_id,
        'transaction_date': t.transaction_date.strftime('%Y-%m-%d') if t.transaction_date else None,
        'amount': float(t.amount) if t.amount else 0,
        'type': t.type,
        'category': t.category,
        'supplier': t.supplier,
        'notes': t.notes,
        'status': t.status,
        'source_image_url': t.source_image_url,
        'voucher_urls': voucher_names_to_urls(t.voucher_urls),
        'ai_confidence': t.ai_confidence,
        'ai_match_status': t.ai_match_status,
        'confirmed_at': t.confirmed_at.strftime('%Y-%m-%d %H:%M:%S') if t.confirmed_at else None,
        'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S') if t.created_at else None,
        'updated_at': t.updated_at.strftime('%Y-%m-%d %H:%M:%S') if t.updated_at else None,
    }


def parse_date(date_str):
    """解析日期字符串，返回date对象，失败返回None"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def build_transaction_query(user_id, args):
    """根据查询参数构建Transaction查询"""
    query = Transaction.query.filter_by(user_id=user_id)

    start_date = parse_date(args.get('start_date'))
    end_date = parse_date(args.get('end_date'))
    category = args.get('category')
    tx_type = args.get('type')

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if category:
        query = query.filter_by(category=category)
    if tx_type:
        query = query.filter_by(type=tx_type)

    return query


# ──────────────────────────────────────────────
# 端点1：POST /api/transactions - 确认入库
# ──────────────────────────────────────────────
@transaction_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        # 校验必填字段
        required = ['transaction_date', 'amount', 'type']
        for field in required:
            if field not in data or data[field] is None:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 校验type
        if data['type'] not in ('income', 'expense'):
            return jsonify({'error': "type只能是'income'或'expense'"}), 400

        # 解析日期
        tx_date = parse_date(data['transaction_date'])
        if tx_date is None:
            return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD'}), 400

        current_user_id = get_jwt_identity()

        transaction = Transaction(
            user_id=current_user_id,
            transaction_date=tx_date,
            amount=Decimal(str(data['amount'])),
            type=data['type'],
            category=data.get('category'),
            supplier=data.get('supplier'),
            notes=data.get('notes', ''),
            status='confirmed',
            confirmed_at=datetime.utcnow(),
            ai_confidence=data.get('ai_confidence'),
            ai_match_status=data.get('ai_match_status'),
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify(serialize_transaction(transaction)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建交易失败: {str(e)}'}), 500


# ──────────────────────────────────────────────
# 端点2：GET /api/transactions - 分页查账
# ──────────────────────────────────────────────
@transaction_bp.route('', methods=['GET'])
@jwt_required()
def list_transactions():
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = build_transaction_query(current_user_id, request.args)
        query = query.order_by(Transaction.transaction_date.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'items': [serialize_transaction(t) for t in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200

    except Exception as e:
        return jsonify({'error': f'查询交易失败: {str(e)}'}), 500


# ──────────────────────────────────────────────
# 端点3：PUT /api/transactions/<id> - 修改已入账数据
# ──────────────────────────────────────────────
@transaction_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    try:
        current_user_id = get_jwt_identity()

        transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()
        if not transaction:
            return jsonify({'error': '交易记录不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        # 可修改的字段映射
        updatable_fields = {
            'transaction_date': 'transaction_date',
            'amount': 'amount',
            'type': 'type',
            'category': 'category',
            'supplier': 'supplier',
            'notes': 'notes',
            'ai_confidence': 'ai_confidence',
            'ai_match_status': 'ai_match_status',
        }

        now = datetime.utcnow()

        for key, attr in updatable_fields.items():
            if key not in data:
                continue

            old_value = getattr(transaction, attr)
            new_value = data[key]

            # 特殊处理日期
            if key == 'transaction_date':
                new_date = parse_date(new_value)
                if new_date is None:
                    return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD'}), 400
                old_str = old_value.strftime('%Y-%m-%d') if old_value else None
                new_str = new_value
                if old_str != new_str:
                    log = ModificationLog(
                        transaction_id=transaction.id,
                        field_name=key,
                        old_value=str(old_str) if old_str else '',
                        new_value=str(new_str),
                        modified_at=now,
                    )
                    db.session.add(log)
                    transaction.transaction_date = new_date
            # 特殊处理金额
            elif key == 'amount':
                old_str = str(float(old_value)) if old_value else '0'
                new_str = str(float(new_value))
                if old_str != new_str:
                    log = ModificationLog(
                        transaction_id=transaction.id,
                        field_name=key,
                        old_value=old_str,
                        new_value=new_str,
                        modified_at=now,
                    )
                    db.session.add(log)
                    transaction.amount = Decimal(str(new_value))
            # 校验type
            elif key == 'type':
                if new_value not in ('income', 'expense'):
                    return jsonify({'error': "type只能是'income'或'expense'"}), 400
                if str(old_value) != str(new_value):
                    log = ModificationLog(
                        transaction_id=transaction.id,
                        field_name=key,
                        old_value=str(old_value) if old_value else '',
                        new_value=str(new_value),
                        modified_at=now,
                    )
                    db.session.add(log)
                    setattr(transaction, attr, new_value)
            else:
                if str(old_value) != str(new_value):
                    log = ModificationLog(
                        transaction_id=transaction.id,
                        field_name=key,
                        old_value=str(old_value) if old_value else '',
                        new_value=str(new_value),
                        modified_at=now,
                    )
                    db.session.add(log)
                    setattr(transaction, attr, new_value)

        transaction.status = 'modified'
        transaction.updated_at = now

        db.session.commit()

        return jsonify(serialize_transaction(transaction)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'修改交易失败: {str(e)}'}), 500


# ──────────────────────────────────────────────
# 端点4：GET /api/transactions/summary - 时间段汇总
# ──────────────────────────────────────────────
@transaction_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    try:
        current_user_id = get_jwt_identity()

        start_date = parse_date(request.args.get('start_date'))
        end_date = parse_date(request.args.get('end_date'))

        query = Transaction.query.filter(
            Transaction.user_id == current_user_id,
            Transaction.status.in_(['confirmed', 'modified']),
        )

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        total_income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user_id,
            Transaction.status.in_(['confirmed', 'modified']),
            Transaction.type == 'income',
            *([Transaction.transaction_date >= start_date] if start_date else []),
            *([Transaction.transaction_date <= end_date] if end_date else []),
        ).scalar() or 0

        total_expense = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user_id,
            Transaction.status.in_(['confirmed', 'modified']),
            Transaction.type == 'expense',
            *([Transaction.transaction_date >= start_date] if start_date else []),
            *([Transaction.transaction_date <= end_date] if end_date else []),
        ).scalar() or 0

        count = query.count()

        return jsonify({
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'total_profit': float(total_income) - float(total_expense),
            'count': count,
        }), 200

    except Exception as e:
        return jsonify({'error': f'获取汇总失败: {str(e)}'}), 500


# ──────────────────────────────────────────────
# 端点5：GET /api/transactions/export - 导出Excel
# ──────────────────────────────────────────────
@transaction_bp.route('/export', methods=['GET'])
@jwt_required()
def export_transactions():
    try:
        current_user_id = get_jwt_identity()

        query = build_transaction_query(current_user_id, request.args)
        query = query.order_by(Transaction.transaction_date.desc())
        transactions = query.all()

        # 计算summary
        start_date = parse_date(request.args.get('start_date'))
        end_date = parse_date(request.args.get('end_date'))

        base_filter = [
            Transaction.user_id == current_user_id,
            Transaction.status.in_(['confirmed', 'modified']),
        ]
        date_filters = []
        if start_date:
            date_filters.append(Transaction.transaction_date >= start_date)
        if end_date:
            date_filters.append(Transaction.transaction_date <= end_date)

        total_income = db.session.query(func.sum(Transaction.amount)).filter(
            *base_filter, Transaction.type == 'income', *date_filters
        ).scalar() or 0

        total_expense = db.session.query(func.sum(Transaction.amount)).filter(
            *base_filter, Transaction.type == 'expense', *date_filters
        ).scalar() or 0

        summary = {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'total_profit': float(total_income) - float(total_expense),
            'count': len(transactions),
        }

        excel_file = generate_excel(transactions, summary)

        filename = f'账目明细_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


# ──────────────────────────────────────────────
# 端点6：POST /api/transactions/<id>/vouchers - 上传凭证图片
# ──────────────────────────────────────────────
@transaction_bp.route('/<int:id>/vouchers', methods=['POST'])
@jwt_required()
def upload_vouchers(id):
    """给指定交易上传凭证图片（一张或多张），返回更新后的凭证URL列表"""
    try:
        current_user_id = get_jwt_identity()

        transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()
        if not transaction:
            return jsonify({'error': '交易记录不存在'}), 404

        files = request.files.getlist('images')
        if not files or len(files) == 0:
            return jsonify({'error': '请选择要上传的凭证图片'}), 400

        upload_dir = os.path.join(current_app.root_path, 'instance', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        saved_names = []
        for f in files:
            if not f.filename or not _voucher_allowed(f.filename):
                continue
            data = f.read()
            if len(data) == 0 or len(data) > MAX_VOUCHER_SIZE:
                continue
            ext = f.filename.rsplit('.', 1)[1].lower()
            name = f'{uuid.uuid4().hex}.{ext}'
            with open(os.path.join(upload_dir, name), 'wb') as out:
                out.write(data)
            saved_names.append(name)

        if not saved_names:
            return jsonify({'error': '没有成功上传的图片，请检查文件格式（JPG/PNG/GIF/WebP）和大小（≤10MB）'}), 400

        # 追加到现有凭证列表
        existing = [n for n in (transaction.voucher_urls or '').split(',') if n]
        transaction.voucher_urls = ','.join(existing + saved_names)
        transaction.status = 'modified' if transaction.status in ('confirmed', 'modified') else transaction.status
        db.session.commit()

        return jsonify({
            'message': f'成功上传 {len(saved_names)} 张凭证',
            'voucher_urls': voucher_names_to_urls(transaction.voucher_urls),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'上传凭证失败: {str(e)}'}), 500


# ──────────────────────────────────────────────
# 端点7：GET /api/transactions/vouchers/<filename> - 访问凭证图片
# ──────────────────────────────────────────────
@transaction_bp.route('/vouchers/<path:filename>', methods=['GET'])
@jwt_required()
def get_voucher(filename):
    """按文件名读取凭证图片（仅限上传该图片的用户）"""
    try:
        current_user_id = get_jwt_identity()

        # 防止路径穿越
        if '..' in filename or '/' in filename.replace('\\', '/'):
            return jsonify({'error': '非法文件名'}), 400

        # 校验该文件名属于当前用户
        tx = Transaction.query.filter(
            Transaction.user_id == current_user_id,
            Transaction.voucher_urls.like(f'%{filename}%'),
        ).first()
        if not tx:
            return jsonify({'error': '凭证不存在或无权访问'}), 404

        upload_dir = os.path.join(current_app.root_path, 'instance', 'uploads')
        file_path = os.path.join(upload_dir, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '凭证文件不存在'}), 404

        return send_file(file_path, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({'error': f'读取凭证失败: {str(e)}'}), 500
```


## 📁 backend/services/

### 📄 backend/services/comparison.py
```
import logging
import concurrent.futures
from services.deepseek_service import DeepSeekService

logger = logging.getLogger(__name__)

# 金额差异阈值：≤2% 视为匹配
AMOUNT_DIFF_THRESHOLD = 0.02


class ComparisonService:
    """双次识别比对服务：并行调用两次AI，比对结果并给出置信度"""

    def __init__(self):
        self.deepseek = DeepSeekService()

    def dual_recognize(self, image_bytes: bytes) -> dict:
        """
        双次识别并比对。
        用两个不同温度（0.3和0.7）并行调用DeepSeek，然后比对结果。

        Args:
            image_bytes: 图片二进制数据

        Returns:
            合并后的识别结果字典，包含confidence和match_status
        """
        # 并行调两次（温度0.3和0.7）
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(self.deepseek.recognize_with_temperature, image_bytes, 0.3)
            future_b = executor.submit(self.deepseek.recognize_with_temperature, image_bytes, 0.7)

            try:
                result_a = future_a.result(timeout=60)
            except concurrent.futures.TimeoutError:
                logger.error("第一次识别（temp=0.3）超时")
                raise RuntimeError("AI识别超时（第一次），请稍后重试")
            except Exception as e:
                logger.error("第一次识别（temp=0.3）失败: %s", str(e))
                raise

            try:
                result_b = future_b.result(timeout=60)
            except concurrent.futures.TimeoutError:
                logger.error("第二次识别（temp=0.7）超时")
                raise RuntimeError("AI识别超时（第二次），请稍后重试")
            except Exception as e:
                logger.error("第二次识别（temp=0.7）失败: %s", str(e))
                raise

        logger.info("第一次识别结果: %s", result_a)
        logger.info("第二次识别结果: %s", result_b)

        # 比对逻辑
        return self._compare(result_a, result_b)

    def _compare(self, result_a: dict, result_b: dict) -> dict:
        """比对两次识别结果，返回合并结果与置信度

        Args:
            result_a: 第一次识别结果（温度0.3，更确定性）
            result_b: 第二次识别结果（温度0.7，更多样性）

        Returns:
            合并后的结果字典
        """
        merged = {}
        confidence = {}
        all_matched = True

        # ---- 金额比对：差距≤2%算匹配 ----
        amount_a = self._safe_float(result_a.get('amount', 0))
        amount_b = self._safe_float(result_b.get('amount', 0))
        max_amount = max(amount_a, amount_b, 0.01)
        amount_diff = abs(amount_a - amount_b) / max_amount

        if amount_diff <= AMOUNT_DIFF_THRESHOLD:
            merged['amount'] = round(amount_a, 2)
            confidence['amount'] = 'high'
        elif amount_diff <= 0.05:
            # 差距在2%~5%之间，中等置信度
            merged['amount'] = round(amount_a, 2)
            confidence['amount'] = 'medium'
            all_matched = False
        else:
            merged['amount'] = round(amount_a, 2)
            confidence['amount'] = 'low'
            all_matched = False

        # ---- 分类比对：完全一致算匹配 ----
        cat_a = str(result_a.get('category', '')).strip()
        cat_b = str(result_b.get('category', '')).strip()
        if cat_a and cat_a == cat_b:
            merged['category'] = cat_a
            confidence['category'] = 'high'
        elif cat_a:
            merged['category'] = cat_a
            confidence['category'] = 'low'
            all_matched = False
        else:
            merged['category'] = cat_b or ''
            confidence['category'] = 'low'
            all_matched = False

        # ---- 供应商比对：完全一致算匹配 ----
        sup_a = str(result_a.get('supplier', '')).strip()
        sup_b = str(result_b.get('supplier', '')).strip()
        if sup_a and sup_a == sup_b:
            merged['supplier'] = sup_a
            confidence['supplier'] = 'high'
        elif sup_a:
            merged['supplier'] = sup_a
            confidence['supplier'] = 'low'
            all_matched = False
        else:
            merged['supplier'] = sup_b or ''
            confidence['supplier'] = 'low'
            all_matched = False

        # ---- 日期：优先用第一次的结果 ----
        date_a = str(result_a.get('transaction_date', '')).strip()
        date_b = str(result_b.get('transaction_date', '')).strip()
        merged['transaction_date'] = date_a or date_b
        if date_a and date_a == date_b:
            confidence['date'] = 'high'
        elif date_a:
            confidence['date'] = result_a.get('confidence_date', 'medium')
        else:
            confidence['date'] = 'low'
            all_matched = False

        # ---- 类型：优先用第一次的结果 ----
        merged['type'] = str(result_a.get('type', '支出')).strip()

        # ---- 备注 ----
        merged['notes'] = str(result_a.get('notes', '') or '').strip()

        # ---- 汇总 ----
        merged['confidence'] = confidence
        merged['match_status'] = 'matched' if all_matched else 'needs_check'

        return merged

    @staticmethod
    def _safe_float(value) -> float:
        """安全地将值转换为浮点数"""
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
```

### 📄 backend/services/deepseek_service.py
```
import os
import json
import base64
import re
import logging
from openai import OpenAI
from PIL import Image
import io

logger = logging.getLogger(__name__)


class DeepSeekService:
    """DeepSeek视觉模型调用服务，用于识别收据图片"""

    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.prompt = self._load_prompt()

    def _load_prompt(self):
        """加载提示词文件"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'prompts', 'receipt_prompt.txt'
        )
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("提示词文件未找到: %s，使用默认提示词", prompt_path)
            return "你是一个专门帮饭店记账的AI文员，请从图片中提取交易信息并以纯JSON格式返回。"

    def compress_image(self, image_bytes: bytes, max_size_mb: float = 2.0) -> bytes:
        """压缩图片到指定大小以内（MB）

        Args:
            image_bytes: 原始图片二进制数据
            max_size_mb: 目标最大文件大小（MB）

        Returns:
            压缩后的JPEG二进制数据
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 先缩小尺寸（如果图片非常大）
            max_dim = 1920
            if max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 逐步降低JPEG质量
            quality = 85
            buffer = io.BytesIO()
            while True:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality)
                size_mb = buffer.tell() / (1024 * 1024)
                if size_mb <= max_size_mb or quality <= 20:
                    break
                quality -= 15

            return buffer.getvalue()

        except Exception as e:
            logger.error("图片压缩失败: %s", str(e))
            # 压缩失败则返回原图，让API端处理
            return image_bytes

    def recognize(self, image_bytes: bytes, temperature: float = 0.3) -> dict:
        """
        调用DeepSeek识别图片中的收据信息

        Args:
            image_bytes: 图片二进制数据
            temperature: 生成温度，较低更确定性

        Returns:
            解析后的收据信息字典
        """
        # 压缩图片
        compressed = self.compress_image(image_bytes)
        # 转base64
        b64_image = base64.b64encode(compressed).decode('utf-8')

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]}
                ],
                temperature=temperature,
                max_tokens=2000,
                timeout=30,
            )

            content = response.choices[0].message.content
            logger.info("DeepSeek原始返回 (temp=%.1f): %s", temperature, content)
            return self._parse_response(content)

        except Exception as e:
            logger.error("DeepSeek API调用失败 (temp=%.1f): %s", temperature, str(e))
            raise RuntimeError(f"AI识别服务调用失败: {str(e)}")

    def recognize_with_temperature(self, image_bytes: bytes, temperature: float) -> dict:
        """指定温度调用识别（供双次比对使用）

        Args:
            image_bytes: 图片二进制数据
            temperature: 生成温度

        Returns:
            解析后的收据信息字典
        """
        return self.recognize(image_bytes, temperature=temperature)

    def _parse_response(self, content: str) -> dict:
        """解析AI返回的内容为JSON字典

        支持多种格式：
        - 纯JSON字符串
        - ```json ... ``` 代码块包裹
        - 带有前后多余文字的内容（正则提取）

        Args:
            content: AI返回的原始文本

        Returns:
            解析后的字典
        """
        if not content or not content.strip():
            raise ValueError("AI返回内容为空")

        text = content.strip()

        # 1. 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. 去除markdown代码块包裹
        md_pattern = r'^```(?:json)?\s*\n?(.*?)\n?\s*```$'
        md_match = re.search(md_pattern, text, re.DOTALL)
        if md_match:
            try:
                return json.loads(md_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3. 用正则找到第一个完整的JSON对象（花括号配对）
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 4. 更宽松的匹配：找所有 {...} 块
        for match in re.finditer(r'\{.*?\}', text, re.DOTALL):
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue

        # 5. 所有方式都失败
        logger.error("无法解析AI返回内容: %s", text[:500])
        raise ValueError(f"无法解析AI返回的JSON内容: {text[:200]}")
```

### 📄 backend/services/export_service.py
```
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime


def generate_excel(transactions, summary=None):
    """
    生成Excel文件
    transactions: Transaction对象列表
    summary: 汇总数据字典（可选）
    返回：BytesIO对象
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "账目明细"

    # 表头样式
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    # 写表头
    headers = ["日期", "类型", "金额", "分类", "供应商", "备注", "状态"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    # 写数据行
    for row_idx, t in enumerate(transactions, 2):
        ws.cell(row=row_idx, column=1, value=str(t.transaction_date))
        ws.cell(row=row_idx, column=2, value="收入" if t.type == "income" else "支出")
        amount_cell = ws.cell(row=row_idx, column=3, value=float(t.amount))
        amount_cell.number_format = '#,##0.00'
        # 收入绿色，支出红色
        if t.type == "income":
            amount_cell.font = Font(color="008000")
        else:
            amount_cell.font = Font(color="FF0000")
        ws.cell(row=row_idx, column=4, value=t.category)
        ws.cell(row=row_idx, column=5, value=t.supplier)
        ws.cell(row=row_idx, column=6, value=t.notes)
        ws.cell(row=row_idx, column=7, value="已确认" if t.status == "confirmed" else "已修改" if t.status == "modified" else "待确认")

    # 如果有汇总数据，在数据下方添加汇总行
    if summary:
        summary_row = len(transactions) + 3
        ws.cell(row=summary_row, column=1, value="汇总").font = Font(bold=True)
        ws.cell(row=summary_row, column=2, value=f"总收入: ¥{summary['total_income']:,.2f}")
        ws.cell(row=summary_row, column=3, value=f"总支出: ¥{summary['total_expense']:,.2f}")
        ws.cell(row=summary_row, column=4, value=f"净利润: ¥{summary['total_profit']:,.2f}")

    # 调整列宽
    for col in ws.columns:
        max_length = 0
        column_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = min(max_length + 4, 30)

    # 保存到BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
```

### 📄 backend/services/tax_service.py
```
"""报税底稿生成服务

把用户的账目数据按时间范围自动归类整理成一份"报税底稿"。
底稿的目的：帮客户把零散账目整理成合规、清晰的报表结构，供客户报税时参考，
不代替专业税务申报。所有税负均为估算参考，最终以税务政策为准。

数据归集规则（针对餐饮小店/个体户）：
- 收入：所有 income 交易 → 营业收入
- 成本（营业成本）：食材、酒水饮料、原材料等可直接归属到"卖出去的东西"上的支出
- 费用（期间费用）：房租、水电、工资、耗材、交通、通讯等经营开支
- 利润 = 营业收入 - 营业成本 - 期间费用
- 税负估算参考：
  增值税：小规模纳税人征收率 1%（估算），仅对收入估算
  个税（经营所得）：简化用"利润 × 5%"做参考，实际按累进税率/核定征收，仅供示意
"""
from datetime import datetime
from sqlalchemy import func
from extensions import db
from models.transaction import Transaction

# 支出分类 → 成本 or 费用
# 成本：直接构成销售货品的支出
COST_CATEGORIES = {'食材', '酒水饮料', '原材料', '烟酒', '农产品', '肉类', '蔬菜', '水产'}
# 费用：经营期间的其他开支
EXPENSE_CATEGORIES = {
    '房租', '水电燃气', '工资', '耗材餐具', '交通', '通讯', '网络', '广告',
    '包装', '设备', '维修', '保险', '税费', '其他', '日用杂货',
}


def _classify_expense(category: str) -> str:
    """把支出分类归为 'cost'(成本) 或 'expense'(费用)"""
    if not category:
        return 'expense'
    for c in COST_CATEGORIES:
        if c in category:
            return 'cost'
    return 'expense'


def _fmt(v):
    """保留两位小数，方便展示"""
    return round(float(v or 0), 2)


def _month_range(year, month):
    """返回某月的起止日期字符串"""
    start = f'{year}-{month:02d}-01'
    if month == 12:
        end = f'{year}-12-31'
    else:
        end = f'{year}-{month + 1:02d}-01'
        # 用下月1号减一天得到本月最后一天
        from datetime import date, timedelta
        end = str(date.fromisoformat(end) - timedelta(days=1))
    return start, end


def _default_range(kind='this-month'):
    """返回时间段。kind: this-month / last-month / all / (start,end 直接给)"""
    now = datetime.now()
    if kind == 'this-month':
        return _month_range(now.year, now.month)
    if kind == 'last-month':
        y, m = now.year, now.month - 1
        if m == 0:
            y, m = y - 1, 12
        return _month_range(y, m)
    # all：返回一个很宽的范围
    return '2000-01-01', '2100-12-31'


def generate_tax_draft(user_id, start_date=None, end_date=None, kind='this-month'):
    """生成报税底稿。

    Args:
        user_id: 用户ID
        start_date: 起始日期 YYYY-MM-DD（可选）
        end_date: 结束日期 YYYY-MM-DD（可选）
        kind: this-month / last-month / all（当没给 start/end 时用）

    Returns:
        底稿字典，含期间、汇总、明细归类、税负估算
    """
    if not start_date or not end_date:
        start_date, end_date = _default_range(kind)

    # 查询该时间段内的确认交易
    txns = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.status.in_(['confirmed', 'modified']),
        Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
        Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date(),
    ).all()

    # 汇总
    total_income = 0.0
    total_cost = 0.0
    total_expense = 0.0
    cost_by_category = {}
    expense_by_category = {}
    tx_count = 0

    for t in txns:
        tx_count += 1
        amount = float(t.amount or 0)
        if t.type == 'income':
            total_income += amount
        else:
            grp = _classify_expense(t.category)
            if grp == 'cost':
                total_cost += amount
                cost_by_category[t.category or '未分类'] = _fmt(cost_by_category.get(t.category or '未分类', 0) + amount)
            else:
                total_expense += amount
                expense_by_category[t.category or '未分类'] = _fmt(expense_by_category.get(t.category or '未分类', 0) + amount)

    total_profit = total_income - total_cost - total_expense

    # 税负估算（仅供示意）
    vat_est = round(total_income * 0.01, 2)          # 小规模纳税人增值税估算 1%
    income_tax_est = round(max(total_profit, 0) * 0.05, 2)  # 个税(经营所得)粗略参考 5%

    return {
        'period': {'start': start_date, 'end': end_date},
        'summary': {
            'total_income': _fmt(total_income),
            'total_cost': _fmt(total_cost),
            'total_expense': _fmt(total_expense),
            'total_profit': _fmt(total_profit),
            'tx_count': tx_count,
        },
        'cost_detail': sorted(cost_by_category.items(), key=lambda x: -x[1]),
        'expense_detail': sorted(expense_by_category.items(), key=lambda x: -x[1]),
        'tax_estimate': {
            'vat': _fmt(vat_est),
            'income_tax': _fmt(income_tax_est),
            'note': '以上税负为简化估算，仅作整理参考，请以最新税收政策及税务机关核定为准。',
        },
    }
```


## 📁 backend/prompts/

### 📄 backend/prompts/receipt_prompt.txt
```
你是一个专门帮饭店、吃食类店铺（夜宵摊、夫妻餐馆、早餐店、快餐店等）记账的AI文员。现在有一张老板拍的单据照片（可能是进货单、收据、微信转账截图、手写白条），你要提取下面的信息，按纯JSON格式返回，绝对不能有任何多余的解释、前言、后缀。

【要提取的字段】

1. 交易日期（transaction_date）：
   - 格式必须是 YYYY-MM-DD
   - 优先用单据上的日期
   - 单据上的日期可能是"5月3日""5/3""5-3"——统一转成"2026-05-03"格式
   - 如果没有年份信息，根据上下文推断最合理的年份（通常是当前年份）
   - 如果单据没有日期，就返回空字符串""，并在confidence_date中标为"low"
   - 如果日期是未来（比今天还晚），就把confidence_date标为"low"
   - 日期格式异常时confidence_date标为"low"

2. 金额（amount）：
   - 找单据上的总金额（最大数字、合计、小计、应付、实付等）
   - 必须是数字，保留最多两位小数
   - 手写数字要注意："7"可能像"1"、"8"可能像"6"、"0"可能像"9"——如果看不清就填最可能的数字，confidence_amount标为"low"
   - 如果金额是0或负数，填0，confidence_amount标为"low"
   - 金额前面有"¥""￥""$"等符号要去掉，只保留数字
   - 如果看不清金额，填0，confidence_amount标为"low"

3. 类型（type）：
   - 只能是"收入"或"支出"
   - 判断依据：
     * 有"进货""采购""买入""付""欠款""支出"字样 → 支出
     * 有"收入""收款""卖""营业额""流水"字样 → 收入
     * 单据是别人开给你的收据/发票 → 通常是支出（你付钱进货）
     * 微信/支付宝转账截图：付款方是你 → 支出，收款方是你 → 收入
   - 不确定时默认为"支出"

4. 分类（category）：只能从下面的分类里选一个，绝对不能自己造分类

   支出分类（10个）：
   - 食材：菜、肉、海鲜、蛋、豆制品、调味料（油盐酱醋、花椒辣椒等）、米面粮油、冻品（冻鸡翅、冻虾等）、干货（木耳、腐竹等）。几乎所有能吃的东西都归这里。如果金额超过500元是正常的大宗进货。
   - 酒水饮料：啤酒、白酒、红酒、瓶装水、汽水、椰汁、凉茶、果汁、奶茶原料等。注意：如果是做菜用的料酒、黄酒，归到"食材"。
   - 房租：店铺租金、摊位租金、物业管理费。
   - 工资：帮厨、服务员、洗碗工等员工的工资、薪水。
   - 水电燃气：水费、电费、煤气罐、炭火、液化气、天然气费用。
   - 耗材餐具：一次性餐盒、筷子、勺子、塑料袋、纸巾、竹签、锡纸、保鲜膜、洗洁精、打包袋、吸管等。
   - 设备维修：灶具维修、冰箱维修、设备购置、桌椅维修等。
   - 运输配送：进货运费、外卖平台配送费、跑腿费等。
   - 税费管理：工商管理费、卫生费、营业执照相关费用等。
   - 其他支出：不属于以上任何分类的支出。

   收入分类（2个）：
   - 营业收入：正常营业的营业收入（当天流水、营业额等）。
   - 其他收入：不属于营业收入的其他收入（押金退还、赔偿收入等）。

   分类置信度规则：
   - 如果能明确判断物品属于某个分类 → confidence_category为"high"
   - 如果物品可能属于多个分类，但选了最可能的一个 → confidence_category为"medium"
   - 如果完全无法判断，只能猜测 → confidence_category为"low"

5. 供应商（supplier）：
   - 单据上写的供应商名字、公司名、摊位号、或者"老张""李姐"之类的称呼
   - 如果看不清就填最可能的，confidence_supplier标为"low"
   - 如果没有供应商信息，返回空字符串""，confidence_supplier标为"low"
   - 微信/支付宝截图中的对方昵称/姓名也算供应商

6. 备注（notes）：
   - 单据上的其他重要信息，如：品名明细、数量、单价、折扣、付款方式等
   - 如果有多项商品，可以简要列出主要品名（用逗号分隔）
   - 没有重要补充信息就返回空字符串""

【置信度（confidence）规则汇总】
每个字段的置信度取值：
- "high"：信息清晰可辨，确信正确
- "medium"：信息基本可读，但有一定不确定性
- "low"：信息模糊、缺失、异常，或无法验证

具体场景：
- 手写单据比打印单据置信度低一级
- 图片模糊、有遮挡、有折痕导致看不清 → "low"
- 金额有涂改痕迹 → confidence_amount为"low"
- 日期部分缺失（只有月日没有年） → confidence_date为"medium"
- 供应商名字潦草难辨 → confidence_supplier为"low"

【返回格式（严格遵守，纯JSON，不要任何其他文字、不要用```包裹）】
{
  "transaction_date": "2026-08-02",
  "amount": 235.5,
  "type": "支出",
  "category": "食材",
  "supplier": "张三",
  "notes": "白菜50斤，土豆30斤",
  "confidence_date": "high",
  "confidence_amount": "high",
  "confidence_category": "high",
  "confidence_supplier": "medium"
}

注意：
- amount必须是数字类型（不要带引号），保留最多两位小数
- type只能是"收入"或"支出"
- category必须从上述12个分类中选一个
- 所有confidence_*字段只能是"high"/"medium"/"low"
- 如果图片完全无法识别（不是单据、太模糊、空白），返回所有字段为空/0，所有confidence为"low"
```


---

# 前端 (frontend)

### 📄 frontend/package.json
```
{
  "name": "ai-virtual-clerk-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vant/auto-import-resolver": "^1.3.0",
    "axios": "^1.7.0",
    "echarts": "^5.5.0",
    "pinia": "^2.2.0",
    "vant": "^4.9.0",
    "vue": "^3.5.0",
    "vue-router": "^4.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "@types/node": "^22.0.0",
    "postcss-px-to-viewport-8-plugin": "^1.2.5",
    "unplugin-auto-import": "^0.18.0",
    "unplugin-vue-components": "^0.27.0",
    "vite": "^5.4.0"
  }
}
```

### 📄 frontend/vite.config.js
```
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from '@vant/auto-import-resolver'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [VantResolver()],
    }),
    Components({
      resolvers: [VantResolver()],
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
```

### 📄 frontend/index.html
```
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>AI虚拟记账员</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

### 📄 frontend/postcss.config.cjs
```
// 说明：曾使用 postcss-px-to-viewport-8-plugin 做"手机端等比缩放"，
// 它把 1px 按 375 宽手机屏幕换算成 vw，导致在电脑浏览器上被放大数倍。
// 现已关闭，页面在电脑上按正常像素显示；手机端由各页面自身的响应式布局处理。
module.exports = {
  plugins: {},
}
```

### 📄 frontend/src/main.js
```
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Vant样式
import 'vant/lib/index.css'
// 全局主题（品牌色 + 组件覆盖）
import './styles/theme.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

### 📄 frontend/src/App.vue
```
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

// 登录页和工作台（/app）不显示底部导航栏
const showTabbar = computed(() => {
  return route.path !== '/login' && !route.path.startsWith('/app')
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
```


## 📁 frontend/src/views/

### 📄 frontend/src/views/Analytics.vue
```
<template>
  <div class="analytics-page">
    <van-nav-bar title="数据分析" />

    <div class="page-content">
      <!-- 日历视图 -->
      <CalendarView ref="calendarRef" @date-select="onCalendarDateSelect" />

      <!-- 时间维度切换 -->
      <div class="dimension-section">
        <van-tabs
          v-model:active="activeDimension"
          shrink
          @change="onDimensionChange"
        >
          <van-tab title="日" name="day" />
          <van-tab title="周" name="week" />
          <van-tab title="月" name="month" />
          <van-tab title="年" name="year" />
          <van-tab title="自定义" name="custom" />
        </van-tabs>
      </div>

      <div class="chart-type-section">
        <div class="btn-group">
          <van-button
            size="small"
            :type="chartType === 'bar' ? 'primary' : 'default'"
            @click="chartType = 'bar'"
          >柱状图</van-button>
          <van-button
            size="small"
            :type="chartType === 'line' ? 'primary' : 'default'"
            @click="chartType = 'line'"
          >折线图</van-button>
          <van-button
            size="small"
            :type="chartType === 'pie' ? 'primary' : 'default'"
            @click="chartType = 'pie'"
          >饼图</van-button>
          <van-button
            size="small"
            :type="chartType === 'table' ? 'primary' : 'default'"
            @click="chartType = 'table'"
          >表格</van-button>
        </div>
      </div>

      <!-- 图表面板 -->
      <ChartPanel
        ref="chartRef"
        :chart-type="chartType"
        :time-dimension="timeDimension"
        :date-range="dateRange"
      />

      <!-- 分析数据区 -->
      <div class="analysis-section">
        <!-- 数字卡片 -->
        <van-grid :column-num="3" :border="false" class="summary-grid">
          <van-grid-item>
            <div class="summary-card">
              <div class="summary-label">总收入</div>
              <div class="summary-value income">{{ formatAmount(summary.totalIncome) }}</div>
            </div>
          </van-grid-item>
          <van-grid-item>
            <div class="summary-card">
              <div class="summary-label">总支出</div>
              <div class="summary-value expense">{{ formatAmount(summary.totalExpense) }}</div>
            </div>
          </van-grid-item>
          <van-grid-item>
            <div class="summary-card">
              <div class="summary-label">总利润</div>
              <div :class="['summary-value', summary.totalProfit >= 0 ? 'income' : 'expense']">
                {{ formatAmount(summary.totalProfit) }}
              </div>
            </div>
          </van-grid-item>
        </van-grid>

        <!-- 同比/环比数据 -->
        <div class="comparison-section" v-if="comparison.yoy || comparison.mom">
          <div class="comparison-block" v-if="comparison.yoy">
            <div class="comparison-title">同比</div>
            <div class="comparison-items">
              <span class="comparison-item">
                收入 <span :class="getTrendClass(comparison.yoy.income)">
                  {{ formatPercent(comparison.yoy.income) }}
                </span>
              </span>
              <span class="comparison-item">
                支出 <span :class="getTrendClass(comparison.yoy.expense)">
                  {{ formatPercent(comparison.yoy.expense) }}
                </span>
              </span>
              <span class="comparison-item">
                利润 <span :class="getTrendClass(comparison.yoy.profit)">
                  {{ formatPercent(comparison.yoy.profit) }}
                </span>
              </span>
            </div>
          </div>

          <div class="comparison-block" v-if="comparison.mom">
            <div class="comparison-title">环比</div>
            <div class="comparison-items">
              <span class="comparison-item">
                收入 <span :class="getTrendClass(comparison.mom.income)">
                  {{ formatPercent(comparison.mom.income) }}
                </span>
              </span>
              <span class="comparison-item">
                支出 <span :class="getTrendClass(comparison.mom.expense)">
                  {{ formatPercent(comparison.mom.expense) }}
                </span>
              </span>
              <span class="comparison-item">
                利润 <span :class="getTrendClass(comparison.mom.profit)">
                  {{ formatPercent(comparison.mom.profit) }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 自定义日期范围弹窗 -->
    <van-calendar
      v-model:show="showDatePicker"
      type="range"
      :min-date="minDate"
      :max-date="maxDate"
      @confirm="onDateConfirm"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { getComparison } from '@/api/analytics'
import CalendarView from '@/components/CalendarView.vue'
import ChartPanel from '@/components/ChartPanel.vue'

const store = useAnalyticsStore()

// 状态
const calendarRef = ref(null)
const chartRef = ref(null)
const activeDimension = ref(1) // 默认"周"索引
const timeDimension = ref(store.timeDimension || 'week')
const chartType = ref(store.chartType || 'bar')
const dateRange = ref({ ...store.dateRange })
const showDatePicker = ref(false)

const minDate = new Date(2020, 0, 1)
const maxDate = new Date()

// 汇总数据
const summary = reactive({
  totalIncome: 0,
  totalExpense: 0,
  totalProfit: 0
})

// 同比/环比数据
const comparison = reactive({
  yoy: null,
  mom: null
})

// 维度名称映射
const dimensionMap = {
  0: 'day',
  1: 'week',
  2: 'month',
  3: 'year',
  4: 'custom'
}

// 金额格式化
function formatAmount(val) {
  if (val === undefined || val === null) return '¥0.00'
  const num = Number(val)
  return '¥' + num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 百分比格式化
function formatPercent(val) {
  if (val === undefined || val === null) return '--'
  const num = Number(val)
  const prefix = num >= 0 ? '+' : ''
  return prefix + num.toFixed(2) + '%'
}

// 获取趋势样式类
function getTrendClass(val) {
  if (val === undefined || val === null) return ''
  return Number(val) >= 0 ? 'trend-up' : 'trend-down'
}

// 维度切换
function onDimensionChange(index) {
  const dim = dimensionMap[index]
  if (dim === 'custom') {
    showDatePicker.value = true
  } else {
    timeDimension.value = dim
    store.timeDimension = dim
  }
}

// 日历日期选择
function onCalendarDateSelect(range) {
  dateRange.value = { start: range.start, end: range.end }
  store.dateRange = { ...dateRange.value }
}

// 自定义日期确认
function onDateConfirm(dates) {
  if (dates && dates.length === 2) {
    const fmt = (d) => {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    }
    dateRange.value = { start: fmt(dates[0]), end: fmt(dates[1]) }
    timeDimension.value = 'custom'
    store.timeDimension = 'custom'
    store.dateRange = { ...dateRange.value }
    showDatePicker.value = false
  }
}

// 获取对比数据
async function fetchComparison() {
  try {
    const params = { dimension: timeDimension.value }
    if (timeDimension.value === 'custom') {
      params.start_date = dateRange.value.start
      params.end_date = dateRange.value.end
    }
    const res = await getComparison(params)
    const data = res.data || res

    summary.totalIncome = data.total_income ?? data.totalIncome ?? 0
    summary.totalExpense = data.total_expense ?? data.totalExpense ?? 0
    summary.totalProfit = data.total_profit ?? data.totalProfit ?? 0
    comparison.yoy = data.yoy || data.year_over_year || null
    comparison.mom = data.mom || data.month_over_month || null
  } catch (e) {
    console.error('获取对比数据失败:', e)
  }
}

// 监听维度变化，重新获取对比数据
watch(
  () => [timeDimension.value, dateRange.value],
  () => {
    fetchComparison()
  },
  { deep: true }
)

onMounted(() => {
  fetchComparison()
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background-color: var(--bg);
}

.page-content {
  padding: 12px;
  padding-bottom: 80px;
}

/* 维度切换 */
.dimension-section {
  background: var(--card);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-1);
}

/* 图表类型切换 */
.chart-type-section {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.chart-type-section .btn-group {
  display: flex;
  width: 100%;
  gap: 0;
}

.chart-type-section .btn-group .van-button {
  flex: 1;
  font-size: 13px;
  border-radius: 0;
}

.chart-type-section .btn-group .van-button:first-child {
  border-radius: 4px 0 0 4px;
}

.chart-type-section .btn-group .van-button:last-child {
  border-radius: 0 4px 4px 0;
}

/* 分析数据区 */
.analysis-section {
  margin-top: 12px;
}

.summary-grid {
  background: var(--card);
  border-radius: var(--radius-sm);
  padding: 16px 0;
  box-shadow: var(--shadow-1);
}

.summary-card {
  text-align: center;
}

.summary-label {
  font-size: 13px;
  color: var(--ink-3);
  margin-bottom: 6px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
}

.summary-value.income {
  color: var(--up);
}

.summary-value.expense {
  color: var(--down);
}

/* 同比环比 */
.comparison-section {
  background: var(--card);
  border-radius: var(--radius-sm);
  padding: 16px;
  margin-top: 12px;
  box-shadow: var(--shadow-1);
}

.comparison-block {
  margin-bottom: 12px;
}

.comparison-block:last-child {
  margin-bottom: 0;
}

.comparison-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 8px;
}

.comparison-items {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.comparison-item {
  font-size: 13px;
  color: var(--ink-2);
}

.trend-up {
  color: var(--up);
  font-weight: 500;
}

.trend-down {
  color: var(--down);
  font-weight: 500;
}
</style>
```

### 📄 frontend/src/views/Bookkeeping.vue
```
<template>
  <div class="page-container">
    <van-nav-bar title="记账" />

    <van-tabs v-model:active="activeTab" sticky>
      <!-- Tab 1: 拍照记账 -->
      <van-tab title="拍照记账">
        <ReceiptUploader @refresh="loadTodayData" />
      </van-tab>

      <!-- Tab 2: 语音记账 -->
      <van-tab title="语音记账">
        <VoiceRecorder />
      </van-tab>

      <!-- Tab 3: 今日快览 -->
      <van-tab title="今日快览">
        <div class="today-list">
          <van-pull-refresh v-model="refreshing" @refresh="onPullRefresh">
            <van-empty v-if="!loading && transactions.length === 0" description="今日暂无记录" />
            <van-list
              v-else
              :loading="loading"
              :finished="finished"
              finished-text="没有更多了"
              @load="loadMore"
            >
              <van-cell
                v-for="item in transactions"
                :key="item.id"
                :title="item.category || '未分类'"
                :label="`${item.transaction_date} · ${item.supplier || '-'} · ${item.notes || ''}`"
                class="transaction-cell"
              >
                <template #value>
                  <span :class="item.type === 'income' ? 'amount-income' : 'amount-expense'">
                    {{ item.type === 'income' ? '+' : '-' }}¥{{ formatAmount(item.amount) }}
                  </span>
                </template>
              </van-cell>
            </van-list>
          </van-pull-refresh>
        </div>

        <!-- 底部汇总 -->
        <div class="summary-bar">
          <div class="summary-item">
            <span class="summary-label">收入</span>
            <span class="summary-value income">¥{{ formatAmount(summary.total_income) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">支出</span>
            <span class="summary-value expense">¥{{ formatAmount(summary.total_expense) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">净利润</span>
            <span class="summary-value" :class="summary.total_profit >= 0 ? 'income' : 'expense'">
              ¥{{ formatAmount(summary.total_profit) }}
            </span>
          </div>
        </div>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getTransactions, getTransactionSummary } from '@/api/transaction'
import { useBookkeepingStore } from '@/stores/bookkeeping'
import ReceiptUploader from '@/components/ReceiptUploader.vue'
import VoiceRecorder from '@/components/VoiceRecorder.vue'

const store = useBookkeepingStore()
const activeTab = ref(0)

// 今日快览数据
const transactions = ref([])
const summary = ref({ total_income: 0, total_expense: 0, total_profit: 0 })
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)

function getToday() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function loadTodayData() {
  page.value = 1
  transactions.value = []
  finished.value = false
  await loadMore()
  await loadSummary()
}

async function loadMore() {
  loading.value = true
  try {
    const today = getToday()
    const res = await getTransactions({
      start_date: today,
      end_date: today,
      page: page.value,
      per_page: 20
    })
    if (res.items && res.items.length > 0) {
      transactions.value.push(...res.items)
    }
    if (page.value >= res.pages) {
      finished.value = true
    } else {
      page.value++
    }
  } catch (e) {
    finished.value = true
  } finally {
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const today = getToday()
    const res = await getTransactionSummary({
      start_date: today,
      end_date: today
    })
    summary.value = {
      total_income: res.total_income || 0,
      total_expense: res.total_expense || 0,
      total_profit: res.total_profit || 0
    }
  } catch (e) {
    // ignore
  }
}

function onPullRefresh() {
  refreshing.value = false
  loadTodayData()
}

function formatAmount(val) {
  const num = parseFloat(val) || 0
  return num.toFixed(2)
}

// 切到今日快览tab时自动加载
watch(activeTab, (val) => {
  if (val === 2 && transactions.value.length === 0) {
    loadTodayData()
  }
})

onMounted(() => {
  // 如果初始就在今日快览tab则加载
  if (activeTab.value === 2) {
    loadTodayData()
  }
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--bg);
  padding-bottom: 50px; /* 底部tabbar空间 */
}

.today-list {
  min-height: 300px;
}

.transaction-cell :deep(.van-cell__value) {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.amount-income {
  color: var(--up);
  font-size: 16px;
  font-weight: bold;
}

.amount-expense {
  color: var(--down);
  font-size: 16px;
  font-weight: bold;
}

.summary-bar {
  position: fixed;
  bottom: 50px; /* tabbar高度 */
  left: 0;
  right: 0;
  display: flex;
  background: var(--card);
  padding: 12px 16px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.summary-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: var(--ink-3);
}

.summary-value {
  font-size: 16px;
  font-weight: bold;
}

.summary-value.income {
  color: var(--up);
}

.summary-value.expense {
  color: var(--down);
}
</style>
```

### 📄 frontend/src/views/ChatView.vue
```
<template>
  <div class="chat-view">
    <!-- 顶部标题栏 -->
    <header class="chat-header">
      <div class="chat-title">
        <van-icon :name="currentConfig?.icon || 'chat-o'" size="18" color="var(--brand)" />
        <span>{{ currentConfig?.label || 'AI对话' }}</span>
      </div>
      <van-button size="mini" plain icon="replay" @click="clearChat">清空对话</van-button>
    </header>

    <!-- 一键操作区：当前功能的预设按钮，点一下直接执行 -->
    <div v-if="actionBtns.length > 0" class="quick-bar">
      <div class="quick-bar-title">一键操作</div>
      <div class="quick-btns">
        <van-button
          v-for="act in actionBtns"
          :key="act.label"
          size="small"
          :type="act.type || 'default'"
          round
          class="quick-btn"
          :loading="actionLoading === act.label"
          @click="onActionClick(act)"
        >
          {{ act.label }}
        </van-button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div ref="msgListRef" class="msg-list">
      <template v-for="msg in messages" :key="msg.id">
        <!-- 用户消息 -->
        <div v-if="msg.role === 'user'" class="msg-row user">
          <div class="bubble user-bubble">
            <template v-if="msg.type === 'text'">{{ msg.content }}</template>
            <template v-else-if="msg.type === 'image'">
              <div class="user-image-wrap">
                <img :src="msg.content" class="user-image" alt="上传图片" />
                <span class="image-label">已上传图片，AI识别中...</span>
              </div>
            </template>
          </div>
        </div>

        <!-- AI消息 -->
        <div v-else class="msg-row ai">
          <div class="ai-avatar">
            <van-icon name="smile-o" size="16" color="#fff" />
          </div>
          <div class="bubble ai-bubble">
            <!-- 文本 -->
            <template v-if="msg.type === 'text'">{{ msg.content }}</template>

            <!-- 核验卡片（记账） -->
            <template v-else-if="msg.type === 'bookkeeping-card'">
              <BookkeepingCard
                :data="msg.payload"
                :low-confidence-fields="msg.lowFields"
                @confirm="onBookkeepingConfirm"
              />
            </template>

            <!-- 查账结果列表 -->
            <template v-else-if="msg.type === 'transaction-list'">
              <div class="tx-list">
                <div class="tx-list-summary" v-if="msg.summary">
                  共 {{ msg.summary.total }} 笔 · 收入 ¥{{ fmt(msg.summary.income) }} · 支出 ¥{{ fmt(msg.summary.expense) }}
                </div>
                <div v-for="tx in msg.items" :key="tx.id" class="tx-item">
                  <div class="tx-main">
                    <span class="tx-date">{{ tx.transaction_date }}</span>
                    <span class="tx-cat">{{ tx.category || '未分类' }}</span>
                    <span class="tx-supplier">{{ tx.supplier || '-' }}</span>
                  </div>
                  <span class="tx-amount" :class="tx.type">
                    {{ tx.type === 'income' ? '+' : '-' }}¥{{ fmt(tx.amount) }}
                  </span>
                </div>
              </div>
            </template>

            <!-- 报表汇总卡片 -->
            <template v-else-if="msg.type === 'summary-card'">
              <div class="sum-card">
                <div class="sum-card-title">{{ msg.periodLabel }}收支汇总</div>
                <div class="sum-grid">
                  <div class="sum-cell">
                    <span class="sum-label">收入</span>
                    <span class="sum-value up">¥{{ fmt(msg.income) }}</span>
                  </div>
                  <div class="sum-cell">
                    <span class="sum-label">支出</span>
                    <span class="sum-value down">¥{{ fmt(msg.expense) }}</span>
                  </div>
                  <div class="sum-cell">
                    <span class="sum-label">利润</span>
                    <span class="sum-value" :class="msg.profit >= 0 ? 'up' : 'down'">¥{{ fmt(msg.profit) }}</span>
                  </div>
                </div>
              </div>
            </template>

            <!-- 报税底稿卡片 -->
            <template v-else-if="msg.type === 'tax-draft-card'">
              <div class="draft-card">
                <div class="draft-head">
                  <span>报税底稿</span>
                  <span class="draft-period">{{ msg.periodLabel }} · {{ msg.period.start }} ~ {{ msg.period.end }}</span>
                </div>
                <div class="draft-rows">
                  <div class="draft-row">
                    <span>营业收入</span><span class="draft-val">¥{{ fmt(msg.summary.total_income) }}</span>
                  </div>
                  <div class="draft-row">
                    <span>营业成本</span><span class="draft-val">¥{{ fmt(msg.summary.total_cost) }}</span>
                  </div>
                  <div class="draft-row">
                    <span>期间费用</span><span class="draft-val">¥{{ fmt(msg.summary.total_expense) }}</span>
                  </div>
                  <div class="draft-row profit">
                    <span>利润</span><span class="draft-val">¥{{ fmt(msg.summary.total_profit) }}</span>
                  </div>
                </div>

                <div v-if="msg.costDetail.length > 0" class="draft-block">
                  <div class="draft-block-title">成本构成</div>
                  <div v-for="(item, i) in msg.costDetail" :key="i" class="draft-block-row">
                    <span>{{ item[0] }}</span><span>¥{{ fmt(item[1]) }}</span>
                  </div>
                </div>

                <div v-if="msg.expenseDetail.length > 0" class="draft-block">
                  <div class="draft-block-title">费用构成</div>
                  <div v-for="(item, i) in msg.expenseDetail" :key="i" class="draft-block-row">
                    <span>{{ item[0] }}</span><span>¥{{ fmt(item[1]) }}</span>
                  </div>
                </div>

                <div class="draft-tax">
                  <div class="draft-tax-title">税负估算参考</div>
                  <div class="draft-block-row">
                    <span>增值税（约1%）</span><span>¥{{ fmt(msg.taxEstimate.vat) }}</span>
                  </div>
                  <div class="draft-block-row">
                    <span>经营所得个税（约5%）</span><span>¥{{ fmt(msg.taxEstimate.income_tax) }}</span>
                  </div>
                  <div class="draft-tax-note">{{ msg.taxEstimate.note }}</div>
                </div>
              </div>
            </template>

            <!-- 报税日期提醒 -->
            <template v-else-if="msg.type === 'tax-reminder-card'">
              <div class="remind-card">
                <div class="remind-head">
                  <van-icon name="alarm-clock-o" size="16" color="var(--brand)" />
                  <span>报税日期提醒</span>
                </div>
                <div v-for="(item, i) in msg.items" :key="i" class="remind-item">
                  <span class="remind-date">{{ item.date }}</span>
                  <span class="remind-label">{{ item.label }}</span>
                </div>
                <div class="remind-note">以税务机关通知为准，请提前准备账目。</div>
              </div>
            </template>

            <!-- 消息内快速按钮 -->
            <div v-if="msg.actions && msg.actions.length > 0" class="msg-actions">
              <van-button
                v-for="act in msg.actions"
                :key="act.label"
                size="small"
                :type="act.type || 'default'"
                round
                @click="act.handler"
              >{{ act.label }}</van-button>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="msg-empty">
        <van-icon name="chat-o" size="48" color="#c8c9cc" />
        <p>请从左侧选择一个功能开始</p>
      </div>
    </div>

    <!-- 统一输入区 -->
    <footer class="chat-input-area">
      <div class="chat-input-row">
        <!-- 图片上传 -->
        <van-uploader
          :after-read="onImageRead"
          accept="image/*"
          :max-count="1"
          :show-upload="!uploading"
          class="input-uploader"
        >
          <van-icon name="photograph" size="24" color="var(--brand)" />
        </van-uploader>

        <!-- 语音 -->
        <van-icon name="audio" size="24" color="var(--brand)" @click="onVoiceClick" />

        <!-- 文字输入 -->
        <van-field
          v-model="inputText"
          placeholder="输入您的记账内容或问题..."
          class="input-field"
          @keyup.enter="onSendText"
        />

        <!-- 发送 -->
        <van-button
          type="primary"
          size="small"
          round
          :disabled="!inputText.trim() && !uploading"
          :loading="uploading"
          @click="onSendText"
        >发送</van-button>
      </div>
      <div class="chat-input-hint">
        <span>也可以直接点上方按钮，一键完成常用操作</span>
      </div>
    </footer>

    <!-- 隐藏文件选择器：供"上传小票识别"按钮使用 -->
    <input
      ref="hiddenFileInput"
      type="file"
      accept="image/*"
      class="hidden-file-input"
      @change="onHiddenFileChange"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showToast } from 'vant'
import { useChatStore } from '@/stores/chat'
import { recognizeReceipt, getTaxDraft } from '@/api/ai'
import { getTransactions, getTransactionSummary, createTransaction, exportTransactions } from '@/api/transaction'
import BookkeepingCard from '@/components/chat/BookkeepingCard.vue'

const route = useRoute()
const chatStore = useChatStore()

const featureId = computed(() => route.params.feature || 'ai-bookkeeping')
const currentConfig = computed(() => chatStore.getFeatureConfig(featureId.value))

const messages = ref([])
const inputText = ref('')
const uploading = ref(false)
const msgListRef = ref(null)
const hiddenFileInput = ref(null)

// 正在执行中的按钮（显示 loading）
const actionLoading = ref('')

// 当前功能的一键操作按钮
const actionBtns = computed(() => currentConfig.value?.actions || [])

// 当前功能配置（用于聊天流程）
const isBookkeeping = computed(() => featureId.value === 'ai-bookkeeping')
const isInquiry = computed(() => featureId.value === 'inquiry')

// 记账流程状态
const bookkeepingStep = ref('idle') // idle / waiting-input / recognizing / awaiting-confirm

// ── 消息管理 ──
async function initChat() {
  messages.value = chatStore.ensureSession(featureId.value)
  await scrollToBottom()
}

function pushUserText(text) {
  chatStore.addMessage(featureId.value, { role: 'user', type: 'text', content: text })
  syncMessages()
}

function pushUserImage(dataUrl) {
  chatStore.addMessage(featureId.value, { role: 'user', type: 'image', content: dataUrl })
  syncMessages()
}

function pushAiText(text, extra = {}) {
  chatStore.addMessage(featureId.value, { role: 'assistant', type: 'text', content: text, ...extra })
  syncMessages()
}

function syncMessages() {
  messages.value = chatStore.sessions[featureId.value] || []
  scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
}

// ── 时间段解析：根据文字判断查账/报表范围 ──
function resolvePeriod(text) {
  const today = new Date()
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  const todayStr = fmt(today)
  const thisMonthStart = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`

  if (text.includes('上个')) {
    const d = new Date()
    d.setDate(1)
    d.setDate(d.getDate() - 1)
    const end = fmt(d)
    const start = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
    return { start, end, label: '上月' }
  }
  if (text.includes('7天')) {
    const d = new Date()
    d.setDate(d.getDate() - 7)
    return { start: fmt(d), end: todayStr, label: '最近7天' }
  }
  if (text.includes('今年') || text.includes('全年')) {
    return { start: `${today.getFullYear()}-01-01`, end: todayStr, label: '今年' }
  }
  return { start: thisMonthStart, end: todayStr, label: '本月' }
}

// ── 一键按钮分发：所有预设按钮的执行入口 ──
async function onActionClick(act) {
  if (actionLoading.value) return
  actionLoading.value = act.label

  try {
    switch (act.command) {
      case 'bookkeeping-upload':
        handleUploadButton()
        break
      case 'quick-text':
        handleQuickText(act.text)
        break
      case 'export-excel':
        await handleExportExcel(act.period)
        break
      case 'tax-draft':
        await handleTaxDraft(act.lastMonth)
        break
      case 'tax-reminder':
        handleTaxReminder(!!act.quarter)
        break
      case 'customers-list':
      case 'customers-add':
        handleCustomers(act.command)
        break
      default:
        showToast('该功能正在完善中')
    }
  } finally {
    actionLoading.value = ''
  }
}

// 上传小票：触发表单里隐藏的文件选择器
function handleUploadButton() {
  if (!isBookkeeping.value) {
    // 不在记账页，先提示
    showToast('请先在左侧选择「AI识别记账」')
    return
  }
  hiddenFileInput.value?.click()
}

async function onHiddenFileChange(e) {
  const file = e.target.files?.[0]
  e.target.value = '' // 允许重复选择同一文件
  if (!file) return
  // 生成 dataURL 用于预览
  const dataUrl = await readFileAsDataURL(file)
  await processImage({ content: dataUrl, file })
}

function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// 快捷文字：按当前功能路由到对应流程
async function handleQuickText(text) {
  pushUserText(text)
  if (isBookkeeping.value) {
    bookkeepingStep.value = 'waiting-input'
    pushAiText('好的，请直接告诉我这笔账的金额和内容，比如「买菜花了235元」或「今天卖了1800元」。')
    return
  }
  // 查账 / 报表 / 收支明细
  if (text.includes('报表')) {
    await handleReport(text)
  } else {
    await handleInquiry(text)
  }
}

// ── 发送文字 ──
async function onSendText() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  pushUserText(text)

  // 记账流程：把文字当作记账信息处理
  if (isBookkeeping.value && bookkeepingStep.value === 'waiting-input') {
    await handleTextBookkeeping(text)
    return
  }

  // 查账流程：文字就是查询条件
  if (isInquiry.value) {
    await handleInquiry(text)
    return
  }

  // 报表流程
  if (featureId.value === 'report') {
    await handleReport(text)
    return
  }

  // 收支明细：当查账处理
  if (featureId.value === 'ledger-detail') {
    await handleInquiry(text)
    return
  }

  // 其他功能：通用回复
  pushAiText('好的，收到。这个功能正在完善中，很快就能为您服务。')
}

// ── 图片上传（记账） ──
async function onImageRead(file) {
  if (!isBookkeeping.value) {
    showToast('当前功能暂不支持图片，请到"AI识别记账"使用')
    return
  }
  if (bookkeepingStep.value === 'awaiting-confirm') {
    showToast('请先确认上一笔账目，或点击"重新记账"')
    return
  }
  await processImage(file)
}

async function processImage(file) {
  // 显示用户上传的图片
  pushUserImage(file.content)
  bookkeepingStep.value = 'recognizing'
  uploading.value = true

  try {
    const result = await recognizeReceipt(file.file)
    // 识别成功 → 生成核验卡片
    bookkeepingStep.value = 'awaiting-confirm'
    pushAiText('识别完成，请核对以下信息：')
    buildBookkeepingCard(result)
  } catch (e) {
    bookkeepingStep.value = 'waiting-input'
    pushAiText('识别失败了，您可以重新拍一张更清晰的图片，或者直接用文字告诉我。比如："昨天买菜花了235元"。')
  } finally {
    uploading.value = false
  }
}

// ── 文字记账 ──
async function handleTextBookkeeping(text) {
  pushAiText('好的，我记下来了。请确认以下信息是否准确：')
  // 简化：从文字里粗提取（日期默认今天，类型默认支出）
  const today = new Date()
  const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  const amountMatch = text.match(/(\d+(\.\d+)?)/)
  const amount = amountMatch ? parseFloat(amountMatch[1]) : 0
  const isIncome = text.includes('收') || text.includes('卖') || text.includes('赚')
  const type = isIncome ? 'income' : 'expense'

  buildBookkeepingCard({
    transaction_date: dateStr,
    amount,
    type,
    category: '',
    supplier: '',
    notes: text,
    confidence: { date: 'medium', amount: 'medium', category: 'low', supplier: 'low' },
    match_status: 'needs_check',
  }, ['category'])
  bookkeepingStep.value = 'awaiting-confirm'
}

// ── 构建核验卡片 ──
function buildBookkeepingCard(result, forceLow = []) {
  const confidence = result.confidence || {}
  const lowFields = []
  const fieldConfidence = {
    date: confidence.date,
    amount: confidence.amount,
    category: confidence.category,
    supplier: confidence.supplier,
  }
  // 找出低可信字段
  for (const [field, level] of Object.entries(fieldConfidence)) {
    if (level === 'low' || level === 'medium' || forceLow.includes(field)) {
      lowFields.push({
        field,
        label: fieldLabel(field),
        value: result[fieldValueKey(field)] || '',
        level,
      })
    }
  }

  chatStore.addMessage(featureId.value, {
    role: 'assistant',
    type: 'bookkeeping-card',
    payload: {
      transaction_date: result.transaction_date,
      amount: result.amount,
      type: result.type === '收入' || result.type === 'income' ? 'income' : 'expense',
      category: result.category,
      supplier: result.supplier,
      notes: result.notes,
    },
    lowFields,
  })
  syncMessages()
}

function fieldLabel(field) {
  return { date: '交易日期', amount: '金额', category: '分类', supplier: '供应商' }[field] || field
}

function fieldValueKey(field) {
  return { date: 'transaction_date', amount: 'amount', category: 'category', supplier: 'supplier' }[field] || field
}

// ── 查账流程 ──
async function handleInquiry(text) {
  const { start, end, label } = resolvePeriod(text)
  try {
    const res = await getTransactions({ start_date: start, end_date: end, per_page: 50 })
    const summaryRes = await getTransactionSummary({ start_date: start, end_date: end })
    const items = res.items || []
    if (items.length === 0) {
      pushAiText(`${label}（${start} ~ ${end}）没有查到收支记录。`)
      return
    }
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'transaction-list',
      items,
      summary: {
        total: res.total,
        income: summaryRes.total_income,
        expense: summaryRes.total_expense,
      },
    })
    syncMessages()
  } catch (e) {
    pushAiText('查询失败了，请稍后再试。')
  }
}

// ── 报表流程：显示汇总卡片 ──
async function handleReport(text) {
  const { start, end, label } = resolvePeriod(text)
  try {
    const summaryRes = await getTransactionSummary({ start_date: start, end_date: end })
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'summary-card',
      periodLabel: label,
      period: { start, end },
      income: summaryRes.total_income || 0,
      expense: summaryRes.total_expense || 0,
      profit: summaryRes.total_profit || 0,
    })
    syncMessages()
  } catch (e) {
    pushAiText('生成报表失败了，请稍后再试。')
  }
}

// ── 导出 Excel ──
async function handleExportExcel(period) {
  const today = new Date()
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  let start, end, label

  if (period === 'last-month') {
    const d = new Date()
    d.setDate(1)
    d.setDate(d.getDate() - 1)
    start = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
    end = fmt(d)
    label = '上月'
  } else if (period === 'all') {
    start = ''
    end = ''
    label = '全部'
  } else {
    start = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`
    end = fmt(today)
    label = '本月'
  }

  try {
    const blob = await exportTransactions({ start_date: start, end_date: end })
    const filename = `账目导出_${label}_${today.getFullYear()}${String(today.getMonth() + 1).padStart(2, '0')}${String(today.getDate()).padStart(2, '0')}.xlsx`
    downloadBlob(blob, filename)
    pushAiText(`已导出 ${label} 账目 Excel，请查看浏览器下载。`)
  } catch (e) {
    pushAiText('导出失败，请稍后再试。')
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// ── 报税底稿：一键生成 ──
async function handleTaxDraft(lastMonth) {
  pushAiText(lastMonth ? '好的，正在生成本月报税底稿...' : '好的，正在生成本月报税底稿...')
  try {
    const draft = await getTaxDraft({ kind: lastMonth ? 'last-month' : 'this-month' })
    chatStore.addMessage(featureId.value, {
      role: 'assistant',
      type: 'tax-draft-card',
      periodLabel: lastMonth ? '上月' : '本月',
      period: draft.period,
      summary: draft.summary,
      costDetail: draft.cost_detail,
      expenseDetail: draft.expense_detail,
      taxEstimate: draft.tax_estimate,
    })
    syncMessages()
  } catch (e) {
    pushAiText('生成报税底稿失败了，请稍后再试。')
  }
}

// ── 报税日期提醒 ──
function handleTaxReminder(quarter) {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth() + 1

  const month15 = `${y}-${String(m).padStart(2, '0')}-15`
  const monthNext15 = `${y}-${String(m % 12 + 1).padStart(2, '0')}-15`

  // 季度截止：1/4/7/10 月的 15 号
  const quarterMap = [
    { label: '第一季度申报', month: 1 },
    { label: '第二季度申报', month: 4 },
    { label: '第三季度申报', month: 7 },
    { label: '第四季度申报', month: 10 },
  ]

  let items
  if (quarter) {
    items = quarterMap.map(q => ({
      date: `${y}-${String(q.month).padStart(2, '0')}-15`,
      label: `${q.label}（小规模纳税人增值税/个税）`,
    }))
  } else {
    items = [
      { date: month15, label: '本月增值税/经营所得个税申报截止' },
      { date: monthNext15, label: '下月申报截止（可提前准备）' },
      { date: `${y}-03-31`, label: '上年度经营所得个税汇算清缴截止' },
    ]
  }

  chatStore.addMessage(featureId.value, {
    role: 'assistant',
    type: 'tax-reminder-card',
    items,
  })
  syncMessages()
}

// ── 客户台账（后端未接，友好提示） ──
function handleCustomers(command) {
  if (command === 'customers-add') {
    pushAiText('新增客户功能正在开发中。以后您可以直接在这里录入客户信息，建立客户台账。')
  } else {
    pushAiText('客户列表正在开发中。以后这里会显示您所有客户的往来账。')
  }
}

// ── 核验卡片确认 ──
async function onBookkeepingConfirm(data) {
  try {
    await createTransaction(data)
    bookkeepingStep.value = 'idle'
    pushAiText('✅ 已入账：' + (data.type === 'income' ? '收入' : '支出') + ' ¥' + fmt(data.amount) +
      (data.category ? '，分类：' + data.category : '') + '。还需要记其他账吗？')
    pushAiText('您可以继续上传小票、打字，或者点击"重新记账"。', {
      actions: [{ label: '重新记账', type: 'primary', handler: resetBookkeeping }],
    })
  } catch (e) {
    pushAiText('入库失败了，请重试。')
  }
}

function resetBookkeeping() {
  bookkeepingStep.value = 'waiting-input'
  pushAiText('好的，我们重新开始记账。您可以直接打字，也可以上传小票图片。')
}

// ── 语音（预留） ──
function onVoiceClick() {
  if (!isBookkeeping.value) {
    showToast('语音记账请在"AI识别记账"中使用')
    return
  }
  showToast('语音记账正在完善中，您也可以直接打字。')
}

// ── 清空对话 ──
function clearChat() {
  chatStore.clearSession(featureId.value)
  initChat()
  bookkeepingStep.value = 'waiting-input'
}

// 金额格式化
function fmt(val) {
  const n = parseFloat(val || 0)
  return n.toFixed(2)
}

// 切换功能时
watch(featureId, () => {
  initChat()
  bookkeepingStep.value = isBookkeeping.value ? 'waiting-input' : 'idle'
})

onMounted(() => {
  initChat()
  bookkeepingStep.value = isBookkeeping.value ? 'waiting-input' : 'idle'
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
  min-width: 0;
  background: var(--bg);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: var(--card);
  border-bottom: 1px solid var(--line);
  flex-shrink: 0;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--ink);
}

/* ── 一键操作区 ── */
.quick-bar {
  background: var(--card);
  border-bottom: 1px solid var(--line);
  padding: 10px 20px;
  flex-shrink: 0;
}

.quick-bar-title {
  font-size: 11px;
  color: var(--ink-3);
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  min-width: 96px;
}

/* ── 消息列表 ── */
.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.msg-row.user {
  justify-content: flex-end;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--brand-strong));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.bubble {
  max-width: 78%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.ai-bubble {
  background: var(--card);
  border: 1px solid var(--line);
  border-top-left-radius: 4px;
  box-shadow: var(--shadow-1);
}

.user-bubble {
  background: var(--brand);
  color: #fff;
  border-top-right-radius: 4px;
}

.msg-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

/* 用户上传图片 */
.user-image-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.user-image {
  max-width: 200px;
  max-height: 180px;
  border-radius: 8px;
  object-fit: cover;
}

.image-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
}

/* 查账结果 */
.tx-list {
  display: flex;
  flex-direction: column;
}

.tx-list-summary {
  font-size: 13px;
  color: var(--brand);
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 8px;
}

.tx-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.tx-item:last-child { border-bottom: none; }

.tx-main {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 13px;
}

.tx-date { color: var(--ink-2); }
.tx-cat {
  background: var(--brand-soft);
  color: var(--brand);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 12px;
}
.tx-supplier { color: var(--ink-3); font-size: 12px; }

.tx-amount { font-size: 14px; font-weight: 600; }
.tx-amount.income { color: var(--up); }
.tx-amount.expense { color: var(--down); }

/* 报表汇总卡片 */
.sum-card {
  min-width: 240px;
}

.sum-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 10px;
}

.sum-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.sum-cell {
  background: var(--brand-tint);
  border-radius: 8px;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.sum-label {
  font-size: 11px;
  color: var(--ink-3);
}

.sum-value {
  font-size: 16px;
  font-weight: 700;
}
.sum-value.up { color: var(--up); }
.sum-value.down { color: var(--down); }

/* 报税底稿卡片 */
.draft-card {
  min-width: 300px;
}

.draft-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  padding-bottom: 10px;
  border-bottom: 2px solid var(--brand);
  margin-bottom: 12px;
}

.draft-period {
  font-size: 11px;
  font-weight: 400;
  color: var(--ink-3);
}

.draft-rows {
  margin-bottom: 8px;
}

.draft-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13.5px;
  color: var(--ink-2);
}

.draft-row.profit {
  font-weight: 700;
  color: var(--ink);
  border-top: 1px dashed var(--line);
  margin-top: 4px;
  padding-top: 10px;
}

.draft-val {
  font-variant-numeric: tabular-nums;
}

.draft-row.profit .draft-val { color: var(--brand); }

.draft-block {
  background: var(--brand-tint);
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 8px;
}

.draft-block-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--brand);
  margin-bottom: 6px;
}

.draft-block-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--ink-2);
  padding: 3px 0;
}

.draft-tax {
  background: #FFF8EC;
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 8px;
}

.draft-tax-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--warn);
  margin-bottom: 6px;
}

.draft-tax-note {
  font-size: 11px;
  color: var(--ink-3);
  margin-top: 6px;
  line-height: 1.5;
}

/* 报税提醒卡片 */
.remind-card {
  min-width: 240px;
}

.remind-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 10px;
}

.remind-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-bottom: 1px dashed var(--line);
}

.remind-item:last-child { border-bottom: none; }

.remind-date {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand);
  white-space: nowrap;
}

.remind-label {
  font-size: 12.5px;
  color: var(--ink-2);
}

.remind-note {
  font-size: 11px;
  color: var(--ink-3);
  margin-top: 8px;
}

/* 空状态 */
.msg-empty {
  text-align: center;
  padding: 60px 0;
  color: #c8c9cc;
}

.msg-empty p { font-size: 13px; margin-top: 12px; }

/* 输入区 */
.chat-input-area {
  background: var(--card);
  border-top: 1px solid var(--line);
  padding: 10px 16px 12px;
  flex-shrink: 0;
}

.chat-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-uploader {
  flex-shrink: 0;
}

.input-field {
  flex: 1;
  background: var(--bg);
  border-radius: 20px;
  padding: 0 14px;
}

.chat-input-hint {
  text-align: center;
  font-size: 11px;
  color: var(--ink-3);
  margin-top: 6px;
}

.hidden-file-input {
  display: none;
}
</style>
```

### 📄 frontend/src/views/Ledger.vue
```
<template>
  <div class="ledger-page">
    <van-nav-bar title="台账" />

    <!-- 筛选区 -->
    <div class="filter-bar">
      <!-- 日期范围 -->
      <van-button
        size="small"
        plain
        icon="calendar-o"
        class="date-btn"
        @click="showCalendar = true"
      >
        {{ dateBtnText }}
      </van-button>

      <!-- 分类筛选 -->
      <van-dropdown-menu class="filter-dropdown" active-color="var(--brand)">
        <van-dropdown-item v-model="filterCategory" :options="categoryOptions" />
        <van-dropdown-item v-model="filterType" :options="typeOptions" />
      </van-dropdown-menu>

      <!-- 查询按钮 -->
      <van-button type="primary" size="small" @click="handleQuery">查询</van-button>
    </div>

    <!-- 数据列表 -->
    <div class="list-container">
      <TransactionList
        ref="listRef"
        :start-date="appliedStartDate"
        :end-date="appliedEndDate"
        :category="appliedCategory"
        :type="appliedType"
        @edit="openEdit"
        @voucher="openVoucher"
        @total-change="onTotalChange"
      />
    </div>

    <!-- 底部汇总栏 -->
    <div class="summary-bar">
      <div class="summary-data">
        <span class="summary-item income">
          收入 <strong>¥{{ formatAmount(summary.total_income) }}</strong>
        </span>
        <span class="summary-item expense">
          支出 <strong>¥{{ formatAmount(summary.total_expense) }}</strong>
        </span>
        <span class="summary-item profit">
          利润 <strong>¥{{ formatAmount(summary.total_profit) }}</strong>
        </span>
      </div>
      <ExportButton
        :start-date="appliedStartDate"
        :end-date="appliedEndDate"
        :category="appliedCategory"
        :type="appliedType"
        :total-count="totalCount"
      />
    </div>

    <!-- 日历弹窗 -->
    <van-calendar
      v-model:show="showCalendar"
      type="range"
      :max-date="maxDate"
      @confirm="onCalendarConfirm"
    />

    <!-- 修改弹窗 -->
    <EditTransaction
      v-model:show="showEdit"
      :transaction="currentTransaction"
      @refresh="handleRefresh"
    />

    <!-- 凭证弹窗 -->
    <VoucherPanel
      v-model:show="showVoucher"
      :transaction="currentTransaction"
      @uploaded="handleRefresh"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TransactionList from '@/components/TransactionList.vue'
import EditTransaction from '@/components/EditTransaction.vue'
import ExportButton from '@/components/ExportButton.vue'
import VoucherPanel from '@/components/VoucherPanel.vue'
import { getTransactionSummary } from '@/api/transaction'

// ─── 筛选条件 ───
const filterStartDate = ref('')
const filterEndDate = ref('')
const filterCategory = ref('')
const filterType = ref('')

// 已应用的筛选条件（点"查询"后生效）
const appliedStartDate = ref('')
const appliedEndDate = ref('')
const appliedCategory = ref('')
const appliedType = ref('')

const showCalendar = ref(false)
const maxDate = new Date()

// ─── 数据 ───
const listRef = ref(null)
const totalCount = ref(0)
const currentTransaction = ref(null)
const showEdit = ref(false)
const showVoucher = ref(false)

const summary = ref({
  total_income: 0,
  total_expense: 0,
  total_profit: 0,
  count: 0,
})

// ─── 选项 ───
const categoryOptions = [
  { text: '全部分类', value: '' },
  { text: '餐饮', value: '餐饮' },
  { text: '交通', value: '交通' },
  { text: '购物', value: '购物' },
  { text: '娱乐', value: '娱乐' },
  { text: '医疗', value: '医疗' },
  { text: '教育', value: '教育' },
  { text: '住房', value: '住房' },
  { text: '通讯', value: '通讯' },
  { text: '工资', value: '工资' },
  { text: '奖金', value: '奖金' },
  { text: '投资收益', value: '投资收益' },
  { text: '其他', value: '其他' },
]

const typeOptions = [
  { text: '全部', value: '' },
  { text: '收入', value: 'income' },
  { text: '支出', value: 'expense' },
]

// ─── 计算属性 ───
const dateBtnText = computed(() => {
  if (filterStartDate.value && filterEndDate.value) {
    return `${filterStartDate.value} ~ ${filterEndDate.value}`
  }
  return '选择日期范围'
})

// ─── 方法 ───
function formatAmount(val) {
  return parseFloat(val || 0).toFixed(2)
}

/** 日历确认 */
function onCalendarConfirm([start, end]) {
  filterStartDate.value = formatDate(start)
  filterEndDate.value = formatDate(end)
  showCalendar.value = false
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/** 查询 */
function handleQuery() {
  appliedStartDate.value = filterStartDate.value
  appliedEndDate.value = filterEndDate.value
  appliedCategory.value = filterCategory.value
  appliedType.value = filterType.value
  fetchSummary()
}

/** 获取汇总数据 */
async function fetchSummary() {
  try {
    const params = {}
    if (appliedStartDate.value) params.start_date = appliedStartDate.value
    if (appliedEndDate.value) params.end_date = appliedEndDate.value
    const res = await getTransactionSummary(params)
    summary.value = res
  } catch {
    // 错误由拦截器处理
  }
}

/** 列表总数变化 */
function onTotalChange(count) {
  totalCount.value = count
}

/** 打开编辑弹窗 */
function openEdit(item) {
  currentTransaction.value = { ...item }
  showEdit.value = true
}

/** 打开凭证弹窗 */
function openVoucher(item) {
  currentTransaction.value = { ...item }
  showVoucher.value = true
}

/** 编辑保存后刷新 */
function handleRefresh() {
  if (listRef.value) {
    listRef.value.reload()
  }
  fetchSummary()
}

/** 初始加载 */
onMounted(() => {
  fetchSummary()
})
</script>

<style scoped>
.ledger-page {
  min-height: 100vh;
  background-color: var(--bg);
  padding-bottom: 120px; /* tabbar + summary-bar */
}

/* ── 筛选栏 ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--card);
  border-bottom: 1px solid var(--line);
}

.date-btn {
  flex-shrink: 0;
  font-size: 12px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.filter-dropdown {
  flex: 1;
  min-width: 0;
}

/* ── 列表区 ── */
.list-container {
  min-height: 300px;
}

/* ── 底部汇总栏 ── */
.summary-bar {
  position: fixed;
  bottom: 50px; /* tabbar高度 */
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--card);
  border-top: 1px solid var(--line);
  z-index: 100;
}

.summary-data {
  display: flex;
  gap: 16px;
  flex: 1;
}

.summary-item {
  font-size: 12px;
  color: var(--ink-2);
}

.summary-item strong {
  display: block;
  font-size: 14px;
  margin-top: 2px;
}

.summary-item.income strong {
  color: var(--up);
}

.summary-item.expense strong {
  color: var(--down);
}

.summary-item.profit strong {
  color: var(--brand);
}
</style>
```

### 📄 frontend/src/views/Login.vue
```
<template>
  <div class="login-page">
    <!-- 左：品牌区（桌面展示，手机端收成紧凑头部） -->
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-top">
          <div class="seal-logo">账</div>
          <span class="brand-wordmark">AI虚拟文员</span>
        </div>

        <h1 class="brand-headline">开店的每一笔，<br>都记得清清楚楚。</h1>
        <p class="brand-sub">AI 记账 · 自动归类 · 报税提醒<br />把散乱的小票，变成一本整整齐齐的账。</p>

        <div class="brand-feats">
          <span class="feat-pill">小票拍照即记</span>
          <span class="feat-pill">收支自动归类</span>
          <span class="feat-pill">报税日期提醒</span>
        </div>

        <div class="brand-stamp">专业账本 · 报税好帮手</div>
      </div>
    </div>

    <!-- 右：登录/注册表单区 -->
    <div class="form-panel">
      <div class="form-card">
        <div class="card-head">
          <h2 class="card-title">{{ activeTab === 0 ? '欢迎回来' : '创建账号' }}</h2>
          <p class="card-sub">{{ activeTab === 0 ? '用手机号登录您的账本' : '注册后即可开始免费体验' }}</p>
        </div>

        <van-tabs v-model:active="activeTab" class="login-tabs" :line-width="26" title-active-color="#123F33">
          <van-tab title="登录">
            <van-form @submit="onLogin" class="login-form">
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
                placeholder="设置密码"
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
                placeholder="再输一次密码"
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
                placeholder="您的店属于哪种？"
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

        <!-- 演示账号提示 -->
        <div v-if="activeTab === 0" class="demo-hint" @click="fillDemo">
          <van-icon name="smile-o" size="15" />
          <span>演示账号：13812345678 / 123456</span>
          <span class="demo-fill">点此填入</span>
        </div>
      </div>

      <div class="footer-tip">前 5 次免费体验，无需付费即可使用</div>
      <div class="version-tag">工作台版 v0.2</div>
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

// 演示账号一键填入
function fillDemo() {
  loginForm.phone = '13812345678'
  loginForm.password = '123456'
  showToast('已填入演示账号，点登录即可')
}

// 登录
async function onLogin() {
  loading.value = true
  try {
    await userStore.login(loginForm.phone, loginForm.password)
    await userStore.fetchUserInfo()
    router.push('/app')
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
    router.push('/app')
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
  /* 设计令牌（商务风） */
  --ink: #1F2421;
  --green-deep: #123F33;
  --green: #227B5B;
  --green-soft: #EAF3EF;
  --bg-soft: #F6F8F7;
  --line: #E6EAE7;
  --warn: #C9932E;

  display: flex;
  min-height: 100vh;
  background: var(--bg-soft);
  color: var(--ink);
}

/* ───────────── 左：品牌区 ───────────── */
.brand-panel {
  flex: 1.15;
  background: linear-gradient(150deg, #0D2E26 0%, #123F33 55%, #1B5E46 100%);
  color: #F4F8F6;
  display: flex;
  position: relative;
  overflow: hidden;
}

/* 细腻光斑，代替原来的账本横格 */
.brand-panel::before {
  content: '';
  position: absolute;
  top: -120px;
  right: -80px;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.07) 0%, transparent 70%);
  pointer-events: none;
}

.brand-panel::after {
  content: '';
  position: absolute;
  left: -100px;
  bottom: -140px;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.brand-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 9vh 8% 48px;
  max-width: 560px;
  margin: 0 auto;
  width: 100%;
}

.brand-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 72px;
}

/* Logo：深绿圆角方块，白"账"字 */
.seal-logo {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: #fff;
  color: var(--green-deep);
  font-family: "Songti SC", "STSong", "SimSun", serif;
  font-size: 23px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.brand-wordmark {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 2px;
}

.brand-headline {
  font-size: 38px;
  font-weight: 700;
  line-height: 1.4;
  margin: 0 0 20px;
  letter-spacing: 1px;
}

.brand-sub {
  font-size: 15px;
  line-height: 1.9;
  color: rgba(244, 248, 246, 0.82);
  margin: 0;
}

.brand-feats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 44px;
}

.feat-pill {
  font-size: 12.5px;
  color: #F4F8F6;
  border: 1px solid rgba(244, 248, 246, 0.3);
  border-radius: 999px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(2px);
}

.brand-stamp {
  margin-top: auto;
  padding-top: 48px;
  font-size: 12px;
  letter-spacing: 3px;
  color: rgba(244, 248, 246, 0.5);
}

/* ───────────── 右：表单区 ───────────── */
.form-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: var(--bg-soft);
}

.form-card {
  width: min(410px, 100%);
  background: #fff;
  border-radius: 16px;
  padding: 34px 32px 24px;
  box-shadow: 0 20px 48px rgba(18, 63, 51, 0.1), 0 2px 8px rgba(18, 63, 51, 0.05);
  border: 1px solid var(--line);
  animation: card-in 0.5s ease both;
}

.card-head {
  margin-bottom: 6px;
}

.card-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 6px;
  letter-spacing: 1px;
}

.card-sub {
  font-size: 13.5px;
  color: var(--ink-3, #8A938D);
  margin: 0 0 14px;
}

/* Tabs */
.login-tabs :deep(.van-tabs__nav) {
  background: transparent;
  margin-bottom: 8px;
}

.login-tabs :deep(.van-tab) {
  font-size: 16px;
  color: #7A807B;
}

.login-tabs :deep(.van-tab--active) {
  color: var(--green-deep);
  font-weight: 600;
}

.login-tabs :deep(.van-tabs__line) {
  background: var(--green);
  height: 3px;
  border-radius: 3px;
}

/* 表单 */
.login-form :deep(.van-cell-group--inset) {
  margin: 0;
  background: transparent;
  border-radius: 0;
}

.login-form :deep(.van-cell) {
  background: transparent;
}

.login-form :deep(.van-field) {
  background: transparent;
  padding: 17px 2px;
  border-bottom: 1px solid var(--line);
  transition: border-color 0.2s;
}

.login-form :deep(.van-field:focus-within) {
  border-bottom-color: var(--green);
}

.login-form :deep(.van-field__left-icon) {
  color: var(--green-deep);
  margin-right: 10px;
}

.login-form :deep(.van-field__control) {
  font-size: 15.5px;
}

.login-form :deep(.van-field__control::placeholder) {
  color: #B6BBB4;
}

/* 按钮 */
.form-footer {
  padding: 26px 0 4px;
}

.submit-btn {
  height: 50px;
  border-radius: 10px;
  background: var(--green-deep) !important;
  border: none !important;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  box-shadow: 0 8px 20px rgba(18, 63, 51, 0.25);
}

.submit-btn:active {
  background: var(--green) !important;
  transform: translateY(1px);
}

/* 演示账号提示 */
.demo-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 18px;
  padding: 11px 14px;
  background: var(--green-soft);
  border: 1px dashed rgba(18, 63, 51, 0.4);
  border-radius: 10px;
  font-size: 12.5px;
  color: var(--green-deep);
  cursor: pointer;
  transition: background 0.2s;
}

.demo-hint:active {
  background: #DFEFE7;
}

.demo-fill {
  margin-left: auto;
  color: var(--green);
  font-weight: 600;
}

/* 底部 */
.footer-tip {
  margin-top: 28px;
  font-size: 13px;
  color: #8A938D;
}

.version-tag {
  margin-top: 10px;
  font-size: 12px;
  color: var(--green);
  letter-spacing: 1px;
}

@keyframes card-in {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ───────────── 手机端：上下堆叠 ───────────── */
@media (max-width: 820px) {
  .login-page {
    flex-direction: column;
  }

  .brand-panel {
    flex: none;
  }

  .brand-inner {
    padding: 40px 24px 28px;
  }

  .brand-top {
    margin-bottom: 32px;
  }

  .brand-headline {
    font-size: 28px;
  }

  .brand-feats {
    margin-top: 22px;
    display: none;
  }

  .brand-stamp {
    display: none;
  }

  .form-panel {
    padding: 28px 18px 40px;
  }

  .form-card {
    padding: 26px 24px 20px;
  }
}

/* 尊重减少动效设置 */
@media (prefers-reduced-motion: reduce) {
  .form-card {
    animation: none;
  }
}
</style>
```

### 📄 frontend/src/views/Pricing.vue
```
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
```

### 📄 frontend/src/views/Profile.vue
```
<template>
  <div class="page-container">
    <van-nav-bar title="个人中心" />
    <div class="page-content">
      <!-- 套餐信息区 -->
      <div class="section subscription-section">
        <div class="subscription-info">
          <p class="subscription-label">您当前是：</p>
          <p v-if="!userStore.userInfo && !fetchFailed" class="subscription-name">加载中...</p>
          <p v-else-if="!userStore.userInfo && fetchFailed" class="subscription-name">数据加载失败，请刷新重试</p>
          <template v-else>
            <p
              class="subscription-name"
              :class="{ 'text-danger': isExpired || userStore.isExpiringSoon }"
            >
              {{ displaySubscription }}
            </p>
            <p v-if="userStore.userInfo?.subscription_expiry" class="expiry-date">
              到期日：{{ formatDate(userStore.userInfo.subscription_expiry) }}
            </p>
            <p v-if="isExpired" class="expiry-warning">
              您的套餐已过期，请续费
            </p>
            <p v-else-if="userStore.isExpiringSoon" class="expiry-warning">
              您的套餐还有{{ userStore.daysUntilExpiry }}天到期，请尽快续费
            </p>
          </template>
        </div>
        <div class="subscription-actions">
          <van-button type="primary" size="small" @click="goRenew">续费</van-button>
          <van-button plain size="small" @click="onEndService">结束服务</van-button>
        </div>
      </div>

      <!-- 推荐码区 -->
      <div class="section">
        <van-cell-group inset>
          <van-cell title="推荐码" :value="referralCode">
            <template #right-icon>
              <van-button size="mini" type="primary" plain @click="copyReferralCode">
                复制
              </van-button>
            </template>
          </van-cell>
          <van-cell title="已邀请" :value="(referralData?.invited_count ?? 0) + '人'" />
          <van-cell title="优惠券" :value="coupons.length + '张'" />
        </van-cell-group>
      </div>

      <!-- 裂变记录 -->
      <div class="section">
        <van-cell-group inset title="裂变记录">
          <template v-if="referralRecords.length > 0">
            <van-cell
              v-for="(record, index) in referralRecords"
              :key="index"
              :title="maskPhone(record.phone)"
              :label="formatDate(record.date)"
              :value="record.status"
            />
          </template>
          <van-empty v-else description="暂无裂变记录" image="search" />
        </van-cell-group>
      </div>

      <!-- 优惠券列表 -->
      <div class="section">
        <van-cell-group inset title="我的优惠券">
          <template v-if="coupons.length > 0">
            <van-cell
              v-for="(coupon, index) in coupons"
              :key="index"
              :title="'¥' + formatMoney(coupon.amount)"
              :label="coupon.source + ' ' + formatDate(coupon.expire_date)"
              :value="couponStatusText(coupon.status)"
              :value-class="'coupon-status-' + coupon.status"
            />
          </template>
          <van-empty v-else description="暂无优惠券" image="coupon" />
        </van-cell-group>
      </div>

      <!-- 退出登录 -->
      <div class="section logout-section">
        <van-button type="danger" plain block @click="onLogout">退出登录</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import { useUserStore } from '@/stores/user'
import { getReferralInfo } from '@/api/referral'

const router = useRouter()
const userStore = useUserStore()
const fetchFailed = ref(false)

// 推荐/裂变数据
const referralData = ref(null)
const referralRecords = ref([])
const coupons = ref([])

// 推荐码
const referralCode = computed(() => {
  return userStore.userInfo?.referral_code || '暂无'
})

// 是否已过期
const isExpired = computed(() => {
  if (!userStore.userInfo?.subscription_expiry) return false
  return userStore.daysUntilExpiry !== null && userStore.daysUntilExpiry <= 0
})

// 显示订阅文本
const displaySubscription = computed(() => {
  if (!userStore.userInfo) return ''
  const plan = userStore.userInfo.subscription_plan
  if (!plan || plan === 'free') {
    const remaining = userStore.userInfo.remaining_free_uses
    return remaining != null ? `免费体验（剩余${remaining}次）` : '免费体验'
  }
  return userStore.subscriptionText
})

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 金额千分位
function formatMoney(amount) {
  if (amount == null) return '0'
  return Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 手机号脱敏
function maskPhone(phone) {
  if (!phone || phone.length < 7) return phone
  return phone.slice(0, 3) + '****' + phone.slice(-4)
}

// 优惠券状态文本
function couponStatusText(status) {
  const map = { unused: '未使用', used: '已使用', expired: '已过期' }
  return map[status] || status
}

// 复制推荐码
async function copyReferralCode() {
  const code = userStore.userInfo?.referral_code
  if (!code) {
    showToast('暂无推荐码')
    return
  }
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(code)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = code
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    showToast('已复制')
  } catch {
    showToast('复制失败，请手动复制')
  }
}

// 续费
function goRenew() {
  router.push('/pricing')
}

// 结束服务
function onEndService() {
  showDialog({
    title: '结束服务',
    message: '结束服务后数据保留90天，之后会自动删除所有数据，确定要结束吗？',
    confirmButtonText: '确定结束',
    cancelButtonText: '再想想',
    showCancelButton: true,
  }).then(() => {
    showToast('功能开发中')
  }).catch(() => {})
}

// 退出登录
function onLogout() {
  showDialog({
    title: '退出登录',
    message: '确定要退出登录吗？',
    showCancelButton: true,
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {})
}

// 加载推荐/裂变数据
async function loadReferralData() {
  try {
    const res = await getReferralInfo()
    referralData.value = res
    referralRecords.value = res?.records || []
    coupons.value = res?.coupons || []
  } catch {
    // API不存在时静默处理
    referralRecords.value = []
    coupons.value = []
  }
}

onMounted(async () => {
  if (!userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
      if (!userStore.userInfo) fetchFailed.value = true
    } catch {
      fetchFailed.value = true
    }
  }
  loadReferralData()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--bg);
}
.page-content {
  padding-bottom: 80px;
}
.section {
  margin: 12px 0;
}
.subscription-section {
  background: linear-gradient(135deg, var(--brand) 0%, var(--brand-strong) 100%);
  padding: 22px 20px;
  margin: 0;
}
.subscription-info {
  margin-bottom: 14px;
}
.subscription-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 6px;
}
.subscription-name {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 6px;
}
.subscription-name.text-danger {
  color: #FFD2C8;
}
.expiry-date {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2px;
}
.expiry-warning {
  font-size: 13px;
  color: #FFD2C8;
  margin-top: 4px;
  font-weight: 500;
}
.subscription-actions {
  display: flex;
  gap: 12px;
}
.logout-section {
  padding: 16px;
}
:deep(.coupon-status-unused) {
  color: var(--up);
}
:deep(.coupon-status-used) {
  color: var(--ink-3);
}
:deep(.coupon-status-expired) {
  color: var(--down);
}
</style>
```

### 📄 frontend/src/views/Workbench.vue
```
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

// 当前激活的功能项
const currentFeature = computed(() => route.params.feature || 'ai-bookkeeping')

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

// 点击功能项 → 跳转到对应会话
function selectFeature(featureId) {
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
```


## 📁 frontend/src/components/

### 📄 frontend/src/components/CalendarView.vue
```
<template>
  <div class="calendar-view">
    <van-calendar
      type="range"
      :show-confirm="false"
      :poppable="false"
      :default-date="defaultDate"
      @select="onDateSelect"
    >
      <template #day-content="{ date }">
        <div class="day-cell">
          <span class="day-number">{{ date.getDate() }}</span>
          <div v-if="getDayData(date)" class="day-data">
            <span class="income">{{ formatMini(getDayData(date).income) }}</span>
            <span class="expense">{{ formatMini(getDayData(date).expense) }}</span>
          </div>
        </div>
      </template>
    </van-calendar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDailyData } from '@/api/analytics'

const emit = defineEmits(['date-select'])

const defaultDate = ref(new Date())
const dailyMap = ref({})

// 格式化迷你金额（日历格子内用）
function formatMini(val) {
  if (val === undefined || val === null) return '--'
  const num = Number(val)
  if (Math.abs(num) >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (Math.abs(num) >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toFixed(0)
}

// 根据日期获取当天数据
function getDayData(date) {
  const key = formatDateKey(date)
  return dailyMap.value[key] || null
}

// 日期格式化为 YYYY-MM-DD
function formatDateKey(date) {
  if (!date) return ''
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// 获取当月及前后月的日历数据
async function fetchMonthData(date) {
  try {
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    // 获取当月第一天和最后一天
    const startDate = new Date(year, month - 1, 1)
    const endDate = new Date(year, month, 0)
    const start = formatDateKey(startDate)
    const end = formatDateKey(endDate)

    const res = await getDailyData({ start_date: start, end_date: end })
    const map = {}
    if (res && Array.isArray(res.data)) {
      res.data.forEach(item => {
        map[item.date] = item
      })
    } else if (res && typeof res === 'object' && !Array.isArray(res)) {
      // 兼容直接返回map格式
      Object.assign(map, res.data || res)
    }
    dailyMap.value = map
  } catch (e) {
    console.error('获取日历数据失败:', e)
    dailyMap.value = {}
  }
}

function onDateSelect(dates) {
  if (dates && dates.length === 2) {
    emit('date-select', {
      start: formatDateKey(dates[0]),
      end: formatDateKey(dates[1])
    })
  }
}

onMounted(() => {
  fetchMonthData(new Date())
})

// 暴露刷新方法
defineExpose({
  refresh: () => fetchMonthData(new Date())
})
</script>

<style scoped>
.calendar-view {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}

.day-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  padding: 2px 0;
}

.day-number {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.day-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  margin-top: 2px;
}

.day-data .income {
  font-size: 9px;
  color: #07c160;
  line-height: 1.2;
}

.day-data .expense {
  font-size: 9px;
  color: #ee0a24;
  line-height: 1.2;
}

:deep(.van-calendar__day) {
  height: 56px;
}
</style>
```

### 📄 frontend/src/components/ChartPanel.vue
```
<template>
  <div class="chart-panel">
    <!-- 表格视图 -->
    <div v-if="chartType === 'table'" class="table-view">
      <van-cell-group inset v-if="tableData.length > 0">
        <van-cell
          v-for="item in tableData"
          :key="item.date"
          :title="item.date"
        >
          <template #label>
            <div class="table-row">
              <span class="income-text">收入: {{ formatAmount(item.income) }}</span>
              <span class="expense-text">支出: {{ formatAmount(item.expense) }}</span>
              <span :class="['profit-text', item.profit >= 0 ? 'positive' : 'negative']">
                利润: {{ formatAmount(item.profit) }}
              </span>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
      <van-empty v-else description="暂无数据" />
    </div>

    <!-- ECharts图表视图 -->
    <div v-else ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { getTrendData, getCategoryRatio } from '@/api/analytics'

// ECharts 按需引入
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart, LineChart, PieChart,
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent, DatasetComponent, CanvasRenderer
])

const props = defineProps({
  chartType: {
    type: String,
    default: 'bar',
    validator: (v) => ['bar', 'line', 'pie', 'table'].includes(v)
  },
  timeDimension: {
    type: String,
    default: 'week'
  },
  dateRange: {
    type: Object,
    default: () => ({ start: null, end: null })
  }
})

const chartRef = ref(null)
let chartInstance = null
const tableData = ref([])

// 金额格式化：千分位 + 2位小数
function formatAmount(val) {
  if (val === undefined || val === null) return '¥0.00'
  const num = Number(val)
  return '¥' + num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 构建请求参数
function buildParams() {
  const params = { dimension: props.timeDimension }
  if (props.timeDimension === 'custom' && props.dateRange.start && props.dateRange.end) {
    params.start_date = props.dateRange.start
    params.end_date = props.dateRange.end
  }
  return params
}

// 获取趋势数据
async function fetchTrendData() {
  try {
    const res = await getTrendData(buildParams())
    return res.data || res || []
  } catch (e) {
    console.error('获取趋势数据失败:', e)
    return []
  }
}

// 获取分类占比数据
async function fetchCategoryRatio() {
  try {
    const res = await getCategoryRatio(buildParams())
    return res.data || res || []
  } catch (e) {
    console.error('获取分类占比失败:', e)
    return []
  }
}

// 渲染柱状图
function renderBarChart(data) {
  if (!chartInstance) return
  const dates = data.map(d => d.date)
  const profits = data.map(d => Number(d.profit || 0))

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/>利润: ${formatAmount(p.value)}`
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 10 ? 45 : 0,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val) => {
          if (Math.abs(val) >= 10000) return (val / 10000).toFixed(1) + 'w'
          if (Math.abs(val) >= 1000) return (val / 1000).toFixed(1) + 'k'
          return val
        }
      }
    },
    series: [{
      type: 'bar',
      data: profits.map(v => ({
        value: v,
        itemStyle: {
          color: v >= 0 ? '#07c160' : '#ee0a24'
        }
      })),
      barMaxWidth: 30
    }]
  }, true)
}

// 渲染折线图
function renderLineChart(data) {
  if (!chartInstance) return
  const dates = data.map(d => d.date)
  const profits = data.map(d => Number(d.profit || 0))

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/>利润: ${formatAmount(p.value)}`
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 10 ? 45 : 0,
        fontSize: 11
      },
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val) => {
          if (Math.abs(val) >= 10000) return (val / 10000).toFixed(1) + 'w'
          if (Math.abs(val) >= 1000) return (val / 1000).toFixed(1) + 'k'
          return val
        }
      }
    },
    series: [{
      type: 'line',
      data: profits,
      smooth: true,
      lineStyle: { color: '#1989fa', width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(25,137,250,0.3)' },
          { offset: 1, color: 'rgba(25,137,250,0.05)' }
        ])
      },
      itemStyle: { color: '#1989fa' }
    }]
  }, true)
}

// 渲染饼图
function renderPieChart(data) {
  if (!chartInstance) return
  const pieData = data.map(d => ({
    name: d.category_name || d.name || d.category,
    value: Number(d.amount || d.value || 0)
  }))

  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        return `${params.name}<br/>${formatAmount(params.value)} (${params.percent}%)`
      }
    },
    legend: {
      orient: 'horizontal',
      bottom: '0%',
      type: 'scroll',
      textStyle: { fontSize: 11 }
    },
    series: [{
      type: 'pie',
      radius: ['35%', '60%'],
      center: ['50%', '45%'],
      data: pieData,
      label: {
        formatter: '{b}\n{d}%',
        fontSize: 11
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      }
    }]
  }, true)
}

// 加载并渲染表格数据
async function loadTableData() {
  const data = await fetchTrendData()
  tableData.value = Array.isArray(data) ? data : []
}

// 更新图表
async function updateChart() {
  if (props.chartType === 'table') {
    await loadTableData()
    return
  }

  await nextTick()
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  chartInstance.clear()

  if (props.chartType === 'pie') {
    const data = await fetchCategoryRatio()
    renderPieChart(Array.isArray(data) ? data : [])
  } else {
    const data = await fetchTrendData()
    const arr = Array.isArray(data) ? data : []
    if (props.chartType === 'bar') {
      renderBarChart(arr)
    } else if (props.chartType === 'line') {
      renderLineChart(arr)
    }
  }
}

// resize处理
function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(
  () => [props.chartType, props.timeDimension, props.dateRange],
  () => {
    updateChart()
  },
  { deep: true }
)

onMounted(() => {
  updateChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 暴露刷新方法
defineExpose({ refresh: updateChart })
</script>

<style scoped>
.chart-panel {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.table-view {
  max-height: 300px;
  overflow-y: auto;
}

.table-row {
  display: flex;
  gap: 12px;
  font-size: 12px;
  margin-top: 4px;
}

.income-text {
  color: #07c160;
}

.expense-text {
  color: #ee0a24;
}

.profit-text.positive {
  color: #07c160;
}

.profit-text.negative {
  color: #ee0a24;
}
</style>
```

### 📄 frontend/src/components/ConfirmDialog.vue
```
<template>
  <van-dialog
    v-model:show="visible"
    title="确认入库"
    :show-cancel-button="false"
    :show-confirm-button="false"
    :close-on-click-overlay="false"
  >
    <div class="confirm-content">
      <div class="field-list">
        <div class="field-item">
          <span class="field-label">交易日期</span>
          <span class="field-value">{{ formData.transaction_date || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">金额</span>
          <span class="field-value amount">¥{{ formData.amount || '0' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">类型</span>
          <span class="field-value" :class="formData.type === 'income' ? 'text-green' : 'text-red'">
            {{ formData.type === 'income' ? '收入' : '支出' }}
          </span>
        </div>
        <div class="field-item">
          <span class="field-label">分类</span>
          <span class="field-value">{{ formData.category || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">供应商</span>
          <span class="field-value">{{ formData.supplier || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-label">备注</span>
          <span class="field-value">{{ formData.notes || '-' }}</span>
        </div>
      </div>
      <div class="warning-text">确认后无法撤销，请逐条核对</div>
    </div>
    <div class="dialog-actions">
      <van-button plain block class="action-btn" @click="onCancel">返回修改</van-button>
      <van-button type="primary" block class="action-btn" :loading="submitting" @click="onConfirm">
        我已核对，确认入账
      </van-button>
    </div>
  </van-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { createTransaction } from '@/api/transaction'

const props = defineProps({
  formData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:show', 'success'])

const visible = ref(false)
const submitting = ref(false)

function open() {
  visible.value = true
}

function close() {
  visible.value = false
  emit('update:show', false)
}

function onCancel() {
  close()
}

async function onConfirm() {
  submitting.value = true
  try {
    await createTransaction(props.formData)
    showToast('入库成功')
    close()
    emit('success')
  } catch (e) {
    // 错误已在axios拦截器中统一处理
  } finally {
    submitting.value = false
  }
}

defineExpose({ open, close })
</script>

<style scoped>
.confirm-content {
  padding: 16px 20px;
}

.field-list {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 12px 16px;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebedf0;
}

.field-item:last-child {
  border-bottom: none;
}

.field-label {
  font-size: 14px;
  color: #969799;
  flex-shrink: 0;
}

.field-value {
  font-size: 14px;
  color: #323233;
  text-align: right;
  word-break: break-all;
}

.field-value.amount {
  font-size: 18px;
  font-weight: bold;
}

.text-green {
  color: #07c160;
}

.text-red {
  color: #ee0a24;
}

.warning-text {
  color: #ee0a24;
  font-size: 12px;
  text-align: center;
  margin-top: 12px;
}

.dialog-actions {
  display: flex;
  gap: 8px;
  padding: 0 20px 16px;
}

.action-btn {
  flex: 1;
}
</style>
```

### 📄 frontend/src/components/EditTransaction.vue
```
<template>
  <van-popup
    v-model:show="visible"
    position="bottom"
    round
    :style="{ maxHeight: '85vh' }"
    @close="handleClose"
  >
    <div class="edit-transaction">
      <!-- 警告条 -->
      <div v-if="!editMode" class="warning-bar">
        <van-icon name="warning-o" size="18" color="#ee0a24" />
        <span class="warning-text">正在修改已入账的历史数据，此操作影响统计结果，确定要修改吗？</span>
      </div>

      <!-- 确认修改按钮（未进入编辑模式时显示） -->
      <div v-if="!editMode" class="confirm-action">
        <van-button type="danger" block round @click="editMode = true">
          确定修改
        </van-button>
      </div>

      <!-- 编辑表单 -->
      <div v-if="editMode" class="edit-form">
        <div class="form-header">
          <span>修改交易记录</span>
          <van-icon name="cross" @click="handleClose" />
        </div>

        <!-- 交易日期 -->
        <van-field
          v-model="form.transaction_date"
          is-link
          readonly
          label="交易日期"
          placeholder="请选择日期"
          @click="showDatePicker = true"
        />

        <!-- 金额 -->
        <van-field
          v-model="form.amount"
          label="金额"
          type="number"
          placeholder="请输入金额"
        />

        <!-- 类型 -->
        <van-field name="type" label="类型">
          <template #input>
            <van-radio-group v-model="form.type" direction="horizontal">
              <van-radio name="income">收入</van-radio>
              <van-radio name="expense">支出</van-radio>
            </van-radio-group>
          </template>
        </van-field>

        <!-- 分类 -->
        <van-field
          v-model="form.category"
          is-link
          readonly
          label="分类"
          placeholder="请选择分类"
          @click="showCategoryPicker = true"
        />

        <!-- 供应商 -->
        <van-field
          v-model="form.supplier"
          label="供应商"
          placeholder="请输入供应商名称"
        />

        <!-- 备注 -->
        <van-field
          v-model="form.notes"
          label="备注"
          type="textarea"
          rows="2"
          placeholder="请输入备注（选填）"
          autosize
        />

        <!-- 底部按钮 -->
        <div class="form-actions">
          <van-button plain round @click="handleClose">取消</van-button>
          <van-button type="primary" round :loading="saving" loading-text="保存中..." @click="handleSave">
            保存修改
          </van-button>
        </div>
      </div>

      <!-- 日期选择器 -->
      <van-popup v-model:show="showDatePicker" position="bottom" round>
        <van-date-picker
          v-model="datePickerValue"
          title="选择交易日期"
          :min-date="minDate"
          :max-date="maxDate"
          @confirm="onDateConfirm"
          @cancel="showDatePicker = false"
        />
      </van-popup>

      <!-- 分类选择器 -->
      <van-popup v-model:show="showCategoryPicker" position="bottom" round>
        <van-picker
          :columns="categoryColumns"
          @confirm="onCategoryConfirm"
          @cancel="showCategoryPicker = false"
        />
      </van-popup>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { showToast } from 'vant'
import { updateTransaction } from '@/api/transaction'

const props = defineProps({
  show: { type: Boolean, default: false },
  transaction: { type: Object, default: null },
})

const emit = defineEmits(['update:show', 'refresh'])

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val),
})

const editMode = ref(false)
const saving = ref(false)
const showDatePicker = ref(false)
const showCategoryPicker = ref(false)

const form = ref({
  transaction_date: '',
  amount: '',
  type: 'expense',
  category: '',
  supplier: '',
  notes: '',
})

// 日期选择器值（数组格式 ['2026','08','02']）
const datePickerValue = ref([])
const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

// 分类选项
const categoryColumns = [
  '餐饮', '交通', '购物', '娱乐', '医疗', '教育',
  '住房', '通讯', '工资', '奖金', '投资收益', '其他',
]

/** 当弹窗打开且有交易数据时，初始化表单 */
watch(
  () => props.show,
  (val) => {
    if (val && props.transaction) {
      editMode.value = false
      const t = props.transaction
      form.value = {
        transaction_date: t.transaction_date || '',
        amount: String(t.amount || ''),
        type: t.type || 'expense',
        category: t.category || '',
        supplier: t.supplier || '',
        notes: t.notes || '',
      }
      // 初始化日期选择器
      if (t.transaction_date) {
        const parts = t.transaction_date.split('-')
        datePickerValue.value = parts
      } else {
        const now = new Date()
        datePickerValue.value = [
          String(now.getFullYear()),
          String(now.getMonth() + 1).padStart(2, '0'),
          String(now.getDate()).padStart(2, '0'),
        ]
      }
    }
  }
)

/** 日期确认 */
function onDateConfirm({ selectedValues }) {
  form.value.transaction_date = selectedValues.join('-')
  showDatePicker.value = false
}

/** 分类确认 */
function onCategoryConfirm({ selectedValues }) {
  form.value.category = selectedValues[0] || ''
  showCategoryPicker.value = false
}

/** 保存修改 */
async function handleSave() {
  if (!form.value.transaction_date) {
    showToast('请选择交易日期')
    return
  }
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    showToast('请输入有效金额')
    return
  }

  saving.value = true
  try {
    await updateTransaction(props.transaction.id, {
      transaction_date: form.value.transaction_date,
      amount: parseFloat(form.value.amount),
      type: form.value.type,
      category: form.value.category,
      supplier: form.value.supplier,
      notes: form.value.notes,
    })
    showToast({ message: '修改成功', type: 'success' })
    visible.value = false
    emit('refresh')
  } catch (error) {
    // 错误已由api拦截器处理
  } finally {
    saving.value = false
  }
}

/** 关闭弹窗 */
function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.edit-transaction {
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.warning-bar {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fff8f0;
  border: 1px solid #ffdfdf;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.warning-text {
  font-size: 13px;
  color: #ee0a24;
  line-height: 1.5;
}

.confirm-action {
  padding: 16px 0;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f5f5f5;
}

.form-header .van-icon {
  cursor: pointer;
  color: #999;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f5f5f5;
}

.form-actions .van-button {
  flex: 1;
}
</style>
```

### 📄 frontend/src/components/ExportButton.vue
```
<template>
  <van-button
    type="primary"
    size="small"
    icon="down"
    :loading="exporting"
    loading-text="导出中..."
    @click="handleExport"
  >
    导出Excel
  </van-button>
</template>

<script setup>
import { ref } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { exportTransactions } from '@/api/transaction'
import { downloadExport } from '@/utils/export'

const props = defineProps({
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' },
  category: { type: String, default: '' },
  type: { type: String, default: '' },
  totalCount: { type: Number, default: 0 },
})

const exporting = ref(false)

async function handleExport() {
  // 大数据量提示
  if (props.totalCount >= 1000) {
    try {
      await showConfirmDialog({
        title: '数据量较大',
        message: `当前筛选结果共 ${props.totalCount} 条记录，导出可能需要较长时间，确定要继续吗？`,
        confirmButtonText: '确定导出',
        cancelButtonText: '取消',
      })
    } catch {
      return // 用户取消
    }
  }

  exporting.value = true
  try {
    const params = {}
    if (props.startDate) params.start_date = props.startDate
    if (props.endDate) params.end_date = props.endDate
    if (props.category) params.category = props.category
    if (props.type) params.type = props.type

    const response = await exportTransactions(params)
    // 从blob中下载
    downloadExport(response)
    showToast({ message: '导出成功', type: 'success' })
  } catch (error) {
    showToast('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}
</script>
```

### 📄 frontend/src/components/ReceiptUploader.vue
```
<template>
  <div class="receipt-uploader">
    <!-- 上传区域 -->
    <div class="upload-section">
      <van-uploader
        v-model="fileList"
        :max-count="1"
        :after-read="onFileRead"
        accept="image/*"
        capture="camera"
        :preview-size="80"
      >
        <div class="upload-trigger">
          <van-icon name="photograph" size="40" color="#1989fa" />
          <span>拍照或选择图片</span>
        </div>
      </van-uploader>
    </div>

    <!-- 开始识别按钮 -->
    <van-button
      v-if="fileList.length > 0 && !hasResult"
      type="primary"
      block
      :loading="isRecognizing"
      loading-text="AI正在识别中，请稍候..."
      class="recognize-btn"
      @click="startRecognize"
    >
      开始识别
    </van-button>

    <!-- 识别中状态 -->
    <div v-if="isRecognizing" class="loading-area">
      <van-loading size="36" vertical>
        AI正在识别中，请稍候...
      </van-loading>
    </div>

    <!-- 识别结果区域 -->
    <div v-if="hasResult" class="result-section">
      <!-- 待核对提示 -->
      <div v-if="matchStatus === 'needs_check'" class="check-banner">
        <van-tag type="danger" size="large">请核对</van-tag>
        <span>AI识别结果存在不一致，请仔细核对各项信息</span>
      </div>

      <!-- 交易日期 -->
      <div class="field-row" :style="getConfidenceBg('date')">
        <van-field
          v-model="form.transaction_date"
          label="交易日期"
          placeholder="YYYY-MM-DD"
          :border="false"
        />
      </div>

      <!-- 金额 -->
      <div class="field-row" :style="getConfidenceBg('amount')">
        <van-field
          v-model="form.amount"
          label="金额"
          type="number"
          placeholder="请输入金额"
          :border="false"
        >
          <template #button>
            <span class="amount-prefix">¥</span>
          </template>
        </van-field>
      </div>

      <!-- 类型 -->
      <div class="field-row">
        <div class="type-selector">
          <span class="type-label">类型</span>
          <van-radio-group v-model="form.type" direction="horizontal">
            <van-radio name="expense">支出</van-radio>
            <van-radio name="income">收入</van-radio>
          </van-radio-group>
        </div>
      </div>

      <!-- 分类 -->
      <div class="field-row" :style="getConfidenceBg('category')">
        <van-field
          v-model="form.category"
          is-link
          readonly
          label="分类"
          placeholder="请选择分类"
          :border="false"
          @click="showCategoryPicker = true"
        />
      </div>

      <!-- 供应商 -->
      <div class="field-row" :style="getConfidenceBg('supplier')">
        <van-field
          v-model="form.supplier"
          label="供应商"
          placeholder="请输入供应商"
          :border="false"
        />
      </div>

      <!-- 备注 -->
      <div class="field-row">
        <van-field
          v-model="form.notes"
          label="备注"
          type="textarea"
          placeholder="请输入备注信息"
          :border="false"
          autosize
        />
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <van-button plain block @click="resetForm">重新上传</van-button>
        <van-button type="primary" block @click="openConfirm">确认入库</van-button>
      </div>
    </div>

    <!-- 分类选择弹窗 -->
    <van-popup v-model:show="showCategoryPicker" position="bottom" round>
      <van-picker
        :columns="currentCategoryColumns"
        @confirm="onCategoryConfirm"
        @cancel="showCategoryPicker = false"
      />
    </van-popup>

    <!-- 确认弹窗 -->
    <ConfirmDialog ref="confirmDialogRef" :form-data="submitData" @success="onSubmitSuccess" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { showToast } from 'vant'
import { recognizeReceipt } from '@/api/ai'
import { useBookkeepingStore } from '@/stores/bookkeeping'
import ConfirmDialog from './ConfirmDialog.vue'

const store = useBookkeepingStore()

// 文件列表
const fileList = ref([])
const imageFile = ref(null)
const isRecognizing = ref(false)
const hasResult = ref(false)
const matchStatus = ref('')

// 表单数据
const form = ref({
  transaction_date: '',
  amount: '',
  type: 'expense',
  category: '',
  supplier: '',
  notes: ''
})

// 各字段置信度
const confidence = ref({
  date: 'high',
  amount: 'high',
  category: 'high',
  supplier: 'high'
})

// 分类选择
const showCategoryPicker = ref(false)

// 默认12个分类（后续接API）
const expenseCategories = [
  '食材', '酒水饮料', '房租', '工资', '水电燃气',
  '耗材餐具', '设备维修', '运输配送', '税费管理', '其他支出'
]
const incomeCategories = ['营业收入', '其他收入']

const currentCategoryColumns = computed(() => {
  return form.value.type === 'income' ? incomeCategories : expenseCategories
})

// 监听类型切换时重置分类
watch(() => form.value.type, () => {
  form.value.category = ''
})

// 提交数据（转换为后端需要的格式）
const submitData = computed(() => ({
  transaction_date: form.value.transaction_date,
  amount: parseFloat(form.value.amount) || 0,
  type: form.value.type,
  category: form.value.category,
  supplier: form.value.supplier,
  notes: form.value.notes,
  ai_confidence: confidence.value.amount,
  ai_match_status: matchStatus.value
}))

const emit = defineEmits(['refresh'])

const confirmDialogRef = ref(null)

function onFileRead(file) {
  imageFile.value = file.file
  hasResult.value = false
}

async function startRecognize() {
  if (!imageFile.value) {
    showToast('请先选择图片')
    return
  }

  isRecognizing.value = true
  store.isRecognizing = true

  try {
    const result = await recognizeReceipt(imageFile.value)

    // 映射AI返回数据到表单
    // AI返回type为中文"支出"/"收入"，需要转为英文
    const typeMap = { '支出': 'expense', '收入': 'income' }
    form.value.transaction_date = result.transaction_date || ''
    form.value.amount = result.amount != null ? String(result.amount) : ''
    form.value.type = typeMap[result.type] || 'expense'
    form.value.category = result.category || ''
    form.value.supplier = result.supplier || ''
    form.value.notes = result.notes || ''

    // 映射置信度
    if (result.confidence) {
      confidence.value = {
        date: result.confidence.date || 'medium',
        amount: result.confidence.amount || 'medium',
        category: result.confidence.category || 'medium',
        supplier: result.confidence.supplier || 'medium'
      }
    }

    matchStatus.value = result.match_status || 'matched'
    hasResult.value = true
    store.setRecognitionResult(result)
  } catch (e) {
    // 错误已在axios拦截器中统一处理
  } finally {
    isRecognizing.value = false
    store.isRecognizing = false
  }
}

function getConfidenceBg(field) {
  const level = confidence.value[field]
  if (level === 'medium') return { backgroundColor: '#fff9e6' }
  if (level === 'low') return { backgroundColor: '#ffe6e6' }
  return {}
}

function onCategoryConfirm({ selectedValues }) {
  form.value.category = selectedValues[0]
  showCategoryPicker.value = false
}

function openConfirm() {
  if (!form.value.transaction_date) {
    showToast('请填写交易日期')
    return
  }
  if (!form.value.amount || parseFloat(form.value.amount) <= 0) {
    showToast('请填写有效金额')
    return
  }
  confirmDialogRef.value?.open()
}

function resetForm() {
  fileList.value = []
  imageFile.value = null
  hasResult.value = false
  matchStatus.value = ''
  form.value = {
    transaction_date: '',
    amount: '',
    type: 'expense',
    category: '',
    supplier: '',
    notes: ''
  }
  confidence.value = { date: 'high', amount: 'high', category: 'high', supplier: 'high' }
  store.clearRecognitionResult()
}

function onSubmitSuccess() {
  resetForm()
  emit('refresh')
}
</script>

<style scoped>
.receipt-uploader {
  padding: 0;
}

.upload-section {
  padding: 16px;
}

.upload-trigger {
  width: 100%;
  height: 120px;
  border: 2px dashed #dcdee0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #fafafa;
  font-size: 14px;
  color: #969799;
}

.recognize-btn {
  margin: 0 16px 16px;
}

.loading-area {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.result-section {
  background: #fff;
  margin: 0 12px 16px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.check-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #fff0f0;
  font-size: 13px;
  color: #ee0a24;
}

.field-row {
  border-bottom: 1px solid #f5f5f5;
  transition: background-color 0.2s;
}

.field-row:last-of-type {
  border-bottom: none;
}

.type-selector {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  gap: 16px;
}

.type-label {
  font-size: 14px;
  color: #646566;
  flex-shrink: 0;
}

.amount-prefix {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
}

.action-buttons {
  display: flex;
  gap: 12px;
  padding: 16px;
}
</style>
```

### 📄 frontend/src/components/TransactionList.vue
```
<template>
  <div class="transaction-list">
    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多了"
      loading-text="正在加载数据，请稍候…"
      @load="onLoad"
    >
      <van-cell
        v-for="item in transactions"
        :key="item.id"
        class="transaction-item"
        clickable
        @click="$emit('edit', item)"
      >
        <template #title>
          <div class="transaction-header">
            <span class="date">{{ item.transaction_date }}</span>
            <van-tag v-if="item.category" type="primary" plain size="medium" class="category-tag">
              {{ item.category }}
            </van-tag>
          </div>
        </template>
        <template #label>
          <div class="transaction-info">
            <span class="supplier">{{ item.supplier || '未知供应商' }}</span>
            <van-tag
              :type="statusTagType(item.status)"
              size="medium"
              class="status-tag"
            >
              {{ statusText(item.status) }}
            </van-tag>
            <span
              class="voucher-link"
              @click.stop="$emit('voucher', item)"
            >
              <van-icon name="photo-o" />
              <span v-if="item.voucher_urls && item.voucher_urls.length > 0">
                凭证({{ item.voucher_urls.length }})
              </span>
              <span v-else>凭证</span>
            </span>
          </div>
        </template>
        <template #value>
          <span class="amount" :class="item.type">
            {{ item.type === 'income' ? '+' : '-' }}¥{{ formatAmount(item.amount) }}
          </span>
        </template>
      </van-cell>

      <!-- 空状态 -->
      <van-empty
        v-if="!loading && finished && transactions.length === 0"
        description="暂无交易记录"
      />
    </van-list>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getTransactions } from '@/api/transaction'

const props = defineProps({
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' },
  category: { type: String, default: '' },
  type: { type: String, default: '' },
})

const emit = defineEmits(['edit', 'voucher', 'totalChange'])

const transactions = ref([])
const loading = ref(false)
const finished = ref(false)
const page = ref(1)
const totalCount = ref(0)

/** 格式化金额 */
function formatAmount(amount) {
  return parseFloat(amount || 0).toFixed(2)
}

/** 状态文字 */
function statusText(status) {
  const map = {
    confirmed: '已确认',
    modified: '已修改',
    pending: '待确认',
  }
  return map[status] || status
}

/** 状态标签类型 */
function statusTagType(status) {
  const map = {
    confirmed: 'success',
    modified: 'warning',
    pending: 'default',
  }
  return map[status] || 'default'
}

/** 加载一页数据 */
async function onLoad() {
  try {
    const params = {
      page: page.value,
      per_page: 20,
    }
    if (props.startDate) params.start_date = props.startDate
    if (props.endDate) params.end_date = props.endDate
    if (props.category) params.category = props.category
    if (props.type) params.type = props.type

    const res = await getTransactions(params)
    const items = res.items || []

    if (page.value === 1) {
      transactions.value = items
    } else {
      transactions.value.push(...items)
    }

    totalCount.value = res.total || 0
    emit('totalChange', totalCount.value)

    if (transactions.value.length >= totalCount.value || items.length < 20) {
      finished.value = true
    } else {
      page.value++
    }
  } catch (error) {
    finished.value = true
  } finally {
    loading.value = false
  }
}

/** 重置列表并重新加载 */
function reload() {
  page.value = 1
  transactions.value = []
  finished.value = false
  loading.value = true
  // 手动触发加载，van-list 不会仅因 loading 变 true 就自动触发 @load
  onLoad()
}

/** 暴露 reload 给父组件 */
defineExpose({ reload })

/** 监听筛选条件变化自动重新查询 */
watch(
  () => [props.startDate, props.endDate, props.category, props.type],
  () => {
    reload()
  }
)
</script>

<style scoped>
.transaction-list {
  background: #fff;
}

.transaction-item {
  border-bottom: 1px solid #f5f5f5;
}

.transaction-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.transaction-header .date {
  font-size: 14px;
  color: #333;
}

.category-tag {
  flex-shrink: 0;
}

.transaction-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.transaction-info .supplier {
  font-size: 12px;
  color: #999;
}

.status-tag {
  flex-shrink: 0;
}

.voucher-link {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #1989fa;
  cursor: pointer;
  padding: 2px 6px;
  background: #e8f4ff;
  border-radius: 4px;
  flex-shrink: 0;
}

.amount {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.amount.income {
  color: #07c160;
}

.amount.expense {
  color: #ee0a24;
}
</style>
```

### 📄 frontend/src/components/VoiceRecorder.vue
```
<template>
  <div class="voice-recorder">
    <div class="record-area">
      <div
        class="record-btn"
        :class="{ recording: isRecording }"
        @touchstart.prevent="startRecord"
        @touchend.prevent="stopRecord"
        @touchcancel.prevent="stopRecord"
        @mousedown.prevent="startRecord"
        @mouseup.prevent="stopRecord"
        @mouseleave="stopRecord"
      >
        <van-icon name="audio" size="36" color="#fff" />
        <span class="record-text">{{ isRecording ? '松开结束' : '按住说话' }}</span>
      </div>
      <div v-if="isRecording" class="record-timer">
        录音中 {{ formatDuration(duration) }}
      </div>
    </div>

    <div v-if="audioBlob" class="record-result">
      <van-cell title="录音完成" :value="formatDuration(duration)" />
      <van-button size="small" plain @click="playAudio" class="play-btn">
        <van-icon name="play" /> 回放
      </van-button>
    </div>

    <div class="dev-hint">
      <van-icon name="info-o" />
      <span>语音记账功能开发中，当前版本仅支持录音预览</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'

const emit = defineEmits(['recorded'])

const isRecording = ref(false)
const duration = ref(0)
const audioBlob = ref(null)

let mediaRecorder = null
let audioChunks = []
let timer = null
let audioUrl = null

async function startRecord() {
  if (isRecording.value) return
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data)
    }

    mediaRecorder.onstop = () => {
      audioBlob.value = new Blob(audioChunks, { type: 'audio/webm' })
      stream.getTracks().forEach(track => track.stop())
      emit('recorded', audioBlob.value)
    }

    mediaRecorder.start()
    isRecording.value = true
    duration.value = 0
    timer = setInterval(() => { duration.value++ }, 1000)
  } catch (e) {
    // 用户拒绝权限或不支持
    isRecording.value = false
  }
}

function stopRecord() {
  if (!isRecording.value || !mediaRecorder) return
  isRecording.value = false
  clearInterval(timer)
  if (mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  mediaRecorder = null
}

function playAudio() {
  if (!audioBlob.value) return
  if (audioUrl) URL.revokeObjectURL(audioUrl)
  audioUrl = URL.createObjectURL(audioBlob.value)
  const audio = new Audio(audioUrl)
  audio.play()
}

function formatDuration(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

onBeforeUnmount(() => {
  clearInterval(timer)
  if (audioUrl) URL.revokeObjectURL(audioUrl)
})
</script>

<style scoped>
.voice-recorder {
  padding: 20px;
}

.record-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

.record-btn {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa, #07c160);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 12px rgba(25, 137, 250, 0.3);
  user-select: none;
}

.record-btn.recording {
  transform: scale(1.15);
  background: linear-gradient(135deg, #ee0a24, #ff6034);
  box-shadow: 0 4px 20px rgba(238, 10, 36, 0.4);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 20px rgba(238, 10, 36, 0.4); }
  50% { box-shadow: 0 4px 30px rgba(238, 10, 36, 0.7); }
}

.record-text {
  font-size: 11px;
  color: #fff;
}

.record-timer {
  margin-top: 16px;
  font-size: 16px;
  color: #ee0a24;
  font-weight: bold;
}

.record-result {
  margin-top: 16px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.play-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.dev-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 24px;
  padding: 12px;
  background: #fff8e6;
  border-radius: 8px;
  font-size: 12px;
  color: #ed6a0c;
}
</style>
```

### 📄 frontend/src/components/VoucherPanel.vue
```
<template>
  <van-popup
    v-model:show="visible"
    position="bottom"
    round
    :style="{ maxHeight: '80vh' }"
  >
    <div class="voucher-panel">
      <div class="panel-header">
        <span>记账凭证</span>
        <span class="panel-sub">凭证用于报税备查，请妥善保存</span>
        <van-icon name="cross" class="close-icon" @click="visible = false" />
      </div>

      <!-- 已有凭证 -->
      <div class="voucher-list" v-if="voucherBlobs.length > 0">
        <div class="voucher-item" v-for="(v, i) in voucherBlobs" :key="i" @click="preview(i)">
          <img :src="v.url" class="voucher-thumb" alt="凭证" />
        </div>
      </div>
      <van-empty v-else description="暂无凭证，请上传" image="image" :image-size="60" />

      <!-- 上传区域 -->
      <div class="upload-row">
        <van-uploader
          v-model="fileList"
          :max-count="9"
          accept="image/*"
          :after-read="onFileRead"
          multiple
        >
          <van-button size="small" type="primary" plain icon="plus">添加凭证</van-button>
        </van-uploader>
        <van-button
          v-if="pendingFiles.length > 0"
          size="small"
          type="primary"
          :loading="uploading"
          loading-text="上传中..."
          @click="handleUpload"
        >
          上传 {{ pendingFiles.length }} 张
        </van-button>
      </div>

      <!-- 操作提示 -->
      <div class="panel-tip">
        <van-icon name="info-o" />
        <span>凭证将与这笔账绑定保存，查账时可随时点开查看、导出</span>
      </div>
    </div>

    <!-- 图片预览 -->
    <van-image-preview
      v-model:show="showPreview"
      :images="previewImages"
      :start-position="previewIndex"
    />
  </van-popup>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { showToast } from 'vant'
import { uploadVouchers } from '@/api/transaction'
import api from '@/api/index'

const props = defineProps({
  show: { type: Boolean, default: false },
  transaction: { type: Object, default: null },
})

const emit = defineEmits(['update:show', 'uploaded'])

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val),
})

const voucherBlobs = ref([]) // { url } 列表（blob URL）
const fileList = ref([])      // van-uploader 已选文件
const pendingFiles = ref([])  // 待上传的 File 对象
const uploading = ref(false)

const showPreview = ref(false)
const previewIndex = ref(0)

const previewImages = computed(() => voucherBlobs.value.map(v => v.url))

/** 打开面板时，把该交易的凭证URL加载为可显示的 blob */
async function loadVouchers() {
  voucherBlobs.value = []
  fileList.value = []
  pendingFiles.value = []
  if (!props.transaction || !props.transaction.voucher_urls || props.transaction.voucher_urls.length === 0) {
    return
  }
  // 逐张拉取（凭证接口需要JWT，不能直接用<img src>）
  for (const url of props.transaction.voucher_urls) {
    try {
      const res = await api.get(url, { responseType: 'blob' })
      const objectUrl = URL.createObjectURL(res)
      voucherBlobs.value.push({ url: objectUrl })
    } catch (e) {
      // 单张加载失败不影响其他
      console.error('凭证加载失败:', url, e)
    }
  }
}

function onFileRead(file) {
  if (file && file.file) {
    pendingFiles.value.push(file.file)
  }
}

async function handleUpload() {
  if (pendingFiles.value.length === 0 || !props.transaction) return
  uploading.value = true
  try {
    const res = await uploadVouchers(props.transaction.id, pendingFiles.value)
    showToast(res.message || '上传成功')
    pendingFiles.value = []
    fileList.value = []
    emit('uploaded')
    await loadVouchers()
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    uploading.value = false
  }
}

function preview(index) {
  previewIndex.value = index
  showPreview.value = true
}

watch(
  () => props.show,
  (val) => {
    if (val) loadVouchers()
  }
)
</script>

<style scoped>
.voucher-panel {
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 14px;
  position: relative;
}

.panel-sub {
  font-size: 12px;
  font-weight: normal;
  color: #969799;
  flex: 1;
}

.close-icon {
  color: #999;
  font-size: 18px;
  cursor: pointer;
}

.voucher-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.voucher-item {
  width: 90px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebedf0;
  cursor: pointer;
}

.voucher-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.panel-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
  padding: 10px;
  background: #f7f8fa;
  border-radius: 8px;
  font-size: 12px;
  color: #646566;
}
</style>
```

### 📄 frontend/src/components/chat/BookkeepingCard.vue
```
<template>
  <div class="bookkeeping-card">
    <!-- 风险提示 -->
    <div class="card-warning">
      <van-icon name="warning-o" size="14" color="#ee0a24" />
      <span>数据将影响报表与报税，请仔细核对后确认</span>
    </div>

    <!-- 高可信数据区 -->
    <div class="data-section">
      <div class="section-label high">✔ 已识别</div>
      <div class="field-grid">
        <div class="field-item">
          <span class="field-name">交易日期</span>
          <span class="field-value">{{ data.transaction_date || '-' }}</span>
        </div>
        <div class="field-item">
          <span class="field-name">金额</span>
          <span class="field-value amount">¥{{ fmtAmount(data.amount) }}</span>
        </div>
        <div class="field-item">
          <span class="field-name">类型</span>
          <span class="field-value" :class="data.type === 'income' ? 'green' : 'red'">
            {{ data.type === 'income' ? '收入' : '支出' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 低可信数据区 -->
    <div v-if="lowConfidenceFields.length > 0" class="data-section low-section">
      <div class="section-label low">需要您确认</div>
      <div v-for="lf in lowConfidenceFields" :key="lf.field" class="low-field-item">
        <div class="low-field-info">
          <span class="field-name">{{ lf.label }}</span>
          <van-tag :type="lf.level === 'low' ? 'danger' : 'warning'" size="mini">
            {{ lf.level === 'low' ? '不确定' : '需核对' }}
          </van-tag>
        </div>
        <div class="low-field-value">
          <van-field
            v-model="editable[lf.field]"
            size="small"
            :placeholder="'请输入' + lf.label"
            class="low-input"
          />
          <van-button size="small" type="primary" plain @click="confirmField(lf.field)">确认</van-button>
        </div>
      </div>
    </div>

    <!-- 全部低可信字段处理完，才出现入库按钮 -->
    <van-button
      v-if="allConfirmed"
      type="primary"
      block
      round
      :loading="submitting"
      loading-text="入库中..."
      class="submit-btn"
      @click="submit"
    >
      全部确认，入库
    </van-button>
    <div v-else class="submit-placeholder">
      <span v-if="lowConfidenceFields.length > 0">请先确认所有"需要您确认"的项目</span>
      <span v-else>点击下方按钮完成入库</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { showToast } from 'vant'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
  lowFields: { type: Array, default: () => [] },
})

const emit = defineEmits(['confirm'])

const submitting = ref(false)
const editable = reactive({})

// 初始化可编辑字段
props.lowFields.forEach(lf => {
  editable[lf.field] = lf.value || ''
})

// 已确认的低可信字段
const confirmedFields = ref([])

const lowConfidenceFields = computed(() => props.lowFields || [])

const allConfirmed = computed(() => {
  if (lowConfidenceFields.value.length === 0) return true
  return confirmedFields.value.length >= lowConfidenceFields.value.length
})

function confirmField(field) {
  const lf = lowConfidenceFields.value.find(f => f.field === field)
  if (lf && (lf.field === 'amount' || lf.field === 'date')) {
    if (!editable[field]) {
      showToast('请先填写' + lf.label)
      return
    }
  }
  if (!confirmedFields.value.includes(field)) {
    confirmedFields.value.push(field)
  }
  showToast('已确认')
}

function fmtAmount(val) {
  const n = parseFloat(val || 0)
  return n.toFixed(2)
}

async function submit() {
  submitting.value = true
  try {
    // 合并确认后的字段
    const finalData = { ...props.data }
    lowConfidenceFields.value.forEach(lf => {
      const key = lf.field
      if (key === 'amount') {
        finalData.amount = parseFloat(editable[key] || finalData.amount)
      } else if (key === 'date') {
        finalData.transaction_date = editable[key] || finalData.transaction_date
      } else if (key === 'category') {
        finalData.category = editable[key] || finalData.category
      } else if (key === 'supplier') {
        finalData.supplier = editable[key] || finalData.supplier
      }
    })
    emit('confirm', finalData)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.bookkeeping-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #ebedf0;
  overflow: hidden;
  width: 100%;
  min-width: 300px;
}

.card-warning {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fff0f0;
  padding: 8px 12px;
  font-size: 12px;
  color: #ee0a24;
}

.data-section {
  padding: 12px;
}

.low-section {
  background: #fffbef;
  border-top: 1px dashed #f0e3c8;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 10px;
}

.section-label.high { color: #07c160; }
.section-label.low { color: #b7791f; }

.field-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.field-item {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-name {
  font-size: 12px;
  color: #969799;
}

.field-value {
  font-size: 14px;
  font-weight: 600;
  color: #323233;
}

.field-value.amount { color: #1F6FB2; font-size: 16px; }
.field-value.green { color: #07c160; }
.field-value.red { color: #ee0a24; }

.low-field-item {
  background: #fff;
  border: 1px solid #f0e3c8;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 8px;
}

.low-field-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.low-field-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.low-input {
  flex: 1;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 0 10px;
}

.submit-btn {
  margin: 12px;
}

.submit-placeholder {
  text-align: center;
  padding: 10px;
  font-size: 12px;
  color: #c8c9cc;
  border-top: 1px solid #f5f5f5;
}
</style>
```


## 📁 frontend/src/router/

### 📄 frontend/src/router/index.js
```
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
```


## 📁 frontend/src/config/

### 📄 frontend/src/config/menu.js
```
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
 *   - quick-text   直接把 text 当作一条用户消息发给现有流程
 *   - tax-draft    调用后端生成报税底稿
 *   - tax-reminder 本地生成报税日期提醒
 *   - export-excel 导出账目 Excel
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
          { label: '查询本月申报', command: 'tax-reminder', type: 'primary' },
          { label: '查询季度申报', command: 'tax-reminder', quarter: true },
        ],
      },
      {
        id: 'tax-draft',
        icon: 'description',
        label: '报税底稿',
        module: 'tax-draft',
        greeting: '点下面的按钮，我根据您的账目一键生成报税底稿。',
        actions: [
          { label: '生成本月报税底稿', command: 'tax-draft', type: 'primary' },
          { label: '生成上个月报税底稿', command: 'tax-draft', lastMonth: true },
        ],
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
```


## 📁 frontend/src/stores/

### 📄 frontend/src/stores/analytics.js
```
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAnalyticsStore = defineStore('analytics', () => {
  const timeDimension = ref('week')  // day/week/month/year/custom
  const chartType = ref('bar')       // bar/line/pie/table
  const dateRange = ref({ start: null, end: null })  // 自定义日期范围

  return { timeDimension, chartType, dateRange }
})
```

### 📄 frontend/src/stores/bookkeeping.js
```
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBookkeepingStore = defineStore('bookkeeping', () => {
  // 当前识别结果（待确认的数据）
  const recognitionResult = ref(null)
  const isRecognizing = ref(false)

  // 今日记录
  const todayTransactions = ref([])
  const todaySummary = ref({ total_income: 0, total_expense: 0, total_profit: 0 })

  function setRecognitionResult(result) {
    recognitionResult.value = result
  }

  function clearRecognitionResult() {
    recognitionResult.value = null
  }

  function addToToday(transaction) {
    todayTransactions.value.unshift(transaction)
    // 更新汇总
    if (transaction.type === 'income') {
      todaySummary.value.total_income += parseFloat(transaction.amount)
    } else {
      todaySummary.value.total_expense += parseFloat(transaction.amount)
    }
    todaySummary.value.total_profit = todaySummary.value.total_income - todaySummary.value.total_expense
  }

  function resetToday() {
    todayTransactions.value = []
    todaySummary.value = { total_income: 0, total_expense: 0, total_profit: 0 }
  }

  return {
    recognitionResult, isRecognizing,
    todayTransactions, todaySummary,
    setRecognitionResult, clearRecognitionResult, addToToday, resetToday
  }
})
```

### 📄 frontend/src/stores/chat.js
```
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { MENU_SECTIONS } from '@/config/menu'

// 消息类型：
// text - 纯文本气泡
// image - 图片消息（用户上传的）
// voucher-card - 凭证卡片
// bookkeeping-card - 记账核验卡片
// list - 列表卡片（查账/客户列表）

export const useChatStore = defineStore('chat', () => {
  // 每个功能项的会话消息
  const sessions = ref({})

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
    if (!sessions.value[featureId]) {
      const config = getFeatureConfig(featureId)
      const greeting = config?.greeting || '您好，有什么可以帮您？'
      sessions.value[featureId] = [
        { id: `g-${featureId}-${Date.now()}`, role: 'assistant', type: 'text', content: greeting, time: Date.now() },
      ]
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
    return sessions.value[featureId]
  }

  // 清空会话
  function clearSession(featureId) {
    sessions.value[featureId] = []
  }

  return { sessions, ensureSession, addMessage, clearSession, getFeatureConfig }
})
```

### 📄 frontend/src/stores/user.js
```
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/index.js'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  const subscriptionText = computed(() => {
    if (!userInfo.value) return ''
    const planMap = { free: '免费体验', basic: '基础版', advanced: '进阶版', clerk: '文员版' }
    const typeMap = { daily: '日付', monthly: '月付', yearly: '年付' }
    const plan = planMap[userInfo.value.subscription_plan] || '免费体验'
    const type = typeMap[userInfo.value.subscription_type] || ''
    return `${plan}${type ? '（' + type + '）' : ''}`
  })

  const isExpiringSoon = computed(() => {
    if (!userInfo.value?.subscription_expiry) return false
    const expiry = new Date(userInfo.value.subscription_expiry)
    const now = new Date()
    const daysLeft = (expiry - now) / (1000 * 60 * 60 * 24)
    return daysLeft <= 7 && daysLeft > 0
  })

  const daysUntilExpiry = computed(() => {
    if (!userInfo.value?.subscription_expiry) return null
    const expiry = new Date(userInfo.value.subscription_expiry)
    const now = new Date()
    return Math.ceil((expiry - now) / (1000 * 60 * 60 * 24))
  })

  async function login(phone, password) {
    const res = await api.post('/auth/login', { phone, password })
    token.value = res.token
    localStorage.setItem('token', res.token)
    userInfo.value = res.user
    return res
  }

  async function register(phone, password, industry, referral_code) {
    const res = await api.post('/auth/register', { phone, password, industry, referral_code })
    token.value = res.token
    localStorage.setItem('token', res.token)
    userInfo.value = res.user
    return res
  }

  async function fetchUserInfo() {
    try {
      // /auth/me 直接返回用户对象（拦截器已剥掉 response.data），没有 .user 包装
      const user = await api.get('/auth/me')
      userInfo.value = user
    } catch (e) {
      // token无效，清除
      logout()
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token, userInfo, isLoggedIn,
    subscriptionText, isExpiringSoon, daysUntilExpiry,
    login, register, fetchUserInfo, logout
  }
})
```


## 📁 frontend/src/api/

### 📄 frontend/src/api/ai.js
```
import api from './index'

// 图片识别
export function recognizeReceipt(imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)
  return api.post('/ai/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000 // AI识别可能较慢
  })
}

// 语音记账（预留）
export function voiceToText(audioFile) {
  const formData = new FormData()
  formData.append('audio', audioFile)
  return api.post('/ai/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 一键生成报税底稿
export function getTaxDraft(params = {}) {
  return api.get('/ai/tax-draft', { params })
}
```

### 📄 frontend/src/api/analytics.js
```
import api from './index'

export function getDailyData(params) {
  return api.get('/analytics/daily', { params })
}

export function getTrendData(params) {
  return api.get('/analytics/trend', { params })
}

export function getCategoryRatio(params) {
  return api.get('/analytics/category-ratio', { params })
}

export function getComparison(params) {
  return api.get('/analytics/comparison', { params })
}
```

### 📄 frontend/src/api/auth.js
```
import api from './index'

export function loginApi(phone, password) {
  return api.post('/auth/login', { phone, password })
}

export function registerApi(phone, password, industry, referral_code) {
  return api.post('/auth/register', { phone, password, industry, referral_code })
}

export function getMeApi() {
  return api.get('/auth/me')
}
```

### 📄 frontend/src/api/index.js
```
import axios from 'axios'
import { showToast } from 'vant'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30秒（AI识别较慢）
})

// 请求拦截器：附加JWT token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      showToast('登录已过期，请重新登录')
    } else {
      showToast(error.response?.data?.message || '网络错误，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default api
```

### 📄 frontend/src/api/referral.js
```
import api from './index'

export function getReferralInfo() {
  return api.get('/referral/info')
}
```

### 📄 frontend/src/api/transaction.js
```
import api from './index'

// 确认入库
export function createTransaction(data) {
  return api.post('/transactions', data)
}

// 分页查账
export function getTransactions(params) {
  return api.get('/transactions', { params })
}

// 修改已入账数据
export function updateTransaction(id, data) {
  return api.put(`/transactions/${id}`, data)
}

// 时间段汇总
export function getTransactionSummary(params) {
  return api.get('/transactions/summary', { params })
}

// 导出Excel
export function exportTransactions(params) {
  return api.get('/transactions/export', { params, responseType: 'blob' })
}

// 上传凭证图片
export function uploadVouchers(id, fileList) {
  const formData = new FormData()
  fileList.forEach(file => formData.append('images', file))
  return api.post(`/transactions/${id}/vouchers`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
}
```


## 📁 frontend/src/styles/

### 📄 frontend/src/styles/theme.css
```
/* ============================================================
   AI虚拟文员 · 全局主题
   设计风格：现代简洁商务风
   主色：深绿（钱/账的直觉色，与登录页呼应）
   ============================================================ */

:root {
  /* ── 品牌主色 ── */
  --brand: #123F33;          /* 主深绿 */
  --brand-strong: #0D2E26;   /* 更深(悬浮/按压) */
  --brand-soft: #EAF3EF;     /* 浅绿底(选中/高亮) */
  --brand-tint: #F4F8F6;     /* 极浅绿(卡片/区块底) */

  /* ── 中性色板 ── */
  --ink: #1F2421;            /* 主文字 */
  --ink-2: #4A5560;          /* 次级文字 */
  --ink-3: #8A938D;          /* 弱文字/提示 */
  --line: #E6EAE7;           /* 分隔线 */
  --bg: #F6F8F7;             /* 页面底色(浅灰) */
  --card: #FFFFFF;           /* 卡片底色 */
  --white: #FFFFFF;

  /* ── 语义色(克制使用) ── */
  --up: #0E8A5F;             /* 收入/增长(绿) */
  --down: #D14343;           /* 支出/下降(红) */
  --warn: #C9932E;           /* 警示/提示(金) */

  /* ── 形状与阴影 ── */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --shadow-1: 0 1px 3px rgba(18, 63, 51, 0.06);
  --shadow-2: 0 4px 16px rgba(18, 63, 51, 0.08);
  --shadow-3: 0 12px 32px rgba(18, 63, 51, 0.12);

  /* ── 字号阶梯 ── */
  --fs-caption: 12px;
  --fs-body: 14px;
  --fs-title: 16px;
  --fs-h2: 20px;
  --fs-h1: 28px;
}

/* ── Vant 组件全局覆盖：把默认蓝换成深绿 ── */
:root:root {
  --van-primary-color: var(--brand);
  --van-success-color: var(--up);
  --van-danger-color: var(--down);
  --van-warning-color: var(--warn);
  --van-text-color: var(--ink);
  --van-text-color-2: var(--ink-2);
  --van-text-color-3: var(--ink-3);
  --van-border-color: var(--line);
  --van-background: var(--bg);
  --van-background-2: var(--card);
  --van-radius-md: var(--radius-sm);
  --van-radius-lg: var(--radius-md);
  --van-nav-bar-background: var(--card);
  --van-nav-bar-title-text-color: var(--ink);
  --van-nav-bar-icon-color: var(--ink-2);
  --van-tabbar-background: var(--card);
  --van-tabbar-item-active-color: var(--brand);
  --van-cell-group-background: transparent;
  --van-button-default-border-color: var(--line);
  --van-button-primary-background: var(--brand);
  --van-button-primary-border-color: var(--brand);
  --van-tabs-bottom-bar-color: var(--brand);
  --van-tab-active-text-color: var(--brand);
  --van-tabs-nav-background: var(--card);
  --van-picker-background: var(--card);
  --van-popup-background: var(--card);
  --van-calendar-background: var(--card);
  --van-field-input-text-color: var(--ink);
  --van-toast-background: rgba(18, 63, 51, 0.88);
  --van-tag-primary-color: var(--brand);
}

/* ── 全局基础 ── */
html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}

* { box-sizing: border-box; }

/* 通用卡片 */
.g-card {
  background: var(--card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-1);
  border: 1px solid rgba(18, 63, 51, 0.05);
}
```


---

# 根目录脚本

### 📄 demo_server.py
```
"""
AI虚拟文员 - 一键演示服务器
同时提供：前端页面( dist 静态文件 ) + 后端 API
启动后浏览器打开 http://localhost:5000 即可使用
"""
import os
import sys

# 保证能 import 到 backend 里的模块
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE_DIR, 'backend'))

from flask import send_from_directory
from app import create_app
from extensions import db
from models.user import User

app = create_app('development')

# 演示账号自动升级为专业版（每次启动都生效，保证能看到全部功能）
# 若演示账号还不存在则跳过（首次请先运行 docbuild/seed_demo.py 造数据）
DEMO_PHONE = '13812345678'
with app.app_context():
    demo_user = User.query.filter_by(phone=DEMO_PHONE).first()
    if demo_user:
        changed = False
        if demo_user.subscription_plan != 'pro':
            demo_user.subscription_plan = 'pro'
            changed = True
        if demo_user.free_uses_remaining is None or demo_user.free_uses_remaining < 99:
            demo_user.free_uses_remaining = 999
            changed = True
        if changed:
            db.session.commit()
            print(f'[演示账号] {DEMO_PHONE} 已升级为专业版，免费次数 999')
        else:
            print(f'[演示账号] {DEMO_PHONE} 已是专业版')
    else:
        print(f'[提示] 未找到演示账号 {DEMO_PHONE}，请先运行 docbuild/seed_demo.py 创建演示数据')

# 前端构建产物目录
DIST_DIR = os.path.join(_BASE_DIR, 'frontend', 'dist')


@app.route('/')
def index():
    return send_from_directory(DIST_DIR, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """静态文件 + SPA 路由回退（history 模式）"""
    full = os.path.join(DIST_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(DIST_DIR, path)
    # 不是文件就回退到 index.html，交给 vue-router 处理
    return send_from_directory(DIST_DIR, 'index.html')


if __name__ == '__main__':
    print('=' * 50)
    print('  AI虚拟文员 演示服务器已启动')
    print('  请在浏览器打开:  http://localhost:5000')
    print('  演示账号:  13812345678 / 123456')
    print('  (关闭本窗口即停止服务)')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 📄 docbuild/seed_demo.py
```
import os, sys, time, json

# 自动定位 backend 目录：无论脚本从哪运行，都能找到本项目 backend
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # docbuild 目录
_BACKEND_DIR = os.path.join(os.path.dirname(_BASE_DIR), 'backend')  # 项目根/backend
sys.path.insert(0, _BACKEND_DIR)
from app import create_app
app = create_app('development')

client = app.test_client()

# 注册（若已存在则登录）
r = client.post('/api/auth/register', json={'phone':'13812345678','password':'123456','industry':'小吃店'})
if r.status_code == 201:
    d = r.get_json()
    token = d['token']
    print('注册:', r.status_code, d['user']['phone'])
elif r.status_code == 409:
    r = client.post('/api/auth/login', json={'phone':'13812345678','password':'123456'})
    d = r.get_json()
    token = d['token']
    print('账号已存在，直接登录:', d['user']['phone'])
else:
    print('注册/登录失败:', r.status_code, r.get_json())
    sys.exit(1)
H = {'Authorization': f'Bearer {token}'}

# 造演示数据（幂等：只补缺失的，重复运行不会翻倍）
# 先查当前交易总数，已 ≥ 9 笔就不再插入
r0 = client.get('/api/transactions', headers=H)
existing_total = r0.get_json()['total'] if r0.status_code == 200 else 0

seed = [
    ('2026-07-28', 215.0, 'expense', '食材', '蔬菜批发市场'),
    ('2026-07-29', 45.0, 'expense', '耗材餐具', '一次性用品店'),
    ('2026-07-30', 3200.0, 'income', '营业收入', '堂食+外卖'),
    ('2026-07-31', 180.0, 'expense', '酒水饮料', '雪花啤酒经销商'),
    ('2026-08-01', 235.5, 'expense', '食材', '水产批发'),
    ('2026-08-02', 1800.0, 'income', '营业收入', '堂食+外卖'),
    ('2026-08-03', 120.0, 'expense', '水电燃气', '供电局'),
    ('2026-08-04', 980.0, 'expense', '工资', '帮厨小李'),
    ('2026-08-05', 2600.0, 'income', '营业收入', '宴席包桌'),
]
created = 0
if existing_total < len(seed):
    for tx_date, amt, typ, cat, sup in seed:
        r = client.post('/api/transactions', headers=H, json={
            'transaction_date': tx_date, 'amount': amt, 'type': typ, 'category': cat, 'supplier': sup, 'notes': '演示数据'
        })
        assert r.status_code == 201, r.get_json()
        created += 1
    print('已创建', created, '笔演示交易')
else:
    print(f'已有 {existing_total} 笔交易，跳过播种（避免重复）')

# 确保演示账号是专业版
import sqlite3, os
_db_path = os.path.join(_BACKEND_DIR, 'instance', 'dev.db')
try:
    _conn = sqlite3.connect(_db_path)
    _conn.execute("UPDATE users SET subscription_plan='pro', free_uses_remaining=999 WHERE phone='13812345678'")
    _conn.commit()
    _conn.close()
    print('演示账号已升级为专业版')
except Exception as e:
    print('升级演示账号失败(可忽略,启动时会自动升级):', e)

# 验证
r = client.get('/api/transactions', headers=H)
d = r.get_json()
print('交易列表:', d['total'], '条, 首页', len(d['items']), '条')

r = client.get('/api/transactions/summary', headers=H)
print('汇总:', r.get_json())

r = client.get('/api/categories', headers=H)
cats = r.get_json()
print('支出分类数:', len(cats['expense']), '收入分类数:', len(cats['income']))

r = client.get('/api/analytics/trend?dimension=month', headers=H)
print('趋势(月):', len(r.get_json()['data']), '个月')
r = client.get('/api/analytics/category-ratio?type=expense', headers=H)
print('分类占比:', len(r.get_json()['data']), '个分类')

print('\n=== 全部接口验证通过 ===')
print('登录账号: 13812345678 / 123456')
```


# 报税知识文档

### 📄 docbuild/个体户报税知识地基.md
```
# 个体户报税知识地基（非技术版）

> 用途：为「AI虚拟文员」产品做报税/税表功能前的必备知识梳理。
> 说明：本文基于公开税务信息整理，最终口径以当地税务局核定为准。建议找一位懂个体户报税的会计做终审。
> 整理日期：2026-08-07

---

## 一、个体户要交哪些税（四大块）

### 1. 增值税（按销售额）
- **小规模纳税人**：月销售额 ≤10万元（季度 ≤30万元）**免征**（政策到 2027-12-31）。
- 超过起征点：按 **1%** 征收率缴纳。
- 开了增值税专用发票的，即使没超起征点也要缴。

### 2. 个人所得税（经营所得）—— 核心税种
- 按 **5%～35% 五级超额累进税率**。
- 优惠：年应纳税所得额 ≤200万元部分，**减半征收**（2023-2027）。

### 3. 附加税费（跟着增值税走）
- 城市维护建设税（7%/5%/1%）、教育费附加（3%）、地方教育附加（2%）。
- 小规模纳税人最高享受 **50% 减征**。

### 4. 其他
- 印花税（合同、账簿）；有自有经营场所的还有房产税、城镇土地使用税。
- 个体户 **不缴企业所得税**，只缴经营所得个税。

---

## 二、申报时间表（做提醒功能的依据）

| 事项 | 周期 | 截止时间 |
|------|------|---------|
| 增值税 + 附加税费 | 月或季（小规模通常按季） | 期满之日起 **15日内** |
| 个税经营所得（预缴） | 季 | 季度终了后 **15日内**（1/4/7/10月） |
| 个税经营所得（年度汇算 B表） | 年 | 次年 **3月31日前** |
| 印花税 | 季/年/次 | 15日内 |
| **工商年报** | 年 | 每年 **1月1日～6月30日** |

> 关键：**不管有没有收入、要不要缴税，都要申报**。逾期按日加收滞纳金（0.05%），还影响纳税信用。

---

## 三、征收方式与建账要求（决定产品做多重的账）

### 征收方式两种
- **核定征收**：税务局按面积/地段/行业定一个应税额，简单但逐步收紧。
- **查账征收**：按真实收入-成本算税，**需要规范记账**。近年主流趋势，必须做账。

### 建账标准（查账征收）
| 情形 | 应建账 |
|------|--------|
| 注册资金 ≥20万 或 月销售 ≥4万（应税劳务）/6万（生产）/8万（批零） | **复式账** |
| 注册资金 10万～20万 或 月销售 1.5万～4万 | **简易账** |
| 达不到上述标准 | 收支凭证粘贴簿 + 进货销货登记簿 |

### 简易账要记什么（这是产品的机会）
简易账需要：**经营收入账、经营费用账、商品（材料）购进账、库存商品盘点表、利润表**。

> 这几乎就是「AI虚拟文员」现有功能（收入/支出/分类/供应商）能覆盖的范围——**你的记账功能天然就是简易账的数字化**。

### 其他要求
- 达到标准须在领照或发生纳税义务后 **15日内** 建账。
- 账簿凭证保存 **10年**。
- 查账征收建议**单独经营账户**，公私分开。

---

## 四、报税流程与税表（产品要生成的交付物）

### 登录渠道
自然人电子税务局（WEB端 https://etax.chinatax.gov.cn 或 个人所得税APP）。

### 三张表
| 表 | 用途 | 时间 |
|----|------|------|
| **A表** | 季度预缴申报 | 季终后15日内 |
| **B表** | 年度汇算清缴 | 次年3月31日前 |
| **C表** | 多处经营汇总申报 | 次年3月31日前 |

### A表（预缴）流程
登录 → 我要办税 → 经营所得(A表) → 选年度 → 录统一社会信用代码 → 据实预缴 → 录收入总额、成本费用 → 提交。

### B表（年度汇算）流程
登录 → 我要办税 → 经营所得(B表) → 录收入成本 → 录纳税调整 → 录减免事项（专项扣除等）→ 提交 → 缴税/无需缴税。

### 关键优惠（系统自动认定）
- 年应纳税所得额 ≤200万，个税**减半**，无需手动填报。

---

## 五、对产品设计的启示（初步）

1. **现有记账功能 = 简易账数字化**。收入/支出/分类/供应商/日期，正好构成简易账所需字段。这是最扎实的地基。

2. **税表生成 = 把账本数字，按规则映射到 A/B 表字段**。核心逻辑是"收入总额、成本费用、应纳税所得额"的归集与计算，规则确定后是确定性计算，不是 AI 猜测。

3. **报税提醒 = 按二的时间表做倒计时**。技术简单，价值直接（避开逾期罚款）。

4. **流程教学 = 把四的操作流程做成图文/视频**。这是差异化卖点，也最需要你（或懂行的人）产出内容。

5. **风险点**：税表算错 → 客户被罚 → 口碑崩塌。所以**规则必须经懂税的人终审**，产品内必须加免责声明与核对引导。

---

## 六、待办（你需要推动的事）

- [ ] 找到一位懂个体户报税的会计/代办，做规则终审
- [ ] 确认目标客户所在地区（税率/政策以当地为准）
- [ ] 确认目标客户多数是查账征收还是核定征收（决定做账深度）
- [ ] 收集 2-3 家真实小店的 3 个月账目样本，用于验证税表逻辑
```

