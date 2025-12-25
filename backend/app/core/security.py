from jose import jwt
from passlib.context import CryptContext
from .config import JWT_SECRET, JWT_ALGO

pwd = CryptContext(schemes=["bcrypt"])

def hash_password(p): return pwd.hash(p)
def verify_password(p, h): return pwd.verify(p, h)

def create_token(data: dict):
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGO)
