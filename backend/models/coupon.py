from extensions import db
from datetime import datetime


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2))
    source = db.Column(db.String(50), default='referral_reward')
    expiry_date = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='coupons')

    def __repr__(self):
        return f'<Coupon {self.id} user={self.user_id} amount={self.amount}>'
