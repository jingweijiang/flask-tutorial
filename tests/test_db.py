import sqlite3

import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    
    # 初始化数据库连接
    with app.app_context():
        db = get_db()
        assert db is get_db()
        
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    
    assert 'closed' in str(e.value)
    
    
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        """用于记录 fake_init_db 函数是否被调用"""
        called = False

    def fake_init_db():
        """init_db 函数，它只是将 Recorder.called 设置为 True数"""
        Recorder.called = True
    # 覆盖默认的init_db函数,将原本的 flaskr.db.init_db 函数替换为我们的 fake_init_db 函数
    # flaskr包下的db模块中定义了init_db函数，它只是初始化数据库
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    
    # 模拟命令行操作
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called