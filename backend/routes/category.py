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

    # 权限校验：必须是系统默认或当前用户的分类（JWT身份是字符串，统一按字符串比较）
    if category.user_id is not None and str(category.user_id) != str(user_id):
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

    # 只能删除自己的自定义分类（JWT身份是字符串，统一按字符串比较）
    if str(category.user_id) != str(user_id):
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
