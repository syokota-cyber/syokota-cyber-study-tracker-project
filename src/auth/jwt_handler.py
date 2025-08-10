"""
JWT認証ハンドラー
トークンの生成、検証、パスワードのハッシュ化・検証機能を提供
"""

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import os

# ローカル開発用の秘密鍵（本番ではSecrets Manager使用）
SECRET_KEY = "your-secret-key-for-development-only-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# パスワードハッシュ化の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWTアクセストークンを生成
    
    Args:
        data: トークンに含めるデータ（通常はユーザーID）
        expires_delta: 有効期限（指定しない場合はデフォルト30分）
    
    Returns:
        生成されたJWTトークン
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    JWTトークンを検証
    
    Args:
        token: 検証するJWTトークン
    
    Returns:
        検証成功時はペイロード、失敗時はNone
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証
    
    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード
    
    Returns:
        パスワードが一致する場合はTrue、そうでなければFalse
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化
    
    Args:
        password: ハッシュ化するパスワード
    
    Returns:
        ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)
