from extensions import db
from datetime import datetime


class Customer(db.Model):
    """客户台账

    面向餐饮小店：记录老客户/赊账客户/团购客户的联系方式与备注，
    方便老板一键查到"这个人是谁、怎么联系、有什么约定"。
    """
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)          # 称呼/姓名
    phone = db.Column(db.String(20))                         # 电话
    tag = db.Column(db.String(50))                           # 标签：老客户/月结/团购/赊账等
    notes = db.Column(db.Text)                               # 备注：口味、欠款、约定等
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_customer_user', 'user_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone or '',
            'tag': self.tag or '',
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Customer {self.id} user={self.user_id} {self.name}>'
