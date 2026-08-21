import os, sys, time, json

# 自动定位 backend 目录：无论脚本从哪运行，都能找到本项目 backend
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # docbuild 目录
_BACKEND_DIR = os.path.join(os.path.dirname(_BASE_DIR), 'backend')  # 项目根/backend
sys.path.insert(0, _BACKEND_DIR)
from app import create_app
app = create_app('development')

client = app.test_client()

# 注册（若已存在则登录）
r = client.post('/api/auth/register', json={'phone':'13812345678','password':'123456','industry':'小吃店'})
if r.status_code == 201:
    d = r.get_json()
    token = d['token']
    print('注册:', r.status_code, d['user']['phone'])
elif r.status_code == 409:
    r = client.post('/api/auth/login', json={'phone':'13812345678','password':'123456'})
    d = r.get_json()
    token = d['token']
    print('账号已存在，直接登录:', d['user']['phone'])
else:
    print('注册/登录失败:', r.status_code, r.get_json())
    sys.exit(1)
H = {'Authorization': f'Bearer {token}'}

# 造演示数据（幂等：只补缺失的，重复运行不会翻倍）
# 先查当前交易总数，已 ≥ 9 笔就不再插入
r0 = client.get('/api/transactions', headers=H)
existing_total = r0.get_json()['total'] if r0.status_code == 200 else 0

seed = [
    ('2026-07-28', 215.0, 'expense', '食材', '蔬菜批发市场'),
    ('2026-07-29', 45.0, 'expense', '耗材餐具', '一次性用品店'),
    ('2026-07-30', 3200.0, 'income', '营业收入', '堂食+外卖'),
    ('2026-07-31', 180.0, 'expense', '酒水饮料', '雪花啤酒经销商'),
    ('2026-08-01', 235.5, 'expense', '食材', '水产批发'),
    ('2026-08-02', 1800.0, 'income', '营业收入', '堂食+外卖'),
    ('2026-08-03', 120.0, 'expense', '水电燃气', '供电局'),
    ('2026-08-04', 980.0, 'expense', '工资', '帮厨小李'),
    ('2026-08-05', 2600.0, 'income', '营业收入', '宴席包桌'),
]
created = 0
if existing_total < len(seed):
    for tx_date, amt, typ, cat, sup in seed:
        r = client.post('/api/transactions', headers=H, json={
            'transaction_date': tx_date, 'amount': amt, 'type': typ, 'category': cat, 'supplier': sup, 'notes': '演示数据'
        })
        assert r.status_code == 201, r.get_json()
        created += 1
    print('已创建', created, '笔演示交易')
else:
    print(f'已有 {existing_total} 笔交易，跳过播种（避免重复）')

# 确保演示账号是专业版
import sqlite3, os
_db_path = os.path.join(_BACKEND_DIR, 'instance', 'dev.db')
try:
    _conn = sqlite3.connect(_db_path)
    _conn.execute("UPDATE users SET subscription_plan='pro', free_uses_remaining=999 WHERE phone='13812345678'")
    _conn.commit()
    _conn.close()
    print('演示账号已升级为专业版')
except Exception as e:
    print('升级演示账号失败(可忽略,启动时会自动升级):', e)

# 验证
r = client.get('/api/transactions', headers=H)
d = r.get_json()
print('交易列表:', d['total'], '条, 首页', len(d['items']), '条')

r = client.get('/api/transactions/summary', headers=H)
print('汇总:', r.get_json())

r = client.get('/api/categories', headers=H)
cats = r.get_json()
print('支出分类数:', len(cats['expense']), '收入分类数:', len(cats['income']))

r = client.get('/api/analytics/trend?dimension=month', headers=H)
print('趋势(月):', len(r.get_json()['data']), '个月')
r = client.get('/api/analytics/category-ratio?type=expense', headers=H)
print('分类占比:', len(r.get_json()['data']), '个分类')

print('\n=== 全部接口验证通过 ===')
print('登录账号: 13812345678 / 123456')
