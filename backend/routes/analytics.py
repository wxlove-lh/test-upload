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


@analytics_bp.route('/category-summary', methods=['GET'])
@jwt_required()
def category_summary():
    """按分类汇总：每个分类的收入/支出/结余（默认本月）"""
    user_id = get_jwt_identity()

    today = date.today()
    default_start = today.replace(day=1)
    default_end = today

    start_date = _parse_date(request.args.get('start_date'), default_start)
    end_date = _parse_date(request.args.get('end_date'), default_end)

    rows = _base_query(user_id, start_date, end_date).with_entities(
        Transaction.category,
        Transaction.type,
        func.sum(Transaction.amount).label('amount'),
    ).group_by(Transaction.category, Transaction.type).all()

    by_category = {}
    for row in rows:
        cat = row.category or '未分类'
        entry = by_category.setdefault(cat, {'category': cat, 'income': 0.0, 'expense': 0.0})
        amount = float(row.amount or 0)
        if row.type == 'income':
            entry['income'] = round(entry['income'] + amount, 2)
        else:
            entry['expense'] = round(entry['expense'] + amount, 2)

    categories = []
    for cat, entry in by_category.items():
        entry['net'] = round(entry['income'] - entry['expense'], 2)
        entry['total'] = round(entry['income'] + entry['expense'], 2)
        categories.append(entry)

    # 按金额大小排序
    categories.sort(key=lambda x: -x['total'])

    totals = {
        'income': round(sum(c['income'] for c in categories), 2),
        'expense': round(sum(c['expense'] for c in categories), 2),
    }
    totals['profit'] = round(totals['income'] - totals['expense'], 2)

    return jsonify({
        'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
        'categories': categories,
        'totals': totals,
    })


@analytics_bp.route('/quarterly', methods=['GET'])
@jwt_required()
def quarterly():
    """按季度汇总：指定年份四个季度的收入/支出/利润（默认今年）"""
    user_id = get_jwt_identity()

    today = date.today()
    year = request.args.get('year', type=int)
    if not year:
        year = today.year

    def quarter_bounds(y, q):
        q_start_month = (q - 1) * 3 + 1
        q_end_month = q_start_month + 2
        start = date(y, q_start_month, 1)
        if q_end_month == 12:
            end = date(y, 12, 31)
        else:
            end = date(y, q_end_month + 1, 1) - timedelta(days=1)
        return start, end

    quarters = []
    for q in range(1, 5):
        start, end = quarter_bounds(year, q)
        row = _base_query(user_id, start, end).with_entities(
            func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
            func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense'),
        ).first()

        income = float(row.income or 0)
        expense = float(row.expense or 0)
        quarters.append({
            'quarter': q,
            'label': f'{year}年第{q}季度',
            'months': f'{q * 3 - 2}~{q * 3}月',
            'income': round(income, 2),
            'expense': round(expense, 2),
            'profit': round(income - expense, 2),
        })

    year_totals = {
        'income': round(sum(x['income'] for x in quarters), 2),
        'expense': round(sum(x['expense'] for x in quarters), 2),
    }
    year_totals['profit'] = round(year_totals['income'] - year_totals['expense'], 2)

    return jsonify({
        'year': year,
        'quarters': quarters,
        'totals': year_totals,
    })
