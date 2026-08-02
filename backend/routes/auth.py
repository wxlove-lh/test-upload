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
