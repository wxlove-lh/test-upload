from extensions import db
from datetime import datetime


class ReferralRecord(db.Model):
    __tablename__ = 'referral_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_amount = db.Column(db.Numeric(10, 2))
    reward_expiry = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='issued')  # issued/used/expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    inviter = db.relationship('User', foreign_keys=[inviter_id], backref='invited_records')
    invitee = db.relationship('User', foreign_keys=[invitee_id], backref='invited_by_records')

    def __repr__(self):
        return f'<ReferralRecord inviter={self.inviter_id} invitee={self.invitee_id}>'
