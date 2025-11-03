from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os

# 
FERNET_KEY = os.environ.get("FERNET_SECRET_KEY") or Fernet.generate_key()
cipher = Fernet(FERNET_KEY)

def encrypt_email(email: str) -> str:
    """加密邮箱"""
    return cipher.encrypt(email.encode()).decode()

def decrypt_email(token: str) -> str:
    """解密邮箱"""
    return cipher.decrypt(token.encode()).decode()

def encrypt_phone(phone: str) -> str:
    """加密手机号"""
    return cipher.encrypt(phone.encode()).decode()

def decrypt_phone(token: str) -> str:
    """解密手机号"""
    return cipher.decrypt(token.encode()).decode()

def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(hash_value: str, password: str) -> bool:
    return check_password_hash(hash_value, password)

# 加密wakatime api key
def encrypt_wakatime_api_key(api_key: str) -> str:
    return cipher.encrypt(api_key.encode()).decode()

# 解密wakatime api key
def decrypt_wakatime_api_key(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()
