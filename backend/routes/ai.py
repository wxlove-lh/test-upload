import logging
from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from services.comparison import ComparisonService
from services.tax_service import generate_tax_draft, build_tax_calendar
from services.deepseek_service import DeepSeekService
from models.user import User
from models.transaction import Transaction
from extensions import db

logger = logging.getLogger(__name__)

# 注意：url_prefix在app.py中注册时已指定为'/api/ai'，这里不再重复设置
ai_bp = Blueprint('ai', __name__)

# 涉及税务的提问关键词：命中后AI回复自动附上"以税务机关核定为准"免责提示
TAX_KEYWORDS = ['税', '报税', '申报', '缴税', '汇算', '年报', '发票', '免征', '纳税']
TAX_DISCLAIMER = '\n（以上为参考，不代替专业申报，请以税务机关核定为准。）'

AI_CHAT_SYSTEM_PROMPT = (
    '你是「AI虚拟文员」，帮餐饮小店老板记账、查账、报税的数字助手。'
    '说话像店里的老会计：口语化、简短、实在，多用大白话，别拽专业词。'
    '你手里有老板的真实账目数据（会随对话提供），回答要结合这些数字，不要凭空编数。'
    '涉及税务的问题要保守：只说政策和估算参考，明确提醒以税务机关核定为准，'
    '绝不承诺"包过""不交税"，也不代替报税。'
    '如果数据不足以回答，就如实说"账上还没有这个数据"。'
    '回答控制在 5 句话以内，条理清楚。'
)

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
        # RuntimeError 里已经带上了人能听懂的失败原因（缺Key/模型不支持图片/网络/余额）
        logger.error("AI识别服务异常，用户ID: %s, 错误: %s", user_id, str(e))
        return jsonify({"message": str(e)}), 503
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
      - kind：this-month / last-month / this-quarter / last-quarter / this-year / all
      - use_ai：1/true 时调用 DeepSeek 生成通俗解读（未配Key自动回退规则版）
    """
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    kind = request.args.get('kind', 'this-month')
    use_ai = (request.args.get('use_ai') or '').lower() in ('1', 'true', 'yes')

    try:
        draft = generate_tax_draft(
            user_id,
            start_date=start_date,
            end_date=end_date,
            kind=kind,
            use_ai=use_ai,
        )
        return jsonify(draft), 200
    except Exception as e:
        logger.error("生成报税底稿失败，用户ID: %s, 错误: %s", user_id, str(e), exc_info=True)
        return jsonify({"message": "生成报税底稿失败，请稍后重试"}), 500


# 功能界面 → 老板能看懂的名字（喂给AI，让它知道老板正待在哪个界面）
FEATURE_LABELS = {
    'ai-chat': '跟AI商量',
    'ai-bookkeeping': 'AI识别记账',
    'inquiry': '查账',
    'report': '报表',
    'export': '导出Excel',
    'customers': '客户台账',
    'customers-unlimited': '客户台账',
    'ledger-detail': '收支详细账本',
    'tax-reminder': '报税日期提醒',
    'tax-draft': '报税底稿',
    'categories': '收支分类',
    'tax-tutorial': '报税流程教程',
}


def _period_summary(user_id, start, end):
    """某时间段的收入/支出/利润/笔数"""
    base = [
        Transaction.user_id == user_id,
        Transaction.status.in_(['confirmed', 'modified']),
    ]
    income = db.session.query(func.sum(Transaction.amount)).filter(
        *base, Transaction.type == 'income',
        Transaction.transaction_date >= start, Transaction.transaction_date <= end,
    ).scalar() or 0
    expense = db.session.query(func.sum(Transaction.amount)).filter(
        *base, Transaction.type == 'expense',
        Transaction.transaction_date >= start, Transaction.transaction_date <= end,
    ).scalar() or 0
    count = Transaction.query.filter(
        *base,
        Transaction.transaction_date >= start, Transaction.transaction_date <= end,
    ).count()
    return float(income), float(expense), count


def _feature_context(user_id, feature):
    """按当前界面补充相关内容：客户台账→客户列表；报税底稿→底稿数字等"""
    lines = []
    label = FEATURE_LABELS.get(feature or '')
    if label:
        lines.append(f'老板现在正在「{label}」界面里，请优先结合这个界面的内容来回答。')

    try:
        if feature in ('customers', 'customers-unlimited'):
            from routes.customer import _customer_stats
            from models.customer import Customer
            customers = Customer.query.filter_by(user_id=user_id).order_by(
                Customer.updated_at.desc()
            ).limit(20).all()
            if customers:
                lines.append('老板的客户台账（含往来账和习惯备注）：')
                for c in customers:
                    stats = _customer_stats(user_id, c.name)
                    parts = [c.name]
                    if c.tag:
                        parts.append(c.tag)
                    if c.phone:
                        parts.append('电话' + c.phone)
                    if stats['tx_count'] > 0:
                        parts.append(
                            f'累计 {stats["total_amount"]:.2f} 元 / {stats["tx_count"]} 笔'
                            f'/ 最近 {stats["last_date"]}'
                        )
                    if c.notes:
                        parts.append('习惯备注：' + str(c.notes)[:30])
                    lines.append('- ' + '，'.join(parts))
            else:
                lines.append('老板的客户台账里还没有客户。')

        elif feature == 'tax-draft':
            draft = generate_tax_draft(user_id, kind='this-quarter')
            s = draft['summary']
            t = draft['tax_estimate']
            lines.append('本季度报税底稿：')
            lines.append(
                f'- 收入 {s["total_income"]:.2f} 元，成本 {s["total_cost"]:.2f} 元，'
                f'费用 {s["total_expense"]:.2f} 元，利润 {s["total_profit"]:.2f} 元'
            )
            lines.append(
                f'- 增值税估算 {t["vat"]:.2f} 元（{"季度收入30万以内免征" if t["vat_exempt"] else "按1%征收"}），'
                f'附加税费 {t["surcharge"]:.2f} 元，经营所得个税估算 {t["income_tax"]:.2f} 元'
            )

        elif feature == 'tax-reminder':
            cal = build_tax_calendar()
            lines.append('最近的申报安排：')
            for item in cal.get('items', [])[:5]:
                lines.append(
                    f'- {item["label"]}（{item["scope"]}），截止 {item["deadline"]}，剩 {item["days_left"]} 天'
                )

        elif feature == 'categories':
            from models.category import Category
            cats = Category.query.filter(
                db.or_(Category.user_id.is_(None), Category.user_id == user_id)
            ).order_by(Category.type, Category.sort_order).all()
            exp = [c.name for c in cats if c.type == 'expense']
            inc = [c.name for c in cats if c.type == 'income']
            lines.append('老板的支出分类：' + '、'.join(exp))
            lines.append('老板的收入分类：' + '、'.join(inc))

        elif feature == 'report':
            today = date.today()
            income, expense, count = _period_summary(user_id, today.replace(day=1), today)
            lines.append(
                f'本月至今：收入 {income:.2f} 元，支出 {expense:.2f} 元，'
                f'利润 {income - expense:.2f} 元，共 {count} 笔。'
            )
    except Exception as e:
        logger.warning("生成界面上下文失败: %s", str(e))

    return '\n'.join(lines)


def _build_chat_context(user_id: int, feature: str = '', history: list = None) -> str:
    """为AI对话准备上下文：当前界面内容 + 本月汇总 + 最近账目 + 报税安排 + 最近聊天记录"""
    today = date.today()
    month_start = today.replace(day=1)

    # 本月汇总
    income, expense, _ = _period_summary(user_id, month_start, today)

    # 最近5笔账
    base_filter = [
        Transaction.user_id == user_id,
        Transaction.status.in_(['confirmed', 'modified']),
    ]
    recent = Transaction.query.filter(*base_filter).order_by(
        Transaction.transaction_date.desc(), Transaction.id.desc()
    ).limit(5).all()

    # 最近报税安排（前3项）
    calendar = build_tax_calendar(today)
    next_deadlines = calendar.get('items', [])[:3]

    lines = [f'今天是{today.year}年{today.month}月{today.day}日。']
    lines.append(f'本月至今：收入 {income:.2f} 元，支出 {expense:.2f} 元，利润 {income - expense:.2f} 元。')

    if recent:
        lines.append('最近几笔账：')
        for t in recent:
            kind = '收入' if t.type == 'income' else '支出'
            parts = [str(t.transaction_date), kind, f'{float(t.amount or 0):.2f}元']
            if t.category:
                parts.append(t.category)
            if t.supplier:
                parts.append(t.supplier)
            if t.notes:
                parts.append(str(t.notes)[:20])
            lines.append('- ' + '，'.join(parts))
    else:
        lines.append('目前账上还没有记账记录。')

    if next_deadlines:
        lines.append('最近的报税安排：')
        for item in next_deadlines:
            lines.append(f'- {item["label"]}（{item["scope"]}），截止 {item["deadline"]}')

    # 客户往来速览：让AI在任何界面都能回答"张老板欠多少/最近来没来"
    try:
        from routes.customer import _customer_stats
        from models.customer import Customer
        customers = Customer.query.filter_by(user_id=user_id).order_by(
            Customer.updated_at.desc()
        ).limit(10).all()
        if customers:
            lines.append('客户往来速览：')
            for c in customers:
                st = _customer_stats(user_id, c.name)
                parts = [c.name]
                if c.tag:
                    parts.append(c.tag)
                if st['tx_count'] > 0:
                    parts.append(f'累计{st["total_amount"]:.2f}元/{st["tx_count"]}笔/最近{st["last_date"]}')
                if c.notes:
                    parts.append('习惯:' + str(c.notes)[:20])
                lines.append('- ' + '，'.join(parts))
    except Exception as e:
        logger.warning("客户速览生成失败: %s", str(e))

    # 当前界面的内容
    feature_text = _feature_context(user_id, feature)
    if feature_text:
        lines.append('')
        lines.append(feature_text)

    # 本对话框最近的聊天记录（AI有记忆，能接着商量）
    if history:
        lines.append('')
        lines.append('这个对话框里刚才聊过：')
        for h in history[-10:]:
            role = h.get('role')
            content = str(h.get('content') or '').strip()[:200]
            if not content:
                continue
            lines.append(f'- {role}：{content}')

    return '\n'.join(lines)


def _fallback_answer(message: str, user_id: int, feature: str = '') -> str:
    """未配DeepSeek Key时的规则版回答：按当前界面 + 常见查账意图，给出真实数字"""
    today = date.today()

    # 先按当前界面给确定性答案
    try:
        if feature in ('customers', 'customers-unlimited'):
            from routes.customer import _customer_stats
            from models.customer import Customer
            customers = Customer.query.filter_by(user_id=user_id).order_by(
                Customer.updated_at.desc()
            ).limit(20).all()
            if not customers:
                return '客户台账里还没有客户，点上面的「新增客户」加上第一位吧。'
            lines = []
            for c in customers[:10]:
                st = _customer_stats(user_id, c.name)
                parts = [c.name]
                if c.tag:
                    parts.append(c.tag)
                if st['tx_count'] > 0:
                    parts.append(f'累计{st["total_amount"]:.2f}元/{st["tx_count"]}笔/最近{st["last_date"]}')
                if c.notes:
                    parts.append('备注:' + str(c.notes)[:20])
                lines.append('、'.join(parts))
            answer = '您的客户（含往来账）：\n' + '\n'.join(lines)
            if len(customers) > 10:
                answer += f'\n……等共 {len(customers)} 位。'
            if '欠' in message or '赊' in message:
                answer += '\n欠款记在客户备注里，点对应客户可以查看和修改。'
            return answer

        if feature == 'tax-draft':
            draft = generate_tax_draft(user_id, kind='this-quarter')
            s = draft['summary']
            t = draft['tax_estimate']
            vat_text = '免征（季度收入30万以内）' if t['vat_exempt'] else f'{t["vat"]:.2f} 元（按1%估算）'
            return (
                f'本季度报税底稿：收入 {s["total_income"]:.2f} 元，成本 {s["total_cost"]:.2f} 元，'
                f'费用 {s["total_expense"]:.2f} 元，利润 {s["total_profit"]:.2f} 元。\n'
                f'增值税估算：{vat_text}；附加税费 {t["surcharge"]:.2f} 元；'
                f'经营所得个税估算 {t["income_tax"]:.2f} 元。'
            )

        if feature == 'tax-reminder':
            cal = build_tax_calendar(today)
            lines = ['最近的申报安排：']
            for item in cal.get('items', [])[:3]:
                lines.append(f'- {item["label"]}：截止 {item["deadline"]}（剩 {item["days_left"]} 天）')
            return '\n'.join(lines)

        if feature == 'categories':
            from models.category import Category
            cats = Category.query.filter(
                db.or_(Category.user_id.is_(None), Category.user_id == user_id)
            ).all()
            exp = [c.name for c in cats if c.type == 'expense']
            inc = [c.name for c in cats if c.type == 'income']
            return (
                f'支出分类（{len(exp)}个）：{"、".join(exp)}\n'
                f'收入分类（{len(inc)}个）：{"、".join(inc)}\n'
                '点「新增分类」可以加您自己的分类。'
            )
    except Exception as e:
        logger.warning("规则版界面回答失败: %s", str(e))

    # 通用查账意图：给时间段真实数字
    if '上月' in message or '上个月' in message:
        y, m = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
        start = date(y, m, 1)
        end = date(y, 12, 31) if m == 12 else date(y, m + 1, 1) - timedelta(days=1)
        label = f'{y}年{m}月'
    elif '今年' in message or '全年' in message:
        start, end, label = date(today.year, 1, 1), today, f'{today.year}年至今'
    elif '7天' in message or '最近' in message:
        start, end, label = today - timedelta(days=7), today, '最近7天'
    else:
        start, end, label = today.replace(day=1), today, f'{today.year}年{today.month}月'

    income, expense, count = _period_summary(user_id, start, end)
    looks_like_query = any(
        kw in message for kw in ('查', '看', '多少', '赚', '亏', '账', '报表', '收入', '支出', '利润', '明细')
    )

    if looks_like_query:
        answer = (
            f'{label}：收入 {income:.2f} 元，支出 {expense:.2f} 元，'
            f'利润 {income - expense:.2f} 元，共 {count} 笔账。'
        )
        if count == 0:
            answer += '\n这个时间段账上还没有记录，可以先记几笔。'
        return answer

    return (
        'AI 聊天需要配置 DeepSeek 密钥（在 backend/.env 里填 DEEPSEEK_API_KEY）。\n'
        '没配密钥也能用：左边的一键按钮可以查账、生成报表和报税底稿；'
        '也可以直接打字查账，比如「查这个月的账」。'
    )


@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    """自由对话：老板在任何界面的输入框直接跟AI商量。

    请求：{"message": "...", "feature": "tax-draft", "history": [{"role": "老板", "content": "..."}]}
    上下文包含：当前界面内容（客户台账/报税底稿/申报安排/分类等）+ 本月账目 +
    最近账目 + 本对话框聊天记录。
    响应：{"reply": "...", "used_ai": true/false}
    未配置 DeepSeek Key 时，查账类问题由规则版直接回答真实数字，其余给出提示。
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()

    if not message:
        return jsonify({"message": "请先输入您想问的内容"}), 400
    if len(message) > 500:
        return jsonify({"message": "一次说太多啦，请控制在500字以内"}), 400

    feature = str(data.get('feature') or '')
    history = data.get('history')
    if not isinstance(history, list):
        history = []

    is_tax_question = any(kw in message for kw in TAX_KEYWORDS)

    context = _build_chat_context(user_id, feature=feature, history=history)
    prompt = f"老板的真实账目和当前界面情况如下：\n{context}\n\n老板刚才问：{message}"

    try:
        service = DeepSeekService()
        if service.available:
            reply = service.chat_text(prompt)
            reply = (reply or '').strip()
            if not reply:
                raise RuntimeError('AI返回为空')
            if is_tax_question and '税务机关' not in reply:
                reply += TAX_DISCLAIMER
            return jsonify({'reply': reply, 'used_ai': True}), 200
    except Exception as e:
        logger.warning("AI对话失败（用户ID: %s）：%s", user_id, str(e))

    # 未配Key或调用失败：规则版回答（查账类给真实数字，其余提示配Key）
    fallback = _fallback_answer(message, user_id, feature=feature)
    if is_tax_question:
        fallback += TAX_DISCLAIMER
    return jsonify({'reply': fallback, 'used_ai': False}), 200
