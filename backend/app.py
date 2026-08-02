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
