"""报税底稿生成服务

把用户的账目数据按时间范围自动归类整理成一份"报税底稿"。
底稿的目的：帮客户把零散账目整理成合规、清晰的报表结构，供客户报税时参考，
不代替专业税务申报。所有税负均为估算参考，最终以税务机关核定为准。

税务规则依据（面向餐饮小店/个体工商户，小规模纳税人）：
- 增值税：小规模纳税人征收率 1%（现行优惠），按月申报月销售额≤10万、
  按季申报季销售额≤30万免征增值税（含未开票收入）；
- 附加税费：城建税7% + 教育费附加3% + 地方教育附加2%，小规模纳税人减半征收，
  随增值税免征而免征；
- 个税（经营所得）：5%~35% 五级超额累进税率，年应纳税所得额不超过200万元的部分
  减半征收（2023-2027年政策）；这里用"本年度累计利润"作简化估算，
  未扣除业主费用6万元/年、专项附加扣除等，实际以税务机关核定为准；
- 个体户不交企业所得税。
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func
from extensions import db
from models.transaction import Transaction

# 支出分类 → 成本 or 费用
# 成本：直接构成销售货品的支出（含老板可能自建的同义分类关键词）
COST_CATEGORIES = {
    '食材', '酒水饮料', '原材料', '烟酒', '农产品', '肉类', '蔬菜', '水产',
    '进货', '购进', '原料', '调料', '冻品', '海鲜', '水果', '粮油', '米面',
}
# 费用：经营期间的其他开支
EXPENSE_CATEGORIES = {
    '房租', '水电燃气', '工资', '耗材餐具', '交通', '通讯', '网络', '广告',
    '包装', '设备', '维修', '设备维修', '运输配送', '保险', '税费', '税费管理', '其他', '其他支出', '日用杂货',
}

# 经营所得个税：五级超额累进税率表（年应纳税所得额 → 税率、速算扣除数）
INCOME_TAX_BRACKETS = [
    (30000, 0.05, 0),
    (90000, 0.10, 1500),
    (300000, 0.20, 10500),
    (500000, 0.30, 40500),
    (float('inf'), 0.35, 65500),
]

VAT_EXEMPT_QUARTER = 300000.0   # 按季免征额度
VAT_EXEMPT_MONTH = 100000.0     # 按月免征额度
VAT_RATE = 0.01                 # 小规模征收率1%
SURCHARGE_RATE = 0.06           # 附加税费≈增值税×6%（城建7%+教育3%+地方教育2%减半）
INCOME_TAX_HALF_LIMIT = 2000000.0  # 年应纳税所得额≤200万部分减半

DISCLAIMER = (
    '本底稿仅为账目整理参考，不代替税务申报。'
    '所有税额均为简化估算，请以最新税收政策及税务机关核定为准。'
)

# 以下规则"待核实"清单：凡不能100%确定的口径，一律列在这里并在结果中标注，
# 不当作确定事实展示给老板。
PENDING_VERIFICATION = [
    {
        'item': '附加税费税率',
        'note': '城建税7%/5%/1%按纳税地点分档，教育费附加3%、地方教育附加2%各省可能不同；'
               '小规模纳税人减半征收为现行阶段性优惠。本工具暂按(7%+3%+2%)÷2=6%简化估算，'
               '请以当地税务机关核定为准。',
    },
    {
        'item': '增值税免征额度与1%征收率',
        'note': '月10万/季30万免征、3%减按1%征收均为现行阶段性优惠（执行至2027年底），'
               '到期后可能调整；开专票的收入不享受免征。请以最新政策公告为准。',
    },
    {
        'item': '经营所得200万减半优惠',
        'note': '年应纳税所得额不超过200万元部分减半，为现行阶段性优惠；'
               '是否适用、核定征收还是查账征收，以税务机关核定为准。',
    },
    {
        'item': '申报方式（按月/按季）',
        'note': '多数小规模纳税人按季申报，但以税务登记时核定为准；'
               '本工具默认按季口径估算。',
    },
    {
        'item': '申报截止日期',
        'note': '按"期终15日内"通用规则计算，遇节假日可能顺延，以税务机关当月公告为准。',
    },
]


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
        end = date(year, month + 1, 1) - timedelta(days=1)
        end = end.isoformat()
    return start, end


def _quarter_range(year, quarter):
    """返回某季度的起止日期字符串"""
    q_start_month = (quarter - 1) * 3 + 1
    q_end_month = q_start_month + 2
    start = f'{year}-{q_start_month:02d}-01'
    if q_end_month == 12:
        end = f'{year}-12-31'
    else:
        end = date(year, q_end_month + 1, 1) - timedelta(days=1)
        end = end.isoformat()
    return start, end


def _default_range(kind='this-month'):
    """返回时间段。kind: this-month / last-month / this-quarter / last-quarter / this-year / all"""
    now = datetime.now()
    y, m = now.year, now.month

    if kind == 'this-month':
        return _month_range(y, m), f'{y}年{m}月'
    if kind == 'last-month':
        yy, mm = (y, m - 1) if m > 1 else (y - 1, 12)
        return _month_range(yy, mm), f'{yy}年{mm}月'
    if kind == 'this-quarter':
        q = (m - 1) // 3 + 1
        return _quarter_range(y, q), f'{y}年第{q}季度'
    if kind == 'last-quarter':
        q = (m - 1) // 3 + 1
        if q == 1:
            return _quarter_range(y - 1, 4), f'{y - 1}年第4季度'
        return _quarter_range(y, q - 1), f'{y}年第{q - 1}季度'
    if kind == 'this-year':
        return f'{y}-01-01', f'{y}-12-31', f'{y}年全年'
    # all：返回一个很宽的范围
    return '2000-01-01', '2100-12-31', '全部账目'


def _period_label(start_date, end_date):
    """根据起止日期给出展示标签（用于自定义时间段）"""
    return f'{start_date} ~ {end_date}'


def _calc_income_tax(taxable_income):
    """按五级超额累进税率计算经营所得个税（简化估算）"""
    taxable = max(float(taxable_income or 0), 0)
    tax = 0.0
    for limit, rate, deduct in INCOME_TAX_BRACKETS:
        if taxable <= limit:
            tax = taxable * rate - deduct
            break
    tax = max(tax, 0)
    halved = taxable <= INCOME_TAX_HALF_LIMIT
    if halved:
        tax = round(tax / 2, 2)
    return round(tax, 2), halved


def _query_txns(user_id, start_date, end_date):
    """查询该时间段内的有效交易"""
    return Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.status.in_(['confirmed', 'modified']),
        Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
        Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date(),
    ).all()


def generate_tax_draft(user_id, start_date=None, end_date=None, kind='this-month', use_ai=False):
    """生成报税底稿。

    Args:
        user_id: 用户ID
        start_date / end_date: 指定时间段 YYYY-MM-DD（可选）
        kind: this-month / last-month / this-quarter / last-quarter / this-year / all
        use_ai: 是否调用 DeepSeek 生成通俗解读（未配Key或失败时自动回退规则版）

    Returns:
        底稿字典，含期间、汇总、明细归类、税负估算、免责声明（可选AI解读）
    """
    label = None
    if not start_date or not end_date:
        (start_date, end_date), label = _default_range(kind)
    else:
        label = _period_label(start_date, end_date)

    txns = _query_txns(user_id, start_date, end_date)

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
            cat_name = t.category or '未分类'
            if grp == 'cost':
                total_cost += amount
                cost_by_category[cat_name] = _fmt(cost_by_category.get(cat_name, 0) + amount)
            else:
                total_expense += amount
                expense_by_category[cat_name] = _fmt(expense_by_category.get(cat_name, 0) + amount)

    total_profit = total_income - total_cost - total_expense

    # ── 增值税（小规模纳税人，按季口径估算） ──
    vat_exempt = total_income <= VAT_EXEMPT_QUARTER
    vat = 0.0 if vat_exempt else round(total_income * VAT_RATE, 2)
    surcharge = 0.0 if vat == 0 else round(vat * SURCHARGE_RATE, 2)

    # ── 经营所得个税（本年度累计利润口径） ──
    # 从当年1月1日到期间结束，作为"本年度累计利润"的估算基础
    period_end = datetime.strptime(end_date, '%Y-%m-%d').date()
    ytd_start = f'{period_end.year}-01-01'
    ytd_txns = _query_txns(user_id, ytd_start, end_date)
    ytd_profit = 0.0
    for t in ytd_txns:
        amount = float(t.amount or 0)
        if t.type == 'income':
            ytd_profit += amount
        else:
            ytd_profit -= amount

    income_tax, income_tax_halved = _calc_income_tax(ytd_profit)

    total_tax = round(vat + surcharge + income_tax, 2)

    draft = {
        'period': {
            'start': start_date,
            'end': end_date,
            'label': label,
            'kind': kind,
        },
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
            'vat_rule': '小规模纳税人：季度收入30万以内免征（现行阶段性优惠），超过部分按1%估算',
            'vat_exempt': vat_exempt,
            'vat': vat,
            'vat_rate': VAT_RATE,
            'surcharge': surcharge,
            'surcharge_note': '附加税费按增值税×6%简化估算（城建+教育附加+地方教育附加减半，具体税率待核实）',
            'income_tax': income_tax,
            'income_tax_halved': income_tax_halved,
            'income_tax_note': '按本年度累计利润套5%~35%累进税率估算，年所得≤200万部分减半（优惠适用待核实）',
            'taxable_income_ytd': _fmt(ytd_profit),
            'total_tax': total_tax,
            'note': '以上税负为简化估算，仅作整理参考，请以最新税收政策及税务机关核定为准。',
        },
        'pending_verification': PENDING_VERIFICATION,
        'disclaimer': DISCLAIMER,
        'ai_notes': _interpret(draft_summary={
            'label': label,
            'income': _fmt(total_income),
            'cost': _fmt(total_cost),
            'expense': _fmt(total_expense),
            'profit': _fmt(total_profit),
            'vat': vat,
            'vat_exempt': vat_exempt,
            'surcharge': surcharge,
            'income_tax': income_tax,
            'income_tax_halved': income_tax_halved,
            'total_tax': total_tax,
        }, use_ai=use_ai),
    }
    return draft


def _rule_based_notes(s: dict):
    """没有AI时的固定解读文案（口语化、面向老板）"""
    lines = []
    lines.append(f"这份{s['label']}底稿里：收入 ¥{_fmt(s['income'])}，成本 ¥{_fmt(s['cost'])}，费用 ¥{_fmt(s['expense'])}，利润 ¥{_fmt(s['profit'])}。")
    if s['vat_exempt']:
        lines.append("增值税：季度收入在30万以内，按现行政策免征，正常申报就行。")
    else:
        lines.append(f"增值税：本季度收入超过30万免征线，按1%估算约 ¥{_fmt(s['vat'])}，附加税费约 ¥{_fmt(s['surcharge'])}。")
    if s['income_tax_halved']:
        lines.append(f"经营所得个税：估算约 ¥{_fmt(s['income_tax'])}（已按年所得200万以内减半的优惠估算）。")
    else:
        lines.append(f"经营所得个税：估算约 ¥{_fmt(s['income_tax'])}。")
    lines.append("提醒：不管有没有收入都要按时申报；小票和账目请留好备查。以上是估算，最终以税务机关核定为准。")
    return lines


def _interpret(draft_summary: dict, use_ai: bool) -> dict:
    """可选AI解读：成功返回AI生成的通俗解读；否则回退规则文案"""
    if not use_ai:
        return {'available': False, 'used': False, 'items': _rule_based_notes(draft_summary)}

    try:
        from services.deepseek_service import DeepSeekService
        service = DeepSeekService()
        if not service.available:
            return {'available': False, 'used': False, 'items': _rule_based_notes(draft_summary)}

        prompt = (
            "你是一位帮餐饮小店老板看账的税务助手。下面是一份报税底稿的汇总数字"
            "（个体户/小规模纳税人）：\n"
            f"期间：{draft_summary['label']}\n"
            f"营业收入：{draft_summary['income']} 元\n"
            f"营业成本：{draft_summary['cost']} 元\n"
            f"期间费用：{draft_summary['expense']} 元\n"
            f"利润：{draft_summary['profit']} 元\n"
            f"增值税估算：{draft_summary['vat']} 元（{'季度收入30万以内免征' if draft_summary['vat_exempt'] else '超过30万按1%估算'}）\n"
            f"附加税费估算：{draft_summary['surcharge']} 元\n"
            f"经营所得个税估算：{draft_summary['income_tax']} 元（{'已按年所得≤200万减半估算' if draft_summary['income_tax_halved'] else ''}）\n"
            f"合计估算税额：{draft_summary['total_tax']} 元\n\n"
            "请用3~5句通俗的大白话（每句不超过40字，面向不懂财税的小店老板），"
            "说明：1) 这份账目健康吗；2) 大概要交多少税；3) 接下来该做什么。"
            "不要使用表格和标题，每句一行，不要有任何免责声明长句以外的废话。"
            "结尾固定加一句：以上为估算参考，以税务机关核定为准。"
        )
        text = service.chat_text(prompt)
        items = [line.strip(' -•·') for line in text.splitlines() if line.strip()]
        if not items:
            raise ValueError('AI返回为空')
        return {'available': True, 'used': True, 'items': items[:6]}
    except Exception:
        return {'available': False, 'used': False, 'items': _rule_based_notes(draft_summary)}


# ─────────────────────────────────────────────────────────────
# 报税日历：真实申报时间表 + 倒计时
# ─────────────────────────────────────────────────────────────

def _next_deadline(today, year, month, day):
    """某年某月某日的截止时间；若已过则顺延到明年"""
    d = date(year, month, day)
    if d < today:
        d = date(year + 1, month, day)
    return d


def _days_left(today, deadline):
    """距离截止还有多少天（负数=已逾期）"""
    return (deadline - today).days


def _status_of(days_left, within_window=False):
    if days_left < 0:
        return 'overdue'
    if within_window:
        return 'open'          # 正在办理期内（如工商年报窗口）
    if days_left <= 3:
        return 'urgent'        # 3天内到期
    if days_left <= 7:
        return 'soon'          # 7天内到期
    return 'normal'


def build_tax_calendar(today=None):
    """按真实申报时间表生成最近的申报安排（含倒计时天数）。

    规则（个体工商户/小规模纳税人）：
    - 增值税：按季申报，季度终了后15日内（次月15日截止）；
    - 经营所得个税预缴：季度终了后15日内（1/4/7/10月15日截止）；
    - 经营所得个税年度汇算：次年3月31日前；
    - 工商年报：每年1月1日至6月30日；
    - 按月申报的增值税：月度终了后15日内（每月15日截止）。
    所有日期以税务机关公告为准（遇节假日可能顺延）。
    """
    today = today or date.today()
    y, m = today.year, today.month

    items = []

    # 1) 增值税及附加（按季）：下一申报截止日
    #    季度申报截止月：Q1→4月、Q2→7月、Q3→10月、Q4→次年1月
    deadline_month = [4, 7, 10, 1]
    q_of_month = (m - 1) // 3 + 1
    # 当前所处季度 Q：其申报截止月 = deadline_month[Q-1]
    cur_q_deadline_month = deadline_month[q_of_month - 1]
    cur_q_deadline_year = y if cur_q_deadline_month != 1 else y + 1
    cur_q_deadline = date(cur_q_deadline_year, cur_q_deadline_month, 15)

    if cur_q_deadline >= today:
        # 下一截止就是本季度申报
        deadline = cur_q_deadline
        q, qy = q_of_month, y
    else:
        # 本季度截止已过 → 看下一季度
        next_q = q_of_month + 1 if q_of_month < 4 else 1
        next_q_year = y if q_of_month < 4 else y + 1
        deadline = date(next_q_year, deadline_month[next_q - 1], 15)
        q, qy = next_q, next_q_year

    q_start_month = (q - 1) * 3 + 1
    scope = f'{qy}年第{q}季度（{q_start_month}~{q_start_month + 2}月）'
    dl = _days_left(today, deadline)
    items.append({
        'key': 'vat-quarter',
        'label': '增值税及附加申报（按季）',
        'scope': scope,
        'deadline': deadline.isoformat(),
        'days_left': dl,
        'status': _status_of(dl),
        'note': '季度收入30万以内免征，不管有没有收入都要申报',
    })

    # 2) 经营所得个税预缴（按季）：截止月 1/4/7/10 月15日
    #    下一截止：从今天起最近的 1/4/7/10 月15日
    predeadline = None
    for month in [1, 4, 7, 10]:
        d = _next_deadline(today, y, month, 15)
        if predeadline is None or d < predeadline:
            predeadline = d
    # 所属期：该截止日申报的是上一季度
    p_q = ((predeadline.month - 4) // 3 + 1) if predeadline.month in (4, 7, 10) else 4
    p_qy = predeadline.year if predeadline.month != 1 else predeadline.year - 1
    p_scope_start = (p_q - 1) * 3 + 1
    p_scope = f'{p_qy}年第{p_q}季度（{p_scope_start}~{p_scope_start + 2}月）'
    p_dl = _days_left(today, predeadline)
    items.append({
        'key': 'income-tax-quarter',
        'label': '经营所得个税预缴（按季）',
        'scope': p_scope,
        'deadline': predeadline.isoformat(),
        'days_left': p_dl,
        'status': _status_of(p_dl),
        'note': '填A表季度预缴，数字按账本利润估算',
    })

    # 3) 按月申报的增值税：每月15日截止（申报上月）
    month_deadline = date(y, m, 15)
    if month_deadline < today:
        if m == 12:
            month_deadline = date(y + 1, 1, 15)
        else:
            month_deadline = date(y, m + 1, 15)
    # 所属期 = 截止月的前一个月
    scope_m = month_deadline.month - 1
    scope_y = month_deadline.year if scope_m >= 1 else month_deadline.year - 1
    scope_m = scope_m if scope_m >= 1 else 12
    m_dl = _days_left(today, month_deadline)
    items.append({
        'key': 'vat-monthly',
        'label': '增值税申报（按月，如您按月申报）',
        'scope': f'{scope_y}年{scope_m}月',
        'deadline': month_deadline.isoformat(),
        'days_left': m_dl,
        'status': _status_of(m_dl),
        'note': '月收入10万以内免征；多数小规模纳税人按季申报，以税务登记为准',
    })

    # 4) 个税年度汇算清缴（B表）：次年3月31日前
    annual_deadline = _next_deadline(today, y, 3, 31)
    annual_scope_y = annual_deadline.year - 1
    a_dl = _days_left(today, annual_deadline)
    items.append({
        'key': 'annual-settlement',
        'label': '经营所得个税年度汇算清缴（B表）',
        'scope': f'{annual_scope_y}年度',
        'deadline': annual_deadline.isoformat(),
        'days_left': a_dl,
        'status': _status_of(a_dl),
        'note': '把全年账目与预缴数字对一遍，多退少补',
    })

    # 5) 工商年报：每年1月1日 ~ 6月30日
    if today <= date(y, 6, 30):
        report_deadline = date(y, 6, 30)
        report_scope = f'{y}年度'
        within_window = today >= date(y, 1, 1)
    else:
        report_deadline = date(y + 1, 6, 30)
        report_scope = f'{y}年度（次年{y + 1}年1月1日开放）'
        within_window = False
    r_dl = _days_left(today, report_deadline)
    items.append({
        'key': 'annual-report',
        'label': '工商年报（企业信用信息公示）',
        'scope': report_scope,
        'deadline': report_deadline.isoformat(),
        'days_left': r_dl,
        'status': _status_of(r_dl, within_window=within_window),
        'note': '每年1月1日至6月30日网上填报，不按时报会被列入异常名录',
    })

    # 按截止日期排序
    items.sort(key=lambda x: x['deadline'])

    return {
        'today': today.isoformat(),
        'items': items,
        'tips': [
            '不管有没有收入都要按时申报，逾期按日加收滞纳金（税款×0.05%/日）。',
            '申报截止日遇节假日可能顺延，以税务机关公告为准。',
            '建议提前3~5天把账目整理好，生成报税底稿对照填表。',
        ],
        'disclaimer': '以上日期为通用规则整理，最终以税务机关通知为准。',
        'pending_verification': [
            {
                'item': '申报方式与截止日期',
                'note': '按月还是按季申报，以税务登记时核定为准；截止日期遇节假日可能顺延，'
                       '请以当地税务机关当月公告为准。',
            },
        ],
    }
