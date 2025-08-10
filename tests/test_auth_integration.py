"""
認証API統合テスト
ユーザー登録・ログイン・認証フローの統合テスト
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.main import app
from src.services.user_service import UserService
from src.models.user import UserCreate, UserRole

# テストクライアント
client = TestClient(app)

# テスト用の環境変数設定
os.environ["DYNAMODB_ENDPOINT_URL"] = "http://localhost:8000"

class TestAuthIntegration:
    """認証統合テストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前処理"""
        # テスト用のユーザーデータ
        self.test_user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "user"
        }
    
    def test_user_registration_flow(self):
        """ユーザー登録フローのテスト"""
        # 1. ユーザー登録
        response = client.post("/api/v1/auth/register", json=self.test_user_data)
        
        assert response.status_code == 201
        user_data = response.json()
        
        # レスポンスの検証
        assert user_data["email"] == self.test_user_data["email"]
        assert user_data["username"] == self.test_user_data["username"]
        assert user_data["role"] == self.test_user_data["role"]
        assert user_data["is_active"] == True
        assert "id" in user_data
        assert "created_at" in user_data
        assert "updated_at" in user_data
        assert "hashed_password" not in user_data  # パスワードは含まれない
    
    def test_user_login_flow(self):
        """ユーザーログインフローのテスト"""
        # 1. ユーザー登録
        client.post("/api/v1/auth/register", json=self.test_user_data)
        
        # 2. ログイン
        login_data = {
            "username": self.test_user_data["email"],  # OAuth2PasswordRequestFormはusernameフィールドを使用
            "password": self.test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        token_data = response.json()
        
        # トークンの検証
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert len(token_data["access_token"]) > 0
    
    def test_protected_endpoints(self):
        """認証が必要なエンドポイントのテスト"""
        # 1. ユーザー登録・ログイン
        client.post("/api/v1/auth/register", json=self.test_user_data)
        
        login_data = {
            "username": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # 2. 認証ヘッダーなしでアクセス（失敗することを確認）
        response = client.get("/api/v1/auth/users/me")
        assert response.status_code == 401
        
        # 3. 認証ヘッダー付きでアクセス（成功することを確認）
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/users/me", headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == self.test_user_data["email"]
    
    def test_user_update_flow(self):
        """ユーザー情報更新フローのテスト"""
        # 1. ユーザー登録・ログイン
        client.post("/api/v1/auth/register", json=self.test_user_data)
        
        login_data = {
            "username": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. ユーザー情報更新
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com"
        }
        
        response = client.put("/api/v1/auth/users/me", json=update_data, headers=headers)
        
        assert response.status_code == 200
        updated_user = response.json()
        
        assert updated_user["username"] == update_data["username"]
        assert updated_user["email"] == update_data["email"]
    
    def test_duplicate_email_registration(self):
        """重複メールアドレスでの登録テスト"""
        # 1. 最初のユーザー登録
        client.post("/api/v1/auth/register", json=self.test_user_data)
        
        # 2. 同じメールアドレスで再度登録（失敗することを確認）
        duplicate_user_data = self.test_user_data.copy()
        duplicate_user_data["username"] = "differentuser"
        
        response = client.post("/api/v1/auth/register", json=duplicate_user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_invalid_login_credentials(self):
        """無効なログイン認証情報のテスト"""
        # 1. ユーザー登録
        client.post("/api/v1/auth/register", json=self.test_user_data)
        
        # 2. 間違ったパスワードでログイン（失敗することを確認）
        invalid_login_data = {
            "username": self.test_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=invalid_login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_user_deletion_flow(self):
        """ユーザー削除フローのテスト"""
        # 1. ユーザー登録・ログイン
        client.post("/api/v1/auth/register", json=self.test_user_data)
        
        login_data = {
            "username": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. ユーザー削除
        response = client.delete("/api/v1/auth/users/me", headers=headers)
        
        assert response.status_code == 204
        
        # 3. 削除後にユーザー情報にアクセス（失敗することを確認）
        response = client.get("/api/v1/auth/users/me", headers=headers)
        assert response.status_code == 404
    
    def test_invalid_token_access(self):
        """無効なトークンでのアクセステスト"""
        # 無効なトークンでアクセス
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/users/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_user_list_endpoint(self):
        """ユーザー一覧エンドポイントのテスト"""
        # 1. 複数のユーザーを登録
        users_data = [
            {"email": "user1@example.com", "username": "user1", "password": "password123", "role": "user"},
            {"email": "user2@example.com", "username": "user2", "password": "password123", "role": "user"},
            {"email": "user3@example.com", "username": "user3", "password": "password123", "role": "user"}
        ]
        
        for user_data in users_data:
            client.post("/api/v1/auth/register", json=user_data)
        
        # 2. ユーザー一覧を取得
        response = client.get("/api/v1/auth/users")
        
        assert response.status_code == 200
        users_data = response.json()
        
        assert "users" in users_data
        assert "count" in users_data
        assert len(users_data["users"]) >= 3  # 最低3人のユーザーがいることを確認

if __name__ == "__main__":
    pytest.main([__file__])

