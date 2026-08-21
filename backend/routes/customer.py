from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from extensions import db
from models.customer import Customer
from models.transaction import Transaction

customer_bp = Blueprint('customer', __name__)


def _customer_stats(user_id, name):
    """该客户的往来账统计：笔数、累计金额、最近一笔日期"""
    query = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.customer_name == name,
        Transaction.status.in_(['confirmed', 'modified']),
    )
    count = query.count()
    total = query.with_entities(func.sum(Transaction.amount)).scalar() or 0
    last_tx = query.order_by(Transaction.transaction_date.desc()).first()
    return {
        'tx_count': count,
        'total_amount': round(float(total), 2),
        'last_date': last_tx.transaction_date.isoformat() if last_tx else None,
    }


@customer_bp.route('', methods=['GET'])
@jwt_required()
def list_customers():
    """客户列表：支持 q 关键字搜索（姓名/电话/标签），附带每个客户的往来账统计"""
    user_id = get_jwt_identity()

    query = Customer.query.filter_by(user_id=user_id)

    q = (request.args.get('q') or '').strip()
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Customer.name.like(like),
                Customer.phone.like(like),
                Customer.tag.like(like),
                Customer.notes.like(like),
            )
        )

    customers = query.order_by(Customer.updated_at.desc(), Customer.id.desc()).all()

    items = []
    for c in customers:
        item = c.to_dict()
        item['stats'] = _customer_stats(user_id, c.name)
        items.append(item)

    return jsonify({
        'items': items,
        'total': len(items),
    })


@customer_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """新增客户：姓名必填，电话/标签/备注选填"""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': '请提供客户信息'}), 400

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': '客户称呼不能为空'}), 400
    if len(name) > 50:
        return jsonify({'error': '客户称呼太长（最多50字）'}), 400

    phone = (data.get('phone') or '').strip()
    if phone and len(phone) > 20:
        return jsonify({'error': '电话格式不对'}), 400

    tag = (data.get('tag') or '').strip()
    notes = (data.get('notes') or '').strip()

    # 同一个人（同名同电话）不重复建档
    duplicate = Customer.query.filter_by(user_id=user_id, name=name).first()
    if duplicate and (not phone or duplicate.phone == phone):
        return jsonify({'error': f'客户「{name}」已存在，无需重复添加'}), 400

    customer = Customer(
        user_id=user_id,
        name=name,
        phone=phone or None,
        tag=tag or None,
        notes=notes or None,
    )
    db.session.add(customer)
    db.session.commit()

    return jsonify(customer.to_dict()), 201


@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """修改客户信息"""
    user_id = get_jwt_identity()
    customer = Customer.query.filter_by(id=customer_id, user_id=user_id).first()
    if not customer:
        return jsonify({'error': '客户不存在'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供修改内容'}), 400

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': '客户称呼不能为空'}), 400

    customer.name = name
    customer.phone = (data.get('phone') or '').strip() or None
    customer.tag = (data.get('tag') or '').strip() or None
    customer.notes = (data.get('notes') or '').strip() or None
    db.session.commit()

    return jsonify(customer.to_dict())


@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """删除客户"""
    user_id = get_jwt_identity()
    customer = Customer.query.filter_by(id=customer_id, user_id=user_id).first()
    if not customer:
        return jsonify({'error': '客户不存在'}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({'message': '客户已删除'})
