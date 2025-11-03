import smtplib
from email.mime.text import MIMEText
from email.header import Header
import random
import logging

def generate_code():
    return f"{random.randint(0, 999999):06d}"

def send_verification_email(to_email, smtp_config):
    code = generate_code()
    subject = "WordsProject 注册验证码"
    body = f"您的验证码是：{code}，请在 5 分钟内完成验证。"

    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(smtp_config['sender_name'], 'utf-8')
    message['To'] = Header(to_email, 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')

    try:
        server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
        server.login(smtp_config['username'], smtp_config['password'])
        server.sendmail(smtp_config['sender_email'], [to_email], message.as_string())
        server.quit()
        logging.info(f"验证码已发送至邮箱: {to_email}，验证码为: {code}")
        return code
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
        return None
