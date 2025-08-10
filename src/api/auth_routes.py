"""
認証APIルート
ユーザー登録・ログイン・認証関連のエンドポイントを定義
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from ..models.user import UserCreate, UserUpdate, UserResponse, Token
from ..services.user_service import UserService
from ..auth.jwt_handler import create_access_token
from ..auth.dependencies import get_current_user
import os

router = APIRouter(prefix="/auth", tags=["認証"])

# ユーザーサービスの初期化（ローカル環境用）
def get_user_service() -> UserService:
    """ユーザーサービスのインスタンスを取得"""
    # ローカル環境の場合はローカルDynamoDBを使用
    endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL", None)
    return UserService(endpoint_url=endpoint_url)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    ユーザー登録
    
    Args:
        user_data: ユーザー登録データ
        
    Returns:
        作成されたユーザー情報
        
    Raises:
        HTTPException: バリデーションエラーまたは重複エラー
    """
    try:
        user = user_service.create_user(user_data)
        return UserResponse.from_user(user)
    except ValueError as e:
        if "Email already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """
    ユーザーログイン
    
    Args:
        form_data: ログインフォームデータ（email, password）
        
    Returns:
        JWTアクセストークン
        
    Raises:
        HTTPException: 認証失敗
    """
    # ユーザー認証
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # アクセストークンの生成
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    現在のユーザー情報を取得
    
    Args:
        current_user: 現在のユーザー情報（JWTトークンから取得）
        user_service: ユーザーサービス
        
    Returns:
        現在のユーザー情報
        
    Raises:
        HTTPException: ユーザーが見つからない場合
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_user(user)

@router.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    現在のユーザー情報を更新
    
    Args:
        user_data: 更新データ
        current_user: 現在のユーザー情報
        user_service: ユーザーサービス
        
    Returns:
        更新されたユーザー情報
        
    Raises:
        HTTPException: 更新失敗
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        updated_user = user_service.update_user(user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_user(updated_user)
    except ValueError as e:
        if "Email already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    現在のユーザーを削除
    
    Args:
        current_user: 現在のユーザー情報
        user_service: ユーザーサービス
        
    Raises:
        HTTPException: 削除失敗
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get("/users", response_model=Dict[str, Any])
async def list_users(
    limit: int = 10,
    last_key: str = None,
    user_service: UserService = Depends(get_user_service)
):
    """
    ユーザー一覧を取得（管理者用）
    
    Args:
        limit: 取得件数
        last_key: ページネーション用のキー
        user_service: ユーザーサービス
        
    Returns:
        ユーザー一覧とページネーション情報
    """
    result = user_service.list_users(limit=limit, last_key=last_key)
    
    # UserResponseオブジェクトに変換
    users = [UserResponse.from_user(user) for user in result['users']]
    
    return {
        'users': users,
        'count': result['count'],
        'last_evaluated_key': result['last_evaluated_key'],
        'scanned_count': result['scanned_count']
    }

