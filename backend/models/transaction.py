from extensions import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(10))  # 'income' 或 'expense'
    category = db.Column(db.String(50))
    supplier = db.Column(db.String(100))
    customer_name = db.Column(db.String(50))  # 关联的客户（客户台账里的称呼），可空
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending/confirmed/modified
    source_image_url = db.Column(db.String(500), nullable=True)
    voucher_urls = db.Column(db.Text, nullable=True)  # 凭证图片文件名，逗号分隔
    ai_confidence = db.Column(db.String(10))  # high/medium/low
    ai_match_status = db.Column(db.String(20))  # matched/needs_check
    confirmed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    modification_logs = db.relationship('ModificationLog', backref='transaction', lazy='dynamic')

    # 索引
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'transaction_date'),
        db.Index('idx_user_category', 'user_id', 'category'),
        db.Index('idx_user_supplier', 'user_id', 'supplier'),
    )

    def __repr__(self):
        return f'<Transaction {self.id} user={self.user_id} {self.type} {self.amount}>'


class ModificationLog(db.Model):
    __tablename__ = 'modification_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    field_name = db.Column(db.String(50))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ModificationLog {self.transaction_id} {self.field_name}>'
