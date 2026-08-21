from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from services.tax_service import build_tax_calendar

tax_bp = Blueprint('tax', __name__)


@tax_bp.route('/calendar', methods=['GET'])
@jwt_required()
def tax_calendar():
    """报税日历：按真实申报时间表计算最近的申报安排与倒计时天数。

    返回结构：
      - today: 今天日期
      - items: [{key, label, scope, deadline, days_left, status, note}, ...]
        status: normal(正常) / soon(7天内) / urgent(3天内) / overdue(已逾期) / open(办理期内)
      - tips / disclaimer / pending_verification
    """
    return jsonify(build_tax_calendar())
