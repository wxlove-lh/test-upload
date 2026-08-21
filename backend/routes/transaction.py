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
        'customer_name': t.customer_name,
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
    customer_name = (args.get('customer_name') or '').strip()

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if category:
        query = query.filter_by(category=category)
    if tx_type:
        query = query.filter_by(type=tx_type)
    if customer_name:
        query = query.filter(Transaction.customer_name == customer_name)

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
            customer_name=(data.get('customer_name') or '').strip() or None,
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
            'customer_name': 'customer_name',
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
