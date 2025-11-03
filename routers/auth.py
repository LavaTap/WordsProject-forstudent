import random
from datetime import datetime, timedelta

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash,session
)
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import Student
from session import login_user, logout_user, current_user
from utils.email_utils import send_verification_email
from scripts.email_config import SMTP_CONFIG

auth_bp = Blueprint("auth", __name__, template_folder="templates")


def generate_code():
    """产生 6 位数字验证码"""
    return f"{random.randint(0, 999999):06d}"

def send_code_to_phone(phone, code):
    """模拟短信发送（或在这里接入阿里云短信 SDK）"""
    print("已发送短信验证码：", code)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    第一步：填写学号 / 手机号 / 密码 → 验证格式 & 唯一性 → 生成 & 存储短信验证码 → 跳转到校验页面
    """
    if request.method == "GET":
        return render_template("register.html")

    student_id = request.form.get("student_id", "").strip()
    sex   = request.form.get("sex", "").strip()
    phone      = request.form.get("phone", "").strip()
    password   = request.form.get("password", "")
    confirm    = request.form.get("confirm_password", "")
    school     = request.form.get("school", "").strip()
    email      = request.form.get("email", "").strip()

    # 3. 生成验证码 & 存储未验证的学生记录
    code   = generate_code()
    expire = datetime.utcnow() + timedelta(minutes=5)
    send_code_to_phone(phone, code)
    
    # 开发调试用

    # 1. 格式校验
    if not (student_id.isdigit() and len(student_id) == 7 and 20 < int(student_id[:2]) < 26):
        flash("无效学号", "error")
        return redirect(url_for("auth.register"))

    if len(password) < 6 or password != confirm:
        flash("密码不一致或长度不足（至少6位）", "error")
        return redirect(url_for("auth.register"))

    # 2. 唯一性校验
    if Student.query.filter_by(student_id=student_id).first():
        flash("学号已存在", "error")
        return redirect(url_for("auth.register"))

    if Student.query.filter_by(phone=phone).first():
        flash("手机号已被绑定", "error")
        return redirect(url_for("auth.register"))

    if Student.query.filter_by(email=email).first():
        flash("邮箱已被绑定", "error")
        return redirect(url_for("auth.register"))
    
    if not email or "@" not in email:
        flash("请输入有效邮箱地址", "error")
        return redirect(url_for("auth.register"))
    

    student = Student(
        sex=sex,
        school=school,
        student_id=student_id,
        phone=phone,
        password_hash=generate_password_hash(password),
        phone_code=code,
        phone_code_expire=expire,
        phone_verified=False
    )
    student.email = email
    student.phone = phone

    db.session.add(student)
    db.session.commit()

    
    return redirect(url_for("auth.confirm_register"))


@auth_bp.route("/confirm_register", methods=["GET", "POST"])
def confirm_register():
    """
    第二步：输入手机号 + 短信验证码 → 完成手机号验证 → 自动登录
    """
    if request.method == "GET":
        return render_template("confirm_register.html")

    phone = request.form.get("phone", "").strip()
    code  = request.form.get("code", "").strip()

    student = Student.query.filter_by(phone=phone).first()
    if not student:
        flash("手机号未注册", "error")
        return redirect(url_for("auth.confirm_register"))

    # 校验验证码与过期时间
    if student.phone_code != code or datetime.utcnow() > student.phone_code_expire:
        flash("验证码错误或已过期", "error")
        return redirect(url_for("auth.confirm_register"))

    # 标记验证完成 & 清理临时字段
    student.phone_verified      = True
    student.phone_code          = None
    student.phone_code_expire   = None
    db.session.commit()

    login_user(student.student_id)
    flash("注册并验证成功，已自动登录", "success")
    return redirect(url_for("mode_select"))


@auth_bp.route("/send_email_code", methods=["POST"])
def send_email_code():
    """
    邮箱验证码发送（POST /send_email_code）
    """
    email = request.form.get("email", "").strip()
    if not email:
        flash("请输入邮箱", "error")
        return redirect(url_for("auth.login"))

    code = send_verification_email(email, SMTP_CONFIG)
    if code:
        expire = datetime.utcnow() + timedelta(minutes=5)
        student = Student.query.filter_by(email=email).first()

        if not student:
            student = Student(email=email)
            db.session.add(student)

        student.email_code         = code
        student.email_code_expiry  = expire
        db.session.commit()
        flash("验证码已发送至您的邮箱", "info")
    else:
        flash("邮箱验证码发送失败，请稍后重试", "error")

    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    登录逻辑：学号 + 密码
    """
    if request.method == "GET":
        if current_user():
            return redirect(url_for("mode_select"))
        return render_template("login.html")

    student_id = request.form.get("student_id", "").strip()
    password   = request.form.get("password", "")

    student = Student.query.filter_by(student_id=student_id).first()
    if student and check_password_hash(student.password_hash, password):
        login_user(student.student_id)
        return redirect(url_for("mode_select"))
    flash("学号或密码错误", "error")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # 1. 登录验证
    student_id = session.get("student_id", "").strip()
    if not student_id:
        flash('请先登录后再修改密码。', 'error')
        return redirect(url_for('auth.login'))

    # 2. 获取当前用户
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        flash('用户不存在，请重新登录。', 'error')
        return redirect(url_for('auth.login'))

    # 3. 处理 POST 请求
    if request.method == 'POST':
        current_pw = request.form.get('current_password') 
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')

        # 验证当前密码
        if not check_password_hash(student.password_hash, current_pw):
            flash('当前密码错误。', 'error')
            return redirect(url_for('auth.change_password'))

        # 验证两次输入的新密码一致性
        if new_pw != confirm_pw:
            flash('两次输入的新密码不一致。', 'error')
            return redirect(url_for('auth.change_password'))

        # 更新密码
        student.set_password(new_pw)
        db.session.commit()

        flash('密码修改成功，请使用新密码重新登录。', 'success')
        session.pop('student_id', None)
        return redirect(url_for('auth.login'))

    # 4. GET 请求，渲染表单
    return render_template('change_password.html')