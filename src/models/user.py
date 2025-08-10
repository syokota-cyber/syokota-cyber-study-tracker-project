"""
ユーザーモデル
認証システムで使用するユーザー関連のPydanticモデルを定義
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """ユーザーロールの定義"""
    USER = "user"
    ADMIN = "admin"

class UserBase(BaseModel):
    """ユーザーの基本情報"""
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    is_active: bool = True
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    """ユーザー作成時のモデル"""
    email: str = Field(..., regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="メールアドレス")
    password: str = Field(..., min_length=8, max_length=100, description="パスワード")

class UserLogin(BaseModel):
    """ユーザーログイン時のモデル"""
    email: str = Field(..., regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="メールアドレス")
    password: str = Field(..., description="パスワード")

class UserUpdate(BaseModel):
    """ユーザー更新時のモデル"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="ユーザー名")
    email: Optional[str] = Field(None, regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="メールアドレス")
    is_active: Optional[bool] = None

class User(UserBase):
    """ユーザー情報の完全なモデル（データベース用）"""
    id: str
    email: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """ユーザー情報のレスポンスモデル（パスワードを除外）"""
    id: str
    email: str
    username: str
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWTトークンのレスポンスモデル"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """トークンに含まれるデータ"""
    user_id: Optional[str] = None

