from enum import unique
import json

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from utils.security import encrypt_email, decrypt_email, hash_password, verify_password, encrypt_phone, decrypt_phone, generate_password_hash, verify_password, encrypt_wakatime_api_key, decrypt_wakatime_api_key

# 用户模型
class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    school = db.Column(db.String(64))
    sex = db.Column(db.String(10))

    phone_verified = db.Column(db.Boolean, default=False)
    phone_code = db.Column(db.String(6))  # 验证码（临时）
    phone_code_expire = db.Column(db.DateTime)  # 验证码过期时间

    # 加密后的手机号字段
    phone_encrypted = db.Column(db.String(128))
    
    # 加密后的邮箱字段
    email_encrypted = db.Column(db.String(128), unique=True, nullable=False)
    email_code = db.Column(db.String(6))
    email_code_expiry = db.Column(db.DateTime)

    # wakatime API密钥
    wakatime_api_key = db.Column(db.String(128))

    records = db.relationship(
        "QuizRecord", backref="student", lazy="dynamic", cascade="all, delete-orphan"
    )

    # 邮箱属性
    @property
    def email(self):
        return decrypt_email(self.email_encrypted)

    @email.setter
    def email(self, raw_email):
        self.email_encrypted = encrypt_email(raw_email)

    # 手机号属性
    @property
    def phone(self):
        return decrypt_phone(self.phone_encrypted)

    @phone.setter
    def phone(self, raw_phone):
        self.phone_encrypted = encrypt_phone(raw_phone)

    # 更改密码
    def set_password(self, raw_password):
        """更新密码"""
        self.password_hash = generate_password_hash(raw_password)

    @property
    def phone(self):
        return decrypt_phone(self.phone_encrypted)

    @phone.setter
    def phone(self, raw_phone):
        self.phone_encrypted = encrypt_phone(raw_phone)

    # # wakatime属性
    # @property
    # def WAKATIME_API_KEY(self):
    #     return decrypt_wakatime_api_key(self.wakatime_api_key)
    
    # @wakatime_api_key.setter
    # def WAKATIME_API_KEY(self, raw_api_key):
    #     self.wakatime_api_key = encrypt_wakatime_api_key(raw_api_key)

    

# 用户统计模型
class UserStats(db.Model):
    __tablename__ = "user_stats"
    id                = db.Column(db.Integer, primary_key=True)
    student_id        = db.Column(
        db.String(64),
        db.ForeignKey("students.student_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    total_words       = db.Column(db.Integer, default=0)
    accuracy          = db.Column(db.Float, default=0.0)

    # 全量历史（日度）缓存
    daily_labels      = db.Column(db.Text)  
    daily_counts      = db.Column(db.Text)  
    daily_accuracies  = db.Column(db.Text)  

    # 时间点分布缓存
    time_labels       = db.Column(db.Text, default="[]")
    time_values       = db.Column(db.Text, default="[]")  

    # 近7天统计
    weekly_labels     = db.Column(db.Text, default="[]")
    weekly_counts     = db.Column(db.Text, default="[]")
    weekly_accuracies = db.Column(db.Text, default="[]")

    # 近30天统计
    monthly_labels     = db.Column(db.Text, default="[]")
    monthly_counts     = db.Column(db.Text, default="[]")
    monthly_accuracies = db.Column(db.Text, default="[]")

    updated_at        = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# 答题记录模型
class QuizRecord(db.Model):
    __tablename__ = "quiz_records"
    id            = db.Column(db.Integer, primary_key=True)
    student_id    = db.Column(
        'username',
        db.String(64),
        db.ForeignKey("students.student_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    mode          = db.Column(db.String(32))
    score         = db.Column(db.Integer, nullable=False)
    total         = db.Column(db.Integer, nullable=False)
    correct_data  = db.Column(db.Text, nullable=False)
    wrong_data    = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# 四级词汇模型
class CET4Word(db.Model):
    __tablename__ = 'cet4_words'

    id          = db.Column(db.Integer, primary_key=True)
    word        = db.Column(db.String(128), nullable=False, unique=True)

# 六级词汇模型
class CET6Word(db.Model):
    __tablename__ = 'cet6_words'

    id          = db.Column(db.Integer, primary_key=True)
    word        = db.Column(db.String(128), nullable=False, unique=True)

# 自定义单词模型
class CustomWord(db.Model):
    __tablename__ = 'custom_words'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    word       = db.Column(db.String(128), nullable=False)
    

# 错误单词模型
class WrongWord(db.Model):
    __tablename__ = 'wrong_words'
    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(
        db.String(64),
        db.ForeignKey('students.student_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    word           = db.Column(db.String(128), nullable=False)
    correct_answer = db.Column(db.String(128), nullable=False)

#编程数据模型
class Summary(db.Model):
    __tablename__ = 'summaries'
    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(
        db.String(64),
        db.ForeignKey('students.student_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    date           = db.Column(db.Date, unique= True,nullable=False)
    total_seconds = db.Column(db.Integer, nullable=False)
    
    projects = db.relationship('ProjectDuration', backref='summary', cascade='all, delete-orphan')

# 项目时长模型
class ProjectDuration(db.Model):
    __tablename__ = 'project_durations'
    id = db.Column(db.Integer, primary_key=True)
    summary_id = db.Column(db.Integer, db.ForeignKey('summaries.id'), nullable=False)
    project_name = db.Column(db.String(128), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)
