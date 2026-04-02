# tests/conftest.py
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from flask import Flask
from info import db
from info.models import User, News, Comment, Category  # 确保导入所有模型

@pytest.fixture(scope='session')
def app():
    """创建测试用的 Flask 应用（无蓝图，仅数据库）"""
    app = Flask(__name__)
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TESTING': True,
    })
    db.init_app(app)
    return app

@pytest.fixture(scope='session')
def _db(app):
    """创建所有表"""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def session(_db, request):
    """每个测试独立的事务，测试后回滚"""
    _db.session.begin_nested()
    yield _db.session
    _db.session.rollback()

@pytest.fixture
def db_session(session):
    return session

@pytest.fixture(scope='function')
def test_user(session):
    """创建测试用户，不提交"""
    user = User(
        nick_name='testuser',
        mobile='13800138000',
        signature='I am a tester'
    )
    user.password = '123456'
    session.add(user)
    session.flush()
    return user