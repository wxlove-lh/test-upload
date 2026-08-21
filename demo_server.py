"""
AI虚拟文员 - 一键演示服务器
同时提供：前端页面( dist 静态文件 ) + 后端 API
启动后浏览器打开 http://localhost:5000 即可使用
"""
import os
import sys

# 保证能 import 到 backend 里的模块
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE_DIR, 'backend'))

from flask import send_from_directory
from app import create_app
from extensions import db
from models.user import User

app = create_app('development')

# 演示账号自动升级为专业版（每次启动都生效，保证能看到全部功能）
# 若演示账号还不存在则跳过（首次请先运行 docbuild/seed_demo.py 造数据）
DEMO_PHONE = '13812345678'
with app.app_context():
    demo_user = User.query.filter_by(phone=DEMO_PHONE).first()
    if demo_user:
        changed = False
        if demo_user.subscription_plan != 'pro':
            demo_user.subscription_plan = 'pro'
            changed = True
        if demo_user.free_uses_remaining is None or demo_user.free_uses_remaining < 99:
            demo_user.free_uses_remaining = 999
            changed = True
        if changed:
            db.session.commit()
            print(f'[演示账号] {DEMO_PHONE} 已升级为专业版，免费次数 999')
        else:
            print(f'[演示账号] {DEMO_PHONE} 已是专业版')
    else:
        print(f'[提示] 未找到演示账号 {DEMO_PHONE}，请先运行 docbuild/seed_demo.py 创建演示数据')

# 前端构建产物目录
DIST_DIR = os.path.join(_BASE_DIR, 'frontend', 'dist')


@app.route('/')
def index():
    return send_from_directory(DIST_DIR, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """静态文件 + SPA 路由回退（history 模式）"""
    full = os.path.join(DIST_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(DIST_DIR, path)
    # 不是文件就回退到 index.html，交给 vue-router 处理
    return send_from_directory(DIST_DIR, 'index.html')


if __name__ == '__main__':
    print('=' * 50)
    print('  AI虚拟文员 演示服务器已启动')
    print('  请在浏览器打开:  http://localhost:5000')
    print('  演示账号:  13812345678 / 123456')
    print('  (关闭本窗口即停止服务)')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
