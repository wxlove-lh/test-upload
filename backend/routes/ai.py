import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.comparison import ComparisonService
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
