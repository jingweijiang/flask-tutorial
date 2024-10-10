import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # 未输入用户名或密码
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        
        if error is None:
            try:
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?,?)',
                    (username, generate_password_hash(password,  method='pbkdf2:sha256'))
                )
                db.commit()
            except db.IntegrityError:
                # 用户已注册
                error = f"User {username} is already registered."
            else:
                # 跳转登录页面
                return redirect(url_for('auth.login'))

        # 显示错误信息
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()    
        error = None
        
        # 查询用户是否存在
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # 登录成功，设置 session
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))

        # 显示错误信息
        flash(error)

    return render_template('auth/login.html')

# 注册一个在视图函数之前运行的函数
@bp.before_app_request
def load_logged_in_user():
    """检查用户是否已登录，并从数据库中加载用户信息。"""

    user_id = session.get('user_id')

    # 如果用户未登录，则 g.user 为 None
    if user_id is None:
        g.user = None
    else:
        # 
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.index'))


def login_required(view):
    """视图函数装饰器，要求用户已登录才能访问。"""
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view