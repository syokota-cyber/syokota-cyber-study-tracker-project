"""
JWT認証機能のテスト
トークン生成、検証、パスワードハッシュ化のテスト
"""

import pytest
from datetime import timedelta
from src.auth.jwt_handler import (
    create_access_token,
    verify_token,
    verify_password,
    get_password_hash
)

class TestJWTHandler:
    """JWTハンドラーのテストクラス"""
    
    def test_create_access_token(self):
        """アクセストークンの生成テスト"""
        data = {"sub": "test_user_id"}
        token = create_access_token(data)
        
        # トークンが生成されることを確認
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """有効なトークンの検証テスト"""
        data = {"sub": "test_user_id"}
        token = create_access_token(data)
        payload = verify_token(token)
        
        # トークンが正しく検証されることを確認
        assert payload is not None
        assert payload["sub"] == "test_user_id"

    def test_verify_token_invalid(self):
        """無効なトークンの検証テスト"""
        payload = verify_token("invalid_token")
        
        # 無効なトークンはNoneを返すことを確認
        assert payload is None

    def test_verify_token_empty(self):
        """空のトークンの検証テスト"""
        payload = verify_token("")
        
        # 空のトークンはNoneを返すことを確認
        assert payload is None

    def test_password_hash_and_verify(self):
        """パスワードハッシュ化と検証テスト"""
        password = "test_password"
        hashed = get_password_hash(password)
        
        # ハッシュ化されたパスワードが元のパスワードと異なることを確認
        assert hashed != password
        
        # 正しいパスワードの検証
        assert verify_password(password, hashed) is True
        
        # 間違ったパスワードの検証
        assert verify_password("wrong_password", hashed) is False

    def test_password_hash_consistency(self):
        """パスワードハッシュの一貫性テスト"""
        password = "test_password"
        hashed1 = get_password_hash(password)
        hashed2 = get_password_hash(password)
        
        # 同じパスワードでもハッシュは異なる（ソルトが異なるため）
        assert hashed1 != hashed2
        
        # どちらも正しく検証される
        assert verify_password(password, hashed1) is True
        assert verify_password(password, hashed2) is True

    def test_token_expiration(self):
        """トークンの有効期限テスト"""
        data = {"sub": "test_user_id"}
        # 1分後に期限切れになるトークンを作成
        token = create_access_token(data, expires_delta=timedelta(minutes=1))
        payload = verify_token(token)
        
        # トークンが有効期限内であることを確認
        assert payload is not None
        assert payload["sub"] == "test_user_id"

    def test_token_with_custom_data(self):
        """カスタムデータを含むトークンのテスト"""
        data = {
            "sub": "test_user_id",
            "username": "testuser",
            "role": "user"
        }
        token = create_access_token(data)
        payload = verify_token(token)
        
        # カスタムデータが正しく含まれていることを確認
        assert payload is not None
        assert payload["sub"] == "test_user_id"
        assert payload["username"] == "testuser"
        assert payload["role"] == "user"

    def test_password_complexity(self):
        """複雑なパスワードのテスト"""
        complex_password = "MySecurePassword123!@#"
        hashed = get_password_hash(complex_password)
        
        # 複雑なパスワードも正しくハッシュ化・検証されることを確認
        assert hashed != complex_password
        assert verify_password(complex_password, hashed) is True
        assert verify_password("wrong_complex_password", hashed) is False

