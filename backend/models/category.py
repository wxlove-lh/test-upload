from extensions import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # NULL表示系统默认
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10))  # 'income' 或 'expense'
    is_default = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'


def init_default_categories():
    """创建12个默认分类（幂等操作：仅在不存在时插入）"""
    defaults = [
        # 支出(10个)
        {'name': '食材', 'type': 'expense', 'sort_order': 1},
        {'name': '酒水饮料', 'type': 'expense', 'sort_order': 2},
        {'name': '房租', 'type': 'expense', 'sort_order': 3},
        {'name': '工资', 'type': 'expense', 'sort_order': 4},
        {'name': '水电燃气', 'type': 'expense', 'sort_order': 5},
        {'name': '耗材餐具', 'type': 'expense', 'sort_order': 6},
        {'name': '设备维修', 'type': 'expense', 'sort_order': 7},
        {'name': '运输配送', 'type': 'expense', 'sort_order': 8},
        {'name': '税费管理', 'type': 'expense', 'sort_order': 9},
        {'name': '其他支出', 'type': 'expense', 'sort_order': 10},
        # 收入(2个)
        {'name': '营业收入', 'type': 'income', 'sort_order': 1},
        {'name': '其他收入', 'type': 'income', 'sort_order': 2},
    ]

    for item in defaults:
        existing = Category.query.filter_by(
            name=item['name'],
            type=item['type'],
            user_id=None
        ).first()
        if not existing:
            category = Category(
                user_id=None,
                name=item['name'],
                type=item['type'],
                is_default=True,
                sort_order=item['sort_order']
            )
            db.session.add(category)

    db.session.commit()
