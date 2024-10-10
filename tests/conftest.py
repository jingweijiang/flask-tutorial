import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')
    
    
@pytest.fixture
def app():
    # 创建并打开一个临时文件，返回文件描述符及其路径
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,    # TESTING告诉 Flask 应用处于测试模式
        'DATABASE': db_path,
    })

    # 运行测试前，先初始化数据库
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    # 关闭并删除临时文件
    os.close(db_fd)
    os.unlink(db_path)
    
@pytest.fixture
def client(app):
    # 测试将使用客户端向应用程序发出请求，而无需运行服务器
    return app.test_client()

@pytest.fixture
def runner(app):
    # 创建一个可以调用在应用程序中注册的 Click 命令的运行器。
    return app.test_cli_runner()



class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):    
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """登录认证装置"""
    return AuthActions(client)
