from flask import session
from datetime import timedelta
from scripts.config import Config

def init_session(app):
    config = Config()
    app.secret_key = config.SECRET_KEY
    app.permanent_session_lifetime = timedelta(days=7)  # 一周免登录

def login_user(student_id):
    session.permanent = True
    session['student_id'] = student_id

def logout_user():
    session.pop('student_id', None)

def current_user():
    return session.get('student_id')
