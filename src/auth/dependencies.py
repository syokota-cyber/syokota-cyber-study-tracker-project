"""
認証依存関係
FastAPIで認証が必要なエンドポイントで使用する依存関係を定義
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
from .jwt_handler import verify_token

# OAuth2PasswordBearerの設定
# tokenUrlは認証エンドポイントのパスを指定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    現在のユーザーを取得（認証が必要なエンドポイントで使用）
    
    Args:
        token: JWTトークン（OAuth2PasswordBearerが自動的に取得）
    
    Returns:
        ユーザー情報（現在は簡易実装のためユーザーIDのみ）
    
    Raises:
        HTTPException: 認証に失敗した場合
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # トークンの検証
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    # ユーザーIDの取得
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # ここでユーザーIDからユーザー情報を取得
    # 現在は簡易実装のため、ユーザーIDのみ返す
    # 将来的にはデータベースからユーザー情報を取得
    return {"user_id": user_id}

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    現在のアクティブユーザーを取得
    
    Args:
        current_user: get_current_userから取得したユーザー情報
    
    Returns:
        アクティブなユーザー情報
    
    Raises:
        HTTPException: ユーザーが非アクティブな場合
    """
    # 将来的にはユーザーのアクティブ状態をチェック
    # 現在は簡易実装のため、常にアクティブとして扱う
    return current_user

