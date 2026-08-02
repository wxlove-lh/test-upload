from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(50))  # 夜宵摊/夫妻餐馆/早餐店/快餐店/小吃店
    subscription_plan = db.Column(db.String(20), default='free')  # free/basic/advanced/clerk
    subscription_type = db.Column(db.String(20), nullable=True)  # daily/monthly/yearly
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    referral_code = db.Column(db.String(10), unique=True)  # 6位随机字母数字
    referred_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    free_uses_remaining = db.Column(db.Integer, default=5)
    is_founding_member = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    referrer = db.relationship('User', remote_side=[id], backref='referrals')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    categories = db.relationship('Category', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_referral_code():
        """生成6位随机字母数字码（大写）"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=6))

    def __repr__(self):
        return f'<User {self.phone}>'
